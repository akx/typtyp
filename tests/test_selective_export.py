from typing import TypedDict

import typtyp
from tests.helpers import check_with_tsc
from typtyp.typescript import TypeScriptOptions


class Foo(TypedDict):
    size: int


class Bar(TypedDict):
    girth: int


def test_selective_export(snapshot):
    w = typtyp.World()
    w.add_many((Foo, Bar))
    code = w.get_typescript(options=TypeScriptOptions(exported_types={"Foo"}))
    assert check_with_tsc(code)
    assert code == snapshot
