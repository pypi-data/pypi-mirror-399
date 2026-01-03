from pathlib import Path
from types import ModuleType
from typing import Any, Type, TypedDict, Unpack

from grpc import protos_and_services

# from jinja2 import Environment, FileSystemLoader, Template
from ..enums import ServiceModes
from ..method import ServerMethodGRPC
from ..middleware import BaseMiddleware
from ..models import Message, Method
from ..utils import camel_to_snake, is_method

# environment: Environment = Environment(
#     loader=FileSystemLoader(searchpath=__module_path__ / 'proto/templates'),
#     trim_blocks=True,
#     autoescape=False,  # noqa: S701
# )


class ExtraKwargs(TypedDict, total=False):
    mode: ServiceModes


class BaseServiceMeta(type):
    def __new__(
        cls: Type['BaseServiceMeta'],
        name: str,
        bases: tuple[Type['BaseServiceMeta'], ...],
        class_dict: dict[str, Any],
        **extra: Unpack[ExtraKwargs],
    ) -> 'BaseServiceMeta':
        class_dict.update(extra)
        class_dict['__extra__'] = extra
        for base in bases:
            class_dict.update(base.__extra__)
        return super().__new__(cls, name, bases, class_dict)

    def __init__(
        cls: 'BaseServiceMeta',
        name: str,
        bases: tuple,
        class_dict: dict[str, Any],
        mode: ServiceModes | None = None,
    ):
        super().__init__(name, bases, class_dict)
        cls.name: str = name
        cls.mode: ServiceModes = mode or class_dict.get('mode', ServiceModes.DEFAULT)
        cls.methods: dict[str, Method] = {}
        cls.messages: dict[str, Type[Message]] = {}
        cls.protos: ModuleType | None = None
        cls.services: ModuleType | None = None
        cls.middlewares: set[Type[BaseMiddleware]] = set()

    def __getattr__(self: 'BaseServiceMeta', attr_name: str) -> ServerMethodGRPC | Any:
        if method := self.methods.get(camel_to_snake(string=attr_name)):
            return ServerMethodGRPC(method=method, middlewares=self.middlewares)
        return getattr(self, attr_name)

    def set_middlewares(self: 'BaseServiceMeta', middlewares: set[Type[BaseMiddleware]]) -> None:
        self.middlewares: set[Type[BaseMiddleware]] = middlewares

    def methods_and_messages(self: 'BaseServiceMeta') -> None:
        for method_name, target in self.__dict__.items():
            if is_method(method=target):
                method: Method = Method.from_target(target=target, mode=self.mode)
                self.methods[method_name] = method
                self.messages.update(method.messages)

    # def get_proto(self: 'BaseServiceMeta') -> str:
    #     self.methods_and_messages()
    #     # template: Template = environment.get_template(name='service.proto.template')
    #     return template.render(
    #         service=self, camel_to_snake=camel_to_snake, snake_to_camel=snake_to_camel
    #     )

    # def gen_proto(self: 'BaseServiceMeta', proto_dir: Path) -> Path:
    def get_proto_path(self: 'BaseServiceMeta', proto_dir: Path) -> Path:
        path: Path = proto_dir / f'{camel_to_snake(string=self.name)}.proto'

        # check it exists or raise an error
        # if not path.exists():
        #     raise FileNotFoundError(f'Could not find proto file: {path}')
        # path.write_text(data=self.get_proto())

        return path

    def get_method(self: 'BaseServiceMeta', method_name: str) -> ServerMethodGRPC:
        return ServerMethodGRPC(method=getattr(self, method_name), middlewares=self.middlewares)

    def init_protos_and_services(self: 'BaseServiceMeta', proto_dir: Path) -> None:
        self.methods_and_messages()
        self.protos, self.services = protos_and_services(
            protobuf_path=str(self.get_proto_path(proto_dir=proto_dir))
        )
        for method in self.methods.values():
            method.protos, method.services = self.protos, self.services
