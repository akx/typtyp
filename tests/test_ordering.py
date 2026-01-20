from dataclasses import dataclass

import pytest

import typtyp
from tests.helpers import world_from_types
from typtyp.typescript import TypeScriptOptions


@dataclass
class Zebra:
    name: str


@dataclass
class Apple:
    count: int


@dataclass
class Mango:
    ripe: bool


@dataclass
class Person:
    """All you need to know about a person."""

    zodiac_sign: str
    archenemy: str
    lucky_number: int


@dataclass
class Robot:
    """A mechanical friend."""

    zap_power: int
    arm_count: int
    model_name: str


@pytest.mark.parametrize(
    "ordering",
    [
        pytest.param(None, id="default"),
        pytest.param(lambda ti: ti.name, id="by_name"),
    ],
)
def test_ordering(checked_ts_snapshot, ordering):
    w = world_from_types(Zebra, Apple, Mango)
    code = w.get_typescript(options=TypeScriptOptions(order_by=ordering))
    if ordering:
        assert code.index("Apple") < code.index("Mango") < code.index("Zebra")
    assert checked_ts_snapshot(code)


@pytest.mark.parametrize(
    "ordering",
    [
        pytest.param(None, id="default"),
        pytest.param(lambda fi: fi.name, id="by_name"),
    ],
)
def test_order_fields_by(checked_ts_snapshot, ordering):
    w = world_from_types(Person)
    code = w.get_typescript(options=TypeScriptOptions(order_fields_by=ordering))
    if ordering:
        assert code.index("archenemy") < code.index("lucky_number") < code.index("zodiac_sign")
    assert checked_ts_snapshot(code)


def test_order_fields_by_per_type(checked_ts_snapshot):
    """Per-type order_fields_by overrides the global default."""
    w = typtyp.World()
    w.add(Person)  # No per-type override, will use global default
    w.add(
        Robot,
        configuration=typtyp.TypeConfiguration(
            order_fields_by=lambda fi: fi.name,
        ),
    )
    code = w.get_typescript()
    # Human fields in default order
    assert code.index("zodiac_sign") < code.index("archenemy")
    # Robot fields sorted alphabetically
    assert code.index("arm_count") < code.index("model_name") < code.index("zap_power")
    assert checked_ts_snapshot(code)
