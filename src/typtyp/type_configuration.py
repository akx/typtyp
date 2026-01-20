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

    # Instead of emitting this type at all, import it from the given module from the given name.
    import_from: tuple[str, str] | None = None

    # For enums, the name of a field to look for that contains labels;
    # either a subclass, or a dict.
    # If found, a mapping of enum value -> label string will be exported.
    # Set to None to disable label export.
    enum_labels_field: str | None = "Labels"

    # When labels are found, the suffix to add to the enum type name for the labels type.
    enum_labels_type_suffix: str = "Labels"

    # Whether to emit non-required fields (e.g. TypedDict's NotRequired, or DRF's `required=False`)
    # as optional (e.g. `field?: type` in TypeScript).
    non_required_fields_optional: bool = True

    def __post_init__(self):
        if self.import_from is not None:
            if self.field_overrides:
                raise ValueError("field_overrides cannot be used with import_from")
