import dataclasses

from typtyp.field_info import FieldInfo, FieldInfoDict


@dataclasses.dataclass(frozen=True, kw_only=True)
class TypeConfiguration:
    # Consider `null`s in e.g. dataclasses as `undefined` in TypeScript
    null_is_undefined: bool = False

    # Overrides for fields in structure-like types (e.g. dataclasses, TypedDicts, pydantic models).
    # If a dict of shape FieldInfoDict is passed in, keys within are merged with the existing field info.
    # If a FieldInfo is passed in, it replaces the existing field info.
    # Fields not originally in the structure can be added here, and fields may likewise be removed
    # by passing in `None` as the value.
    field_overrides: dict[str, FieldInfo | FieldInfoDict | None] = dataclasses.field(default_factory=dict)
