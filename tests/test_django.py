import pytest

pytest.importorskip("django")

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

import typtyp
from tests.django_interop.models import PetEmergencyContact, PetMedication, PetSittingGig


def test_django(snapshot):
    w = typtyp.World()

    w.add_many(
        (
            ContentType,
            Group,
            Permission,
            PetEmergencyContact,
            PetMedication,
            PetSittingGig,
            User,
        ),
    )
    assert w.get_typescript() == snapshot
