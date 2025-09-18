import typtyp
from tests.helpers import check_with_tsc


def test_no_builtin_docstring(snapshot):
    w = typtyp.World()
    w.add(list[int], name="ListOfInts")
    code = w.get_typescript()
    assert check_with_tsc(code)
    assert code == snapshot
