from typing import TYPE_CHECKING

import pytest

import typtyp
from tests.common import HairColor
from tests.helpers import check_with_tsc

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


def test_pydantic(snapshot):
    w = typtyp.World()
    w.add_many((Person, HairColor, Head))
    code = w.get_typescript()
    assert code == snapshot
    assert check_with_tsc(code)
