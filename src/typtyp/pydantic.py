from __future__ import annotations

from typing import Any, Iterable

from pydantic import BaseModel


def is_pydantic_model(t) -> bool:
    """
    Infallibly checks if a type is a Pydantic model. Never throws.
    """
    try:
        return issubclass(t, BaseModel)
    except Exception:
        return False


def get_pydantic_fields(tp) -> Iterable[tuple[str, Any]]:
    for name, f in sorted(tp.model_fields.items(), key=lambda item: item[0]):
        yield (name, f.annotation)
