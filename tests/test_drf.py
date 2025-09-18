import pytest

from tests.helpers import check_with_tsc, typescript_from_types

pytest.importorskip("rest_framework")

from tests.django_interop.serializers import (
    PetEmergencyContactSerializer,
    PetMedicationSerializer,
    PetSittingGigSerializer,
    UserSerializer,
)


def test_drf(snapshot):
    code = typescript_from_types(
        (
            UserSerializer,
            PetMedicationSerializer,
            PetEmergencyContactSerializer,
            PetSittingGigSerializer,
        ),
    )
    assert check_with_tsc(code)
    assert code == snapshot
