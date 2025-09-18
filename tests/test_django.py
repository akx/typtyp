import pytest

pytest.importorskip("django")

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

from tests.django_interop.models import PetEmergencyContact, PetMedication, PetSittingGig
from tests.helpers import check_with_tsc, typescript_from_types


def test_django(snapshot):
    code = typescript_from_types(
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
    assert check_with_tsc(code)
    assert code == snapshot
