from __future__ import annotations

import enum
from typing import Any, Iterable


def get_enum_members(enum_type: type) -> Iterable[tuple[str, enum.Enum]]:
    for name, value in enum_type.__members__.items():  # type: ignore
        yield name, value


def get_enum_labels(enum_type: type, member_name: str) -> dict[str, str] | None:
    labels = enum_type.__dict__.get(member_name)
    if not labels:
        return None

    if isinstance(labels, enum.nonmember):  # Unwrap enum.nonmember (for dicts, etc.)
        labels = labels.value

    if isinstance(labels, type):  # Looks like a namespace subclass
        labels_map = labels.__dict__
    elif isinstance(labels, dict):
        labels_map = labels
    else:
        raise TypeError(f"Unsupported enum labels type: {type(labels)}")

    ret = {}
    for name, member in get_enum_members(enum_type):
        if (label := labels_map.get(name)) is not None:
            ret[name] = str(label)
    return ret or None


def try_derive_choices_enum(choices_dict: dict[Any, Any]) -> type[enum.Enum] | None:
    """
    Return an enum type iff `choices_dict`'s keys represent the value set of one.
    """
    if all(isinstance(choice, enum.Enum) for choice in choices_dict):
        enum_types = {type(choice) for choice in choices_dict}
        if len(enum_types) == 1:
            enum_type = enum_types.pop()
            if set(choices_dict) == set(enum_type):
                return enum_type
    return None
