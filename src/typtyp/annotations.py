import dataclasses


@dataclasses.dataclass(frozen=True)
class Comment:
    comment: str
