from typing import TypedDict

import typtyp
from tests.helpers import check_with_tsc
from typtyp import TypeConfiguration


class Wibblewobble:
    pass


class Toot:
    pass


class Foo(TypedDict):
    wibble: Wibblewobble
    toot: Toot


def test_override(snapshot):
    w = typtyp.World()
    w.add(Foo)
    w.add(Wibblewobble, configuration=TypeConfiguration(import_from=("./webby", "WibWob")))
    w.add(Toot, configuration=TypeConfiguration(import_from=("./webby", "Toot")))
    code = w.get_typescript()
    assert check_with_tsc(code, extra_files={"webby.ts": 'export class WibWob {}\nexport type Toot = "toot!!!";'})
    assert code == snapshot
