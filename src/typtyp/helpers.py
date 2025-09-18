from typing import Hashable, Iterable, TypeVar

THashable = TypeVar("THashable", bound=Hashable)


def unique_in_order(values: Iterable[THashable]) -> Iterable[THashable]:
    seen = set()
    for v in values:
        if v in seen:
            continue
        seen.add(v)
        yield v
