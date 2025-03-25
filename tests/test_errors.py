from dataclasses import dataclass
from typing import List

import pytest

import typtyp
from typtyp.excs import UnreferrableTypeError


@dataclass
class User:
    name: str


@dataclass
class Team:
    name: str
    members: List[User]
    admins: list[User]


def test_unreferrable():
    world = typtyp.World()
    world.add(Team)
    with pytest.raises(UnreferrableTypeError):
        # We forgot to explicitly add `User`.
        world.get_typescript()


def test_duplicate():
    world = typtyp.World()
    world.add(str, name="Team")
    with pytest.raises(KeyError):
        world.add(Team)
