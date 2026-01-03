from asyncio import to_thread
from types import NoneType, UnionType
from typing import Any, Callable, Type, Union, _UnionGenericAlias, assert_never, cast
from warnings import catch_warnings

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message as ProtoMessage
from grpc import experimental
from grpc.aio import ServicerContext
from pydantic import ValidationError

from .enums import ServiceModes
from .exceptions import RunTimeServerError, SendEmpty
from .middleware import BaseMiddleware
from .models import Message, Method
from .proto.enums import ProtoBufTypes
from .utils import snake_to_camel

Delay = float
Service = type
MethodType = Callable[[ProtoMessage, str, bool], ProtoMessage]


class MethodGRPC:
    def __init__(self: 'MethodGRPC', method: Method):
        self.method: Method = method

    def __getattr__(self: 'MethodGRPC', attr_name: str) -> Any:
        return getattr(self.method.target.func, attr_name)

    @classmethod
    def proto_to_pydantic(
        cls: Type['MethodGRPC'], message: ProtoMessage, model: Type[Message], method: Method
    ) -> Message:
        params: dict[str, Any] = {}
        model_fields = model.model_fields

        for field in cast(list[FieldDescriptor], message.DESCRIPTOR.fields):
            field_name = field.name
            value = getattr(message, field_name)

            # check if this field is Optional in the Pydantic model
            pydantic_field = model_fields.get(field_name)
            is_optional = False
            if pydantic_field:
                # check if the annotation includes None (Optional)
                annotation = pydantic_field.annotation
                if hasattr(annotation, '__args__'):
                    is_optional = type(None) in annotation.__args__

            if is_optional and not value and value is not False and value != 0:
                value = None

            elif field.message_type and field.message_type.GetOptions().map_entry:
                value = dict(value) if value else {}
            elif field.is_repeated:
                value = [
                    cls.proto_to_pydantic(
                        message=item,
                        model=method.get_additional_message(message_name=field.message_type.name),
                        method=method,
                    )
                    if isinstance(item, ProtoMessage)
                    else item
                    for item in value
                ]
            elif isinstance(value, ProtoMessage):
                value = cls.proto_to_pydantic(
                    message=value,
                    model=method.get_additional_message(message_name=field.message_type.name),
                    method=method,
                )

            params[field_name] = value

        return model(**params)

    @classmethod
    def pydantic_to_proto(
        cls: Type['MethodGRPC'],
        message: Message,
        model: Type[ProtoMessage],
        method: Method,
        warnings: bool = False,
        exclude_types: set[ProtoBufTypes | str] | None = None,
    ) -> ProtoMessage:
        exclude_types: set[ProtoBufTypes | str] = exclude_types or {ProtoBufTypes.BYTES}
        exclude: set[str] = {
            field.name for field in message.fields() if field.type in exclude_types
        }
        dump: dict[str, Any] = message.model_dump(mode='json', warnings=warnings, exclude=exclude)
        params: dict[str, Any] = {}
        for field_name, field_info in message.model_fields.items():
            name = getattr(field_info.annotation, '__name__', None)

            if type(field_info.annotation) in (UnionType, Union) or isinstance(
                field_info.annotation, _UnionGenericAlias
            ):
                # check args of the union type are: (type, NoneType) : len is 2 and one of them is
                # None

                if (
                    not len(field_info.annotation.__args__) == 2
                    and None in field_info.annotation.__args__
                ):
                    raise ValueError(f'Union type {field_info.annotation} not supported')

                # use the name of the type that is not None
                name = (
                    field_info.annotation.__args__[0].__name__
                    if field_info.annotation.__args__[0] is not NoneType
                    else field_info.annotation.__args__[1].__name__
                )

            if name in method.additional_messages:
                inner_message = getattr(message, field_name)
                if inner_message is not None:
                    value: ProtoMessage = cls.pydantic_to_proto(
                        message=inner_message,
                        model=method.get_additional_proto(proto_name=name),
                        method=method,
                        warnings=warnings,
                        exclude_types=exclude_types,
                    )
                else:
                    value = None
            elif field_info.annotation is bytes:
                value: bytes = getattr(message, field_name)
            else:
                value: Any = dump[field_name]
            params[field_name] = value
        return model(**params)  # noqa: args, kwargs

    @classmethod
    def pydantic_to_bytes(
        cls: Type['MethodGRPC'], message: Message, method: Method
    ) -> ProtoMessage:
        message_type: Type[ProtoMessage] = method.get_additional_proto(proto_name='BytesMessage')
        return message_type(bytes=message.model_dump_json().encode())  # noqa: bytes

    @classmethod
    def bytes_to_pydantic(
        cls: Type['MethodGRPC'], message: ProtoMessage, model: Type[Message]
    ) -> Message:
        return model.model_validate_json(json_data=getattr(message, 'bytes').decode())


