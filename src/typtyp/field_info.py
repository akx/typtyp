import dataclasses
from typing import TypedDict


@dataclasses.dataclass(frozen=True, kw_only=True)
class FieldInfo:
    name: str
    type: type
    doc: str | None = None
    required: bool  # This is distinct from Optional[type].


class FieldInfoDict(TypedDict, total=False):
    name: str
    type: type
    doc: str | None
    required: bool
