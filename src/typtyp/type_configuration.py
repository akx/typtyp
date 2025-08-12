import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class TypeConfiguration:
    # Consider `null`s in e.g. dataclasses as `undefined` in TypeScript
    null_is_undefined: bool = False