class ServerMethodGRPC(MethodGRPC):
    def __init__(self, method: Method, middlewares: set[Type[BaseMiddleware]]):
        super().__init__(method=method)
        self.middlewares: set[Type[BaseMiddleware]] = middlewares

        self.target = self.method.target
        self.wrapped_target: BaseMiddleware | None = None
        self.wrap_target()

    def wrap_target(self) -> None:
        for middleware in self.middlewares:
            self.wrapped_target = middleware(target=self.wrapped_target or self.target)

    async def call_target(self, request: Message, context: ServicerContext) -> Message:
        if self.wrapped_target:
            response: Message | None = await self.wrapped_target(request=request, context=context)
        else:
            response: Message | None = await self.target(request=request)
        if not response:
            raise SendEmpty(text='Method did not return anything')
        return response

    async def default_call(
        self: 'ServerMethodGRPC', message: ProtoMessage, context: ServicerContext
    ) -> ProtoMessage | None:
        request: Message = self.proto_to_pydantic(
            message=message, model=self.method.validation_request, method=self.method
        )
        try:
            response: Message = await self.call_target(request=request, context=context)
            return self.pydantic_to_proto(
                message=response, model=self.method.proto_response, method=self.method
            )
        except ValidationError as exc:
            raise RunTimeServerError(details={'validation_error': exc.json()})

    async def bytes_call(
        self: 'ServerMethodGRPC', message: ProtoMessage, context: ServicerContext
    ) -> ProtoMessage | None:
        request: Message = self.bytes_to_pydantic(
            message=message, model=self.method.validation_request
        )
        try:
            response: Message = await self.call_target(request=request, context=context)
            return self.pydantic_to_bytes(message=response, method=self.method)
        except ValidationError as exc:
            raise RunTimeServerError(details={'validation_error': exc.json()})

    async def __call__(
        self: 'ServerMethodGRPC', message: ProtoMessage, context: ServicerContext
    ) -> ProtoMessage | None:
        match self.method.mode:
            case ServiceModes.DEFAULT:
                return await self.default_call(message=message, context=context)
            case ServiceModes.BYTES:
                return await self.bytes_call(message=message, context=context)
            case _:
                return assert_never(self.method.mode)


class ClientMethodGRPC(MethodGRPC):
    def __init__(
        self: 'ClientMethodGRPC',
        method: Method,
        service_name: str,
        host: str,
        port: int = 50051,
        timeout_delay: Delay = 1,
    ):
        super().__init__(method=method)
        self.method: Method = method
        self.service_name: str = service_name
        self.host: str = host
        self.port: int = port
        self.timeout_delay: Delay = timeout_delay

    @property
    def service(self: 'ClientMethodGRPC') -> Service:
        return getattr(self.method.services, f'{self.service_name}')

    @classmethod
    async def call_grpc_method(
        cls: Type['ClientMethodGRPC'], method: MethodType, **kwargs: Any
    ) -> ProtoMessage:
        with catch_warnings(action='ignore', category=experimental.ExperimentalApiWarning):
            return await to_thread(method, **kwargs)

    async def default_call(
        self: 'ClientMethodGRPC', grpc_method: Callable, request: Message
    ) -> Message | None:
        proto_request: ProtoMessage = self.pydantic_to_proto(
            message=request, model=self.method.proto_request, method=self.method
        )
        proto_response: ProtoMessage = await self.call_grpc_method(
            method=grpc_method,
            request=proto_request,
            target=f'{self.host}:{self.port}',
            insecure=True,
            timeout=self.timeout_delay,
        )
        return self.proto_to_pydantic(
            message=proto_response, model=self.method.response, method=self.method
        )

    async def bytes_call(
        self: 'ClientMethodGRPC', grpc_method: Callable, request: Message
    ) -> Message | None:
        proto_request: ProtoMessage = self.pydantic_to_bytes(message=request, method=self.method)
        proto_response: ProtoMessage = await self.call_grpc_method(
            method=grpc_method,
            request=proto_request,
            target=f'{self.host}:{self.port}',
            insecure=True,
            timeout=self.timeout_delay,
        )
        return self.bytes_to_pydantic(message=proto_response, model=self.method.validation_response)

    async def __call__(self: 'ClientMethodGRPC', request: Message) -> Message | None:
        grpc_method: Callable = getattr(
            self.service, snake_to_camel(self.method.target.func.__name__)
        )
        match self.method.mode:
            case ServiceModes.DEFAULT:
                return await self.default_call(grpc_method=grpc_method, request=request)
            case ServiceModes.BYTES:
                return await self.bytes_call(grpc_method=grpc_method, request=request)
            case _:
                return assert_never(self.method.mode)
