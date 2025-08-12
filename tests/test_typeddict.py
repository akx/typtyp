from __future__ import annotations  # This tests that forward references are unnested

from typing import Literal, Optional, TypedDict, Union

import typtyp
from tests.common import HairColor
from tests.helpers import check_with_tsc
from typtyp import TypeConfiguration


class Head(TypedDict):
    size: int
    hair_color: HairColor | None


class Feet(TypedDict):
    shoe_color: Optional[Union[Literal["red"], Literal["blue"]]]


class Person(TypedDict):
    head: Head
    name: str


def test_typeddict(snapshot):
    w = typtyp.World()
    w.add_many((Person, HairColor, Head))
    w.add(Feet, configuration=TypeConfiguration(null_is_undefined=True))
    code = w.get_typescript()
    assert check_with_tsc(code)
    assert code == snapshot
