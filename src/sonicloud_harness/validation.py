from __future__ import annotations

from collections.abc import Iterable
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any, get_args, get_origin, get_type_hints


class ValidationError(ValueError):
    """Raised when a harness object does not satisfy its schema."""


def require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string")


def require_range(value: float, field_name: str, minimum: float, maximum: float) -> None:
    if value < minimum or value > maximum:
        raise ValidationError(f"{field_name} must be between {minimum} and {maximum}")


def require_unique(values: Iterable[str], field_name: str) -> None:
    seen: set[str] = set()
    for value in values:
        if value in seen:
            raise ValidationError(f"{field_name} contains duplicate value: {value}")
        seen.add(value)


def asdict_shallow(instance: Any) -> dict[str, Any]:
    if not is_dataclass(instance):
        raise TypeError("asdict_shallow expects a dataclass instance")

    output: dict[str, Any] = {}
    for field in fields(instance):
        value = getattr(instance, field.name)
        output[field.name] = _to_jsonable(value)
    return output


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return asdict_shallow(value)
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    return value


def parse_enum(enum_type: type[Enum], value: str, field_name: str) -> Enum:
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ValidationError(f"{field_name} must be one of: {allowed}") from exc


def parse_dataclass(cls: type[Any], payload: dict[str, Any]) -> Any:
    if not is_dataclass(cls):
        raise TypeError("parse_dataclass expects a dataclass type")

    kwargs: dict[str, Any] = {}
    type_hints = get_type_hints(cls)
    for field in fields(cls):
        if field.name not in payload:
            raise ValidationError(f"missing required field: {field.name}")
        kwargs[field.name] = _parse_value(type_hints[field.name], payload[field.name], field.name)

    instance = cls(**kwargs)
    validate = getattr(instance, "validate", None)
    if validate:
        validate()
    return instance


def _parse_value(type_hint: Any, value: Any, field_name: str) -> Any:
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is list:
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be a list")
        item_type = args[0]
        return [_parse_value(item_type, item, field_name) for item in value]

    if origin is dict:
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be an object")
        return value

    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        return parse_enum(type_hint, value, field_name)

    if is_dataclass(type_hint):
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name} must be an object")
        return parse_dataclass(type_hint, value)

    return value
