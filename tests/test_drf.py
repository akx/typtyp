import pytest

from tests.helpers import check_with_tsc, typescript_from_types

pytest.importorskip("rest_framework")

from tests.django_interop.enums import DifficultyLevel
from tests.django_interop.serializers import (
    PetEmergencyContactSerializer,
    PetMedicationSerializer,
    PetSittingGigSerializer,
    UserSerializer,
)


def test_drf(snapshot):
    code = typescript_from_types(
        (
            # Do not change the order to keep the snapshot stable
            UserSerializer,
            PetMedicationSerializer,
            PetEmergencyContactSerializer,
            PetSittingGigSerializer,
            DifficultyLevel,
        ),
    )
    assert check_with_tsc(code)
    assert code == snapshot
