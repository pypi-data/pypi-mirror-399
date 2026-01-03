import asyncio
import inspect
import logging
import re
from typing import AsyncGenerator, Callable

from google.protobuf.message import Message
from grpc import StatusCode
from grpc.aio import ServicerContext
from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor.server import AsyncServerInterceptor
from pydantic import ValidationError

from .exceptions import RunTimeServerError, SendEmpty
from .method import ServerMethodGRPC

logger = logging.getLogger(__name__)


class ServerInterceptor(AsyncServerInterceptor):
    def __init__(self: 'ServerInterceptor', access_log: bool = False) -> None:
        self.access_log = access_log

    async def intercept(
        self: 'ServerInterceptor',
        route: ServerMethodGRPC | Callable,
        message: Message,
        context: ServicerContext,
        method_name: str,
    ) -> Message | None:
        response: Message | None = None

        try:
            if asyncio.iscoroutinefunction(route):
                response = await route(message, context)
            else:
                response = route(message, context)

            if self.access_log and inspect.isasyncgen(response):
                return stream_with_logging(response, context, route, method_name)
            else:
                return response
        except GrpcException as grpc_exc:
            context.set_code(grpc_exc.status_code)
            context.set_details(grpc_exc.details)
        except SendEmpty as exc:
            context.set_code(StatusCode.ABORTED)
            context.set_details(exc.text)
        except RunTimeServerError as exc:
            logger.error(exc)
            context.set_code(exc.status_code)
            context.set_details(
                'Internal Server Error' if exc.status_code == StatusCode.INTERNAL else exc.details
            )
        except ValidationError as exc:
            context.set_code(StatusCode.INVALID_ARGUMENT)
            context.set_details(exc.json())
        except Exception as exc:
            logger.exception(exc)
            context.set_code(StatusCode.INTERNAL)
            context.set_details('Internal Server Error')
        finally:
            if self.access_log and not inspect.isasyncgen(response):
                # log non-streaming responses in a separate asyncio task
                asyncio.create_task(
                    log_response(
                        context=context,
                        route=route,
                        method_name=method_name,
                        response=response or None,
                    )
                )


async def stream_with_logging(
    generator: AsyncGenerator[Message, None],
    context: ServicerContext,
    route: ServerMethodGRPC,
    method_name: str,
) -> AsyncGenerator[Message, None]:
    """wrap an async generator to log each yielded message"""
    message_count = 0
    async for message in generator:
        message_count += 1
        asyncio.create_task(
            log_response(context, route, method_name, message, streaming_count=message_count)
        )
        yield message


async def log_response(
    context: ServicerContext,
    route: ServerMethodGRPC,
    method_name: str,
    response: Message | None = None,
    streaming_count: int | None = None,
) -> None:
    code = context.code() or StatusCode.OK

    if code is not StatusCode.OK:
        msg = (
            f'{context.peer()} - {route.__qualname__} '
            f'{{{method_name}}} | {code} | {context.details()}'
        )
    else:
        status_part = f'streaming[{streaming_count}]' if streaming_count else StatusCode.OK
        msg = f'{context.peer()} - {route.__qualname__} {{{method_name}}} | {status_part} |'
        resp = re.sub(r'\n+$', '', f'{response or ""}')
        resp = re.sub(r'(?m)^', '  | ', resp)
        msg = f'{msg}\n{resp}'

    logger.debug(msg)
