import typtyp


def test_no_builtin_docstring(checked_ts_snapshot):
    w = typtyp.World()
    w.add(list[int], name="ListOfInts")
    assert checked_ts_snapshot(w)
