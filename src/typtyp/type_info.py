import dataclasses

from typtyp.type_configuration import TypeConfiguration


@dataclasses.dataclass(frozen=True, kw_only=True)
class TypeInfo(TypeConfiguration):
    name: str
    type: type
    doc: str | None = None
