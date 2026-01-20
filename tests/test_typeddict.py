from __future__ import annotations  # This tests that forward references are unnested

from typing import Literal, Optional, TypedDict, Union

import typtyp
from tests.common import HairColor
from typtyp import TypeConfiguration


class Head(TypedDict):
    size: int
    hair_color: HairColor | None


class Feet(TypedDict):
    shoe_color: Optional[Union[Literal["red"], Literal["blue"]]]


class Person(TypedDict):
    head: Head
    name: str


def test_typeddict(checked_ts_snapshot):
    w = typtyp.World()
    w.add_many((Person, HairColor, Head))
    w.add(Feet, configuration=TypeConfiguration(null_is_undefined=True))
    assert checked_ts_snapshot(w)
