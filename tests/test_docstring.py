import typtyp


def test_no_builtin_docstring(snapshot):
    w = typtyp.World()
    w.add(list[int], name="ListOfInts")
    code = w.get_typescript()
    assert code == snapshot
