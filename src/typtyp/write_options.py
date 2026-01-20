from __future__ import annotations

import dataclasses
from typing import Any, Callable

from typtyp.field_info import FieldInfo
from typtyp.type_info import TypeInfo


@dataclasses.dataclass(frozen=True)
class WriteOptions:
    # Sort key function for ordering types in the output.
    # If None, types are emitted in their registration order.
    order_by: Callable[[TypeInfo], Any] | None = None

    # Default sort key function for ordering fields within struct-like types.
    # Can be overridden per-type via TypeConfiguration.order_fields_by.
    # If None, fields are emitted in their original order.
    order_fields_by: Callable[[FieldInfo], Any] | None = None
