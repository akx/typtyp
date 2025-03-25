import dataclasses


@dataclasses.dataclass(frozen=True)
class TypeInfo:
    name: str
    type: type
    doc: str | None = None

    # Consider `null`s in e.g. dataclasses as `undefined` in TypeScript
    null_is_undefined: bool = False
