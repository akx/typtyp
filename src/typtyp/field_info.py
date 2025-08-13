import dataclasses
from typing import TypedDict


@dataclasses.dataclass(frozen=True)
class FieldInfo:
    name: str
    type: type
    doc: str | None = None


class FieldInfoDict(TypedDict, total=False):
    name: str
    type: type
    doc: str | None
