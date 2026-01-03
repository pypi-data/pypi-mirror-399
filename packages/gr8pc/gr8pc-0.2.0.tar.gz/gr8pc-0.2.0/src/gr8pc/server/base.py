import logging
from asyncio import AbstractEventLoop, get_event_loop
from pathlib import Path
from types import ModuleType
from typing import Awaitable, Callable, ParamSpec, Type

from grpc.aio import server
from grpc.aio._server import Server  # noqa: _server

from ..interceptor import ServerInterceptor
from ..middleware import BaseMiddleware
from ..service import BaseService

ServerParam: ParamSpec = ParamSpec('ServerParam')
LifespanFunc = Callable[[ServerParam], Awaitable[None]]

logger = logging.getLogger(__name__)


class GrpcServer:
    def __init__(
        self: 'GrpcServer',
        port: int = 50051,
        host: str = '[::]',
        proto_dir: Path = Path('proto'),
        middlewares: set[Type[BaseMiddleware]] | None = None,
        on_startup: LifespanFunc | None = None,
        on_shutdown: LifespanFunc | None = None,
        name: str | None = None,
        *,
        services: tuple[Type[BaseService], ...] = (),
        access_log: bool = False,
        reflection: bool = False,
    ):
        self.port: int = port
        self.host: str = host
        self.proto_dir: Path = proto_dir
        self.loop: AbstractEventLoop = get_event_loop()
        self.server: Server = server(interceptors=[ServerInterceptor(access_log=access_log)])
        self.server._loop = self.loop
        self.services: dict[str, Type[BaseService]] = {}
        self.__protos: dict[str, ModuleType] = {}
        self.__services: dict[str, ModuleType] = {}
        self.middlewares: set[Type[BaseMiddleware]] = middlewares or set()
        self.on_startup: LifespanFunc | None = on_startup
        self.on_shutdown: LifespanFunc | None = on_shutdown
        self.name = name or self.__class__.__name__
        self.reflection: bool = reflection

        for service in services:
            self.add_service(service=service)

        if self.reflection:
            from ..reflection import apply_reflection

            apply_reflection(server=self.server, services=self.services)

    def add_service(self: 'GrpcServer', service: Type[BaseService]) -> None:
        self.services[service.name] = service
        service.set_middlewares(middlewares=self.middlewares)
        service.init_protos_and_services(proto_dir=self.proto_dir)
        self.__protos[service.name], self.__services[service.name] = (
            service.protos,
            service.services,
        )
        getattr(service.services, f'add_{service.name}Servicer_to_server')(
            servicer=service, server=self.server
        )

        logger.debug(f'{service.name} service added to {self.name} server')

    async def start_server(self: 'GrpcServer') -> None:
        await self.server.start()
        logger.info(f'{self.name} is up and listening on {self.host}:{self.port}')
        await self.server.wait_for_termination()

    def run(self: 'GrpcServer') -> None:
        self.server.add_insecure_port(address=f'{self.host}:{self.port}')
        try:
            logger.debug(f'Starting {self.name} server...')
            if self.on_startup:
                self.loop.run_until_complete(future=self.on_startup(server=self))
            self.loop.run_until_complete(future=self.start_server())
        except KeyboardInterrupt:
            ...
        finally:
            if self.on_shutdown:
                self.loop.run_until_complete(future=self.on_shutdown(server=self))
            logger.info(f'Stopping {self.name} server')
            self.loop.stop()
            logger.info(f'{self.name} server stopped')
