from typing import TYPE_CHECKING

import pytest

from tests.common import HairColor
from tests.helpers import world_from_types

if TYPE_CHECKING:
    import pydantic
else:
    pydantic = pytest.importorskip("pydantic")


class Head(pydantic.BaseModel):
    size: int
    hair_color: HairColor | None


class Person(pydantic.BaseModel):
    head: Head
    name: str


def test_pydantic(checked_ts_snapshot):
    w = world_from_types(Person, HairColor, Head)
    assert checked_ts_snapshot(w)
