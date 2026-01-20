from typing import TypedDict

import typtyp
from tests.helpers import check_with_tsc
from typtyp import FieldInfo, TypeConfiguration


class Foo(TypedDict):
    size: int
    color_code: int
    skip_this: str


def test_override(snapshot):
    w = typtyp.World()
    w.add(
        Foo,
        configuration=TypeConfiguration(
            field_overrides={
                "size": {"type": int | str, "doc": "Size of the foo"},
                "color_code": FieldInfo(name="väri", type=str, required=True),
                "skip_this": None,
            },
        ),
    )
    code = w.get_typescript()
    assert check_with_tsc(code)
    assert code == snapshot
