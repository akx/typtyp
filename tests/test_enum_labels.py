import enum

import typtyp
from tests.helpers import check_with_tsc
from typtyp.type_configuration import TypeConfiguration


class Status(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

    @enum.nonmember
    class Labels:
        PENDING = "Waiting for processing"
        ACTIVE = "Currently active"
        INACTIVE = "No longer active"


class TurtleStatus(enum.StrEnum):
    WAITING = "waiting"
    HOBBLING_ALONG = "hobbling_along"
    DITHERING = "dithering"

    __texts__ = enum.nonmember(
        {
            "WAITING": "In a state of waiting",
            "HOBBLING_ALONG": "Making slow progress",
            "DITHERING": "Unable to decide",
        },
    )


class Priority(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @enum.nonmember
    class Descriptions:
        LOW = "Not urgent"
        MEDIUM = "Somewhat urgent"
        HIGH = "Very urgent"


def test_enum_labels(snapshot):
    w = typtyp.World()
    w.add(Status)
    code = w.get_typescript()
    assert code == snapshot
    assert check_with_tsc(code)


def test_enum_labels_custom_names(snapshot):
    w = typtyp.World()
    w.add(
        Priority,
        configuration=TypeConfiguration(
            enum_labels_field="Descriptions",
            enum_labels_type_suffix="Texts",
        ),
    )
    code = w.get_typescript()
    assert code == snapshot
    assert check_with_tsc(code)


def test_enum_labels_custom_names_dict(snapshot):
    w = typtyp.World()
    w.add(
        TurtleStatus,
        configuration=TypeConfiguration(
            enum_labels_field="__texts__",
            enum_labels_type_suffix="Prose",
        ),
    )
    code = w.get_typescript()
    assert code == snapshot
    assert check_with_tsc(code)
