from __future__ import annotations

import datetime
import uuid
from decimal import Decimal
from typing import Annotated, Any, Iterable, Literal, Optional, Union

from django.db import models

from typtyp.annotations import Comment
from typtyp.field_info import FieldInfo

STRINGLIKE_FIELDS = (
    models.CharField,
    models.EmailField,
    models.GenericIPAddressField,
    models.SlugField,
    models.TextField,
    models.URLField,
)

SIMPLE_FIELD_TYPES = {
    models.BinaryField: bytes,
    models.BooleanField: bool,
    models.DateField: datetime.date,
    models.DateTimeField: datetime.datetime,
    models.DecimalField: Decimal,
    models.DurationField: str,
    models.FileField: Annotated[str, Comment("file field")],  # TODO: Handle more specific types?
    models.FloatField: float,
    models.ImageField: Annotated[str, Comment("image field")],  # TODO: Handle more specific types?
    models.IntegerField: int,
    models.JSONField: Any,
    models.TimeField: datetime.time,
    models.UUIDField: uuid.UUID,
}


def get_referred_model_type(field: models.Field, model_type: type[models.Model]):
    if field.related_model == "self":
        return model_type  # self-referential relation
    return field.related_model


def get_django_field_type(field: models.Field, *, model_type: type[models.Model]) -> tuple[type, str | None] | None:
    if flatchoices := getattr(field, "flatchoices", None):
        return (Union[*(Literal[c[0]] for c in flatchoices)], None)
    if isinstance(field, STRINGLIKE_FIELDS):
        return (str, None)
    for field_type, typ in SIMPLE_FIELD_TYPES.items():
        if isinstance(field, field_type):
            return (typ, None)
    if isinstance(field, (models.ManyToManyRel, models.ManyToOneRel)):
        # Skip reverse relations for now.
        return None
    if isinstance(field, models.ManyToManyField):
        return (list[get_referred_model_type(field, model_type)], "many-to-many relation")
    if isinstance(field, models.OneToOneField):
        return (get_referred_model_type(field, model_type), "one-to-one relation")
    if isinstance(field, models.ForeignKey):
        return (get_referred_model_type(field, model_type), "foreign key relation")
    raise NotImplementedError(f"Unsupported Django field type ({type(field).__name__}): {field!r}")  # pragma: no cover


def is_django_model(t) -> bool:
    """
    Infallibly checks if a type is a Django model. Never throws.
    """
    try:
        return issubclass(t, models.Model)
    except Exception:  # pragma: no cover
        return False


def get_model_fields(model_type: type[models.Model]) -> Iterable[FieldInfo]:
    for field in sorted(model_type._meta.get_fields(include_hidden=True), key=lambda field: field.name):
        typ = get_django_field_type(field, model_type=model_type)
        if typ is None:
            continue
        typ, comment = typ
        if field.null:
            typ = Optional[typ]
        if comment:
            typ = Annotated[typ, Comment(comment=comment)]
        yield FieldInfo(
            name=field.name,
            type=typ,
            doc=str(field.help_text) if field.help_text else None,
            required=True,  # TODO: not implemented
        )
