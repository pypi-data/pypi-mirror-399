import dataclasses
import datetime
from collections import deque
from decimal import Decimal
from enum import Enum
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network, IPv4Interface, IPv6Interface
from pathlib import PurePath, Path
from types import GeneratorType
from typing import Any, Optional, Callable, Literal, Union, Pattern
from uuid import UUID

from fastapi.encoders import encoders_by_class_tuples
from pydantic import BaseModel, NameEmail, SecretBytes, SecretStr, AnyUrl
from pydantic_core import Url


def _model_dump(model: BaseModel, mode: Literal["json", "python"] = "json", **kwargs):
    return model.model_dump(mode=mode, **kwargs)

def isoformat(o: Union[datetime.date, datetime.time]) -> str:
    return o.isoformat()

def decimal_encoder(dec_value: Decimal) -> Union[int, float]:
    if dec_value.as_tuple().exponent >= 0:
        return int(dec_value)
    return float(dec_value)

ENCODERS_BY_TYPE: dict[type[Any], Callable[[Any], Any]] = {
    bytes: lambda x: x.decode(),
    # Color: str,
    datetime.date: isoformat,
    datetime.datetime: isoformat,
    datetime.timedelta: lambda x: x.total_seconds(),
    Decimal: decimal_encoder,
    Enum: lambda x: x.value,
    frozenset: list,
    deque: list,
    GeneratorType: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    NameEmail: str,
    Path: str,
    Pattern: lambda x: x.pattern,
    SecretBytes: str,
    SecretStr: str,
    set: list,
    UUID: str,
    Url: str,
    AnyUrl: str,
}

def jsonable_encoder(
        obj: Any,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        custom_encoder: Optional[dict[Any, Callable[[Any], Any]]] = None,
        sqlalchemy_safe: bool = True,
):
    custom_encoder = custom_encoder or {}
    if custom_encoder:
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        else:
            for encoder_type, encoder_instance in custom_encoder.items():
                if isinstance(obj, encoder_type):
                    return encoder_instance(obj)
    if isinstance(obj, BaseModel):
        obj_dict = _model_dump(
            obj,
            mode="json",
            include=None,
            exclude=None,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )
        if "__root__" in obj_dict:
            obj_dict = obj_dict["__root__"]
        return jsonable_encoder(
            obj_dict,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            sqlalchemy_safe=sqlalchemy_safe,
        )

    if dataclasses.is_dataclass(obj):
        if not isinstance(obj, type):
            obj_dict = dataclasses.asdict(obj)
            return jsonable_encoder(
                obj_dict,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                custom_encoder=custom_encoder,
                sqlalchemy_safe=sqlalchemy_safe,
            )
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(obj, str | int | float | type(None)):
        return obj
    if isinstance(obj, Decimal):
        return format(obj, "f")
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            if (not sqlalchemy_safe or (not isinstance(key, str)) or (not key.startswith("_sa"))) and (value is not None or not exclude_none):
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    if isinstance(obj, list | set | frozenset | GeneratorType | tuple | deque):
        encoded_list = []
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list

    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)

    for encoder, classes_tuple in encoders_by_class_tuples.items():
        if isinstance(obj, classes_tuple):
            return encoder(obj)

    try:
        data = dict(obj)
    except Exception as ex:
        errors: list[Exception] = []
        errors.append(ex)
        try:
            data = vars(obj)
        except Exception as ex:
            errors.append(ex)
            raise ValueError(errors) from ex

    return jsonable_encoder(
        data,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )

