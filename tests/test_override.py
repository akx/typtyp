from typing import TypedDict

import typtyp
from typtyp import FieldInfo, TypeConfiguration


class Foo(TypedDict):
    size: int
    color_code: int
    skip_this: str


def test_override(checked_ts_snapshot):
    w = typtyp.World()
    w.add(
        Foo,
        configuration=TypeConfiguration(
            field_overrides={
                "size": {"type": int | str, "doc": "Size of the foo"},
                "color_code": FieldInfo(name="väri", type=str),
                "skip_this": None,
            },
        ),
    )
    assert checked_ts_snapshot(w)
