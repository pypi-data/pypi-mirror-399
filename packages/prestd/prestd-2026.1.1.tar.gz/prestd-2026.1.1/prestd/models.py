from __future__ import annotations

from dataclasses import asdict, is_dataclass
from functools import lru_cache
from typing import Any, Callable, Optional, Sequence, Type, TypeVar, overload

from pydantic import BaseModel, TypeAdapter

from prestd.core import AsyncTable, Table
from prestd.core import _coerce_nested_json_values

T = TypeVar("T", bound=BaseModel)

# -------------------------
# Pydantic v2 codec helpers
# -------------------------


def pydantic_encode(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        payload = obj.model_dump(mode="json", exclude_none=True)
        return _coerce_nested_json_values(payload)
    if is_dataclass(obj):
        return _coerce_nested_json_values(asdict(obj))
    return _coerce_nested_json_values(obj)


@lru_cache(maxsize=256)
def _adapter_for_model(model: Type[BaseModel]) -> TypeAdapter[Any]:
    return TypeAdapter(model)


@lru_cache(maxsize=256)
def _adapter_for_list(model: Type[BaseModel]) -> TypeAdapter[Any]:
    # Avoid typing.List gymnastics; TypeAdapter can take list[Model] in py3.9+.
    return TypeAdapter(list[model])  # type: ignore[index]


def parse_one(model: Type[T]) -> Callable[[Any], T]:
    adapter = _adapter_for_model(model)

    def _parse(obj: Any) -> T:
        return adapter.validate_python(obj)  # type: ignore[return-value]

    return _parse


def parse_list(model: Type[T]) -> Callable[[Any], list[T]]:
    adapter = _adapter_for_list(model)

    def _parse(obj: Any) -> list[T]:
        return adapter.validate_python(obj)  # type: ignore[return-value]

    return _parse


# -------------------------
# Public API: attach a model to a table
# -------------------------


@overload
def as_model(table: Table[Any], model: Type[T]) -> Table[T]: ...
@overload
def as_model(table: AsyncTable[Any], model: Type[T]) -> AsyncTable[T]: ...


def as_model(table: Any, model: Type[T]) -> Any:
    """Return a new Table/AsyncTable that parses responses as the given Pydantic model (v2)."""
    return table.with_codec(
        encode=pydantic_encode,
        parse_one=parse_one(model),
        parse_list=parse_list(model),
    )


__all__ = ["as_model", "pydantic_encode", "parse_one", "parse_list"]
