import dataclasses


@dataclasses.dataclass(frozen=True)
class FieldInfo:
    name: str
    type: type
    doc: str | None = None
