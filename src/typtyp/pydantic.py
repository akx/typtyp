from __future__ import annotations

from typing import Iterable

from pydantic import BaseModel

from typtyp.internal import FieldInfo


def is_pydantic_model(t) -> bool:
    """
    Infallibly checks if a type is a Pydantic model. Never throws.
    """
    try:
        return issubclass(t, BaseModel)
    except Exception:
        return False


def get_pydantic_fields(tp) -> Iterable[FieldInfo]:
    for name, f in sorted(tp.model_fields.items(), key=lambda item: item[0]):
        yield FieldInfo(name=name, type=f.annotation)
