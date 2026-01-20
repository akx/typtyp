from typing import TypedDict

from tests.helpers import world_from_types


class DoublyNumber(TypedDict):
    # Will end up `number | string`, not `number | string | number`
    value: float | str | int


def test_duplicate_union_member(checked_ts_snapshot):
    """
    Test that union members with types that end up being the same in TypeScript
    (e.g., float and int both become number) are handled correctly.
    """
    w = world_from_types(DoublyNumber)
    assert checked_ts_snapshot(w)
