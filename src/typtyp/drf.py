from __future__ import annotations

import datetime
import inspect
import uuid
from decimal import Decimal
from typing import Annotated, Any, Iterable, Literal, Union

from rest_framework import fields, relations, serializers

from typtyp.annotations import Comment
from typtyp.field_info import FieldInfo

STRINGLIKE_FIELDS = (
    fields.CharField,
    fields.EmailField,
    fields.RegexField,
    fields.SlugField,
    fields.URLField,
)

SIMPLE_FIELD_TYPES = {
    fields.BooleanField: bool,
    fields.DateField: datetime.date,
    fields.DateTimeField: datetime.datetime,
    fields.DecimalField: Decimal,
    fields.DurationField: str,
    fields.FileField: Annotated[str, Comment("file field")],  # TODO: Handle more specific types?
    fields.FloatField: float,
    fields.ImageField: Annotated[str, Comment("image field")],  # TODO: Handle more specific types?
    fields.IntegerField: int,
    fields.JSONField: Any,
    fields.TimeField: datetime.time,
    fields.ReadOnlyField: Annotated[  # TODO: can we dig into these?
        Any,
        Comment(comment="read only field, type unknown"),
    ],
    fields.UUIDField: uuid.UUID,
    relations.HyperlinkedRelatedField: str,
    relations.PrimaryKeyRelatedField: Annotated[  # TODO: Handle more specific types?
        Any,
        Comment(comment="primary key related field"),
    ],
}


def is_drf_serializer(t) -> bool:
    """
    Infallibly checks if a type is a DRF serializer. Never throws.
    """
    try:
        return issubclass(t, serializers.Serializer)
    except Exception:  # pragma: no cover
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
    if isinstance(field, fields.ChoiceField):
        return Union[*(Literal[choice] for choice in field.choices)]
    if isinstance(field, serializers.SerializerMethodField):
        method = getattr(field.parent, field.method_name)
        rtype = inspect.get_annotations(method).get("return", Any)
        if isinstance(rtype, str):
            # If the return type is a string, assume it's a forward reference
            return Annotated[
                Any,
                Comment(comment=f"forward reference: {rtype}"),
            ]
        return rtype
    if isinstance(field, STRINGLIKE_FIELDS):
        return str
    for field_type, typ in SIMPLE_FIELD_TYPES.items():
        if isinstance(field, field_type):
            return typ
    raise NotImplementedError(f"Unsupported DRF field type ({type(field).__name__}): {field!r}")  # pragma: no cover


def get_serializer_fields(ser_type: type[serializers.Serializer]) -> Iterable[FieldInfo]:
    context = {"request": None}
    for name, field in sorted(ser_type(context=context).fields.items(), key=lambda item: item[0]):
        yield FieldInfo(
            name=name,
            type=get_drf_field_type(field),
            doc=str(field.help_text) if field.help_text else None,
        )
