from __future__ import annotations

from typing import Iterable

from pydantic import BaseModel

from typtyp.field_info import FieldInfo


def is_pydantic_model(t) -> bool:
    """
    Infallibly checks if a type is a Pydantic model. Never throws.
    """
    try:
        return issubclass(t, BaseModel)
    except Exception:  # pragma: no cover
        return False


def get_pydantic_fields(tp: type[BaseModel]) -> Iterable[FieldInfo]:
    for name, f in sorted(tp.model_fields.items(), key=lambda item: item[0]):
        yield FieldInfo(
            name=name,
            type=f.annotation,
            required=not bool(f.default or f.default_factory),
        )
