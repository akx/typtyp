from typing import TYPE_CHECKING

import pytest

from tests.common import HairColor
from tests.helpers import check_with_tsc, typescript_from_types

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
    code = typescript_from_types([Person, HairColor, Head])
    assert code == snapshot
    assert check_with_tsc(code)
