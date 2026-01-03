from datetime import date, datetime, time
from enum import Enum
from inspect import isclass
from types import GenericAlias, NoneType, UnionType
from typing import Annotated, Any, Iterable, Union, get_origin
from uuid import UUID

from pydantic import BaseModel

from .enums import ProtoBufTypes

TYPE_MAPPING: dict[type, ProtoBufTypes] = {
    int: ProtoBufTypes.INT64,
    float: ProtoBufTypes.DOUBLE,
    bool: ProtoBufTypes.BOOL,
    str: ProtoBufTypes.STRING,
    bytes: ProtoBufTypes.BYTES,
    dict: ProtoBufTypes.MAP,
    UUID: ProtoBufTypes.STRING,
    date: ProtoBufTypes.STRING,
    time: ProtoBufTypes.STRING,
    datetime: ProtoBufTypes.STRING,
}


def parse_type(
    field_name: str, python_value: Any, field_type: type, allow_model: bool = True
) -> ProtoBufTypes | str:
    if python_value in TYPE_MAPPING:
        return TYPE_MAPPING[python_value]
    elif (origin := get_origin(python_value)) is not None and origin in (
        Annotated,
        Union,
        UnionType,
    ):
        return parse_type_union(
            field_name=field_name, field_type=python_value, args=list(python_value.__args__)
        )['type']
    elif allow_model and isclass(python_value) and issubclass(python_value, BaseModel):
        return python_value.__name__
    raise TypeError(
        f'Field `{field_name}`: unsupported type `{python_value}` in type `{field_type}`.'
    )


def parse_type_union(
    field_name: str, field_type: type | None | GenericAlias, args: list
) -> dict[str, Any]:
    if NoneType in args:
        args.remove(NoneType)
    if len(args) != 1:
        raise TypeError(
            f'Field `{field_name}`: type `{field_type}` must have only one subtype, not '
            f'{len(args)}. Tip: None/Optional type ignoring.'
        )
    return {
        'name': field_name,
        'type': parse_type(field_name=field_name, python_value=args[0], field_type=field_type),
    }


def parse_type_sequence(
    field_name: str, field_type: type | None | GenericAlias, args: list
) -> dict[str, Any]:
    if len(args) != 1:
        raise TypeError(
            f'Field `{field_name}`: type `{field_type}` must have only one subtype, not'
            f' {len(args)}.'
        )

    return {
        'name': field_name,
        'type': parse_type(field_name=field_name, python_value=args[0], field_type=field_type),
        'repeated': True,
    }


def parse_type_mapping(
    field_name: str, field_type: type | None | GenericAlias, args: list
) -> dict[str, Any]:
    if len(args) != 2:
        raise TypeError(
            f'Field `{field_name}`: type `{field_type}` must have two subtypes, not {len(args)}'
        )

    return {
        'name': field_name,
        'type': ProtoBufTypes.MAP,
        'map_key': parse_type(
            field_name=field_name, python_value=args[0], field_type=field_type, allow_model=False
        ),
        'map_value': parse_type(field_name=field_name, python_value=args[1], field_type=field_type),
    }


def parse_field_type(field_name: str, field_type: type) -> dict[str, Any]:
    if proto_buf_type := TYPE_MAPPING.get(field_type):
        return {'name': field_name, 'type': proto_buf_type}

    if isclass(field_type):
        if issubclass(field_type, BaseModel):
            return {'name': field_name, 'type': field_type.__name__}
        if issubclass(field_type, Enum):
            return {'name': field_name, 'type': ProtoBufTypes.STRING}

    origin = get_origin(tp=field_type)

    if origin is not None:
        args: list = list(field_type.__args__)
        if origin in (Union, UnionType):
            return parse_type_union(field_name=field_name, field_type=field_type, args=args)
        if issubclass(origin, dict):
            return parse_type_mapping(field_name=field_name, field_type=field_type, args=args)
        if issubclass(origin, Iterable):
            return parse_type_sequence(field_name=field_name, field_type=field_type, args=args)
        raise TypeError(f'Field unsupported type `{field_type}`')

    raise TypeError(f'Field unsupported type `{field_type}`')
