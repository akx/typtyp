import pytest

import typtyp
from tests.helpers import check_with_tsc


@pytest.fixture
def checked_ts_snapshot(snapshot):
    def _checked_ts_snapshot(world_or_code: str | typtyp.World, /, *snapshot_args, **snapshot_kwargs):
        if isinstance(world_or_code, str):
            code = world_or_code
        else:
            code = world_or_code.get_typescript()
        assert check_with_tsc(code)
        assert code == snapshot(*snapshot_args, **snapshot_kwargs)
        return True

    return _checked_ts_snapshot
