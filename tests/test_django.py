import pytest

from tests.helpers import world_from_types

pytest.importorskip("django")

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from tests.django_interop.models import PetEmergencyContact, PetMedication, PetSittingGig


def test_django(checked_ts_snapshot):
    w = world_from_types(
        ContentType,
        Group,
        Permission,
        PetEmergencyContact,
        PetMedication,
        PetSittingGig,
        User,
    )
    assert checked_ts_snapshot(w)
