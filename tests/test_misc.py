from typing import TypedDict

from tests.helpers import check_with_tsc, typescript_from_types


class DoublyNumber(TypedDict):
    # Will end up `number | string`, not `number | string | number`
    value: float | str | int


def test_duplicate_union_member(snapshot):
    """
    Test that union members with types that end up being the same in TypeScript
    (e.g., float and int both become number) are handled correctly.
    """
    code = typescript_from_types([DoublyNumber])
    assert check_with_tsc(code)
    assert code == snapshot
