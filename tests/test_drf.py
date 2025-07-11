import pytest

pytest.importorskip("rest_framework")

import typtyp
from tests.django_interop.serializers import (
    PetEmergencyContactSerializer,
    PetMedicationSerializer,
    PetSittingGigSerializer,
    UserSerializer,
)


def test_drf(snapshot):
    w = typtyp.World()

    w.add_many(
        (
            UserSerializer,
            PetMedicationSerializer,
            PetEmergencyContactSerializer,
            PetSittingGigSerializer,
        ),
    )
    assert w.get_typescript() == snapshot
