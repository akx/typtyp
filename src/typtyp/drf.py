from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Any, Iterable

from rest_framework import fields, relations, serializers

STRINGLIKE_FIELDS = (
    fields.CharField,
    fields.EmailField,
    fields.RegexField,
    fields.SlugField,
    fields.URLField,
)

SIMPLE_FIELD_TYPES = {
    fields.BooleanField: bool,
    fields.ChoiceField: str,  # This could be wrong, technically ChoiceField can be any type
    fields.DateField: datetime.date,
    fields.DateTimeField: datetime.datetime,
    fields.DecimalField: Decimal,
    fields.DurationField: str,
    fields.FileField: str,  # TODO: Handle more specific types?
    fields.FloatField: float,
    fields.ImageField: str,  # TODO: Handle more specific types?
    fields.IntegerField: int,
    fields.JSONField: Any,
    fields.ReadOnlyField: Any,  # TODO: can we dig these?
    fields.TimeField: datetime.time,
    fields.UUIDField: uuid.UUID,
    relations.HyperlinkedRelatedField: str,
    relations.PrimaryKeyRelatedField: Any,  # TODO: Handle more specific types?
    serializers.SerializerMethodField: Any,  # TODO: should look up the return type of the method
}


def is_drf_serializer(t) -> bool:
    """
    Infallibly checks if a type is a DRF serializer. Never throws.
    """
    try:
        return issubclass(t, serializers.Serializer)
    except Exception:
        return False


def get_drf_field_type(field: fields.Field) -> type:
    if isinstance(field, serializers.DictField):
        return dict[Any, get_drf_field_type(field.child)]
    if isinstance(field, fields._UnvalidatedField):
        return Any
    if isinstance(field, fields.ListField):
        return list[get_drf_field_type(field.child)]
    if isinstance(field, serializers.Serializer):
        return field.__class__
    if isinstance(field, serializers.ListSerializer):
        return list[get_drf_field_type(field.child)]
    if isinstance(field, STRINGLIKE_FIELDS):
        return str
    for field_type, typ in SIMPLE_FIELD_TYPES.items():
        if isinstance(field, field_type):
            return typ
    raise NotImplementedError(f"Unsupported DRF field type ({type(field).__name__}): {field!r}")


def get_serializer_fields(ser_type: type[serializers.Serializer]) -> Iterable[tuple[str, Any]]:
    context = {"request": None}
    for name, field in sorted(ser_type(context=context).fields.items(), key=lambda item: item[0]):
        typ = get_drf_field_type(field)
        yield (name, typ)
