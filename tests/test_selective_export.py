from typing import TypedDict

import typtyp
from typtyp.typescript import TypeScriptOptions


class Foo(TypedDict):
    size: int


class Bar(TypedDict):
    girth: int


def test_selective_export(checked_ts_snapshot):
    w = typtyp.World()
    w.add_many((Foo, Bar))
    code = w.get_typescript(options=TypeScriptOptions(exported_types={"Foo"}))
    assert checked_ts_snapshot(code)
