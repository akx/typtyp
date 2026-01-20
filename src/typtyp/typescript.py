from __future__ import annotations

import collections
import collections.abc
import dataclasses
import datetime
import decimal
import enum
import ipaddress
import json
import pathlib
import re
import textwrap
import types
import typing
import uuid
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ForwardRef, NamedTuple, TextIO, TypeVar

from typtyp.annotations import Comment
from typtyp.consts import COLLECTION_ORIGINS, MAPPING_ORIGINS
from typtyp.enums import get_enum_labels, get_enum_members
from typtyp.excs import UnreferrableTypeError
from typtyp.field_info import FieldInfo, FieldInfoDict
from typtyp.helpers import unique_in_order
from typtyp.type_info import TypeInfo

if TYPE_CHECKING:
    from typtyp.world import World


RECORD_KEY_TS_TYPE = "string | number | symbol"


class TypeAndKind(NamedTuple):
    type: type
    kind: str | None


@dataclasses.dataclass(frozen=True)
class TypeScriptOptions:
    exported_types: set[str] | bool = True


@dataclasses.dataclass(frozen=True)
class TypeScriptContext:
    fp: TextIO
    world: World
    options: TypeScriptOptions
    null_is_undefined: bool = False
    required_utility_types: dict[str, type] = dataclasses.field(default_factory=dict)

    def sub(self, **replacements):
        return dataclasses.replace(self, **replacements)

    def write(self, s: str) -> None:
        self.fp.write(s)

    def get_export_modifier(self, type_info: TypeInfo) -> str:
        exported = self.options.exported_types
        if exported is False:
            return ""
        if exported is True or type_info.name in exported:
            return "export "
        return ""


@dataclasses.dataclass(frozen=True)
class TSTypeAndComment:
    name: str
    comments: list[str] = dataclasses.field(default_factory=list)


def map_plain_type_ref(
    field_type: type,
    ts_context: TypeScriptContext,
    *,
    elide_any_comment=False,
) -> str | TSTypeAndComment:
    try:
        # This will handle enums as well – they need to have been registered
        return ts_context.world.get_name_for_type(field_type)
    except KeyError:
        pass

    # Special types

    if isinstance(field_type, ForwardRef):
        return TSTypeAndComment("unknown", [f"forward reference: {field_type.__forward_arg__}"])
    if type(field_type) is TypeVar:
        return TSTypeAndComment("unknown", [f"type: {field_type}"])
    if type(field_type) is type(Ellipsis):
        return TSTypeAndComment("unknown", ["..."])
    if field_type is Any:
        return TSTypeAndComment("unknown", ["any" if not elide_any_comment else ""])

    if issubclass(field_type, (bytes, bytearray, memoryview)):
        return TSTypeAndComment("unknown", [field_type.__name__])

    if issubclass(field_type, bool):
        return "boolean"

    if issubclass(field_type, complex):
        return TSTypeAndComment("[number, number]", ["complex"])

    if issubclass(field_type, (pathlib.Path, ipaddress._IPAddressBase, re.Pattern)):
        return TSTypeAndComment("string", [field_type.__name__])

    if issubclass(field_type, (int, float, decimal.Decimal, datetime.timedelta)) and not issubclass(
        field_type,
        enum.Enum,
    ):
        return "number"

    if issubclass(field_type, uuid.UUID):
        ts_context.required_utility_types["UUID"] = str
        return "UUID"

    if issubclass(field_type, str) and not issubclass(field_type, enum.Enum):
        return "string"

    if issubclass(field_type, type(None)):
        if ts_context.null_is_undefined:
            return "undefined"
        return "null"

    if field_type is datetime.date:
        ts_context.required_utility_types["ISO8601Date"] = str
        return "ISO8601Date"

    if field_type is datetime.time:
        ts_context.required_utility_types["ISO8601Time"] = str
        return "ISO8601Time"

    if field_type is datetime.datetime:
        ts_context.required_utility_types["ISO8601"] = str
        return "ISO8601"

    if issubclass(field_type, collections.Counter):
        return TSTypeAndComment(f"Record<{RECORD_KEY_TS_TYPE}, number>", ["Counter"])

    if issubclass(field_type, dict):
        comment = field_type.__name__ if field_type is not dict else ""
        return TSTypeAndComment(f"Record<{RECORD_KEY_TS_TYPE}, unknown>", [comment])

    raise UnreferrableTypeError(f"Unable to refer to the type {field_type!r}; if it's a struct, add it to the world")


def to_ts_function_declaration(field_type: type, ts_context: TypeScriptContext) -> str:
    tps = typing.get_args(field_type)
    if len(tps) == 2:
        args_list, retval = tps
        arglist = ", ".join(f"_{i}: {to_ts_type(arg, ts_context)}" for i, arg in enumerate(args_list))
        return f"({arglist}) => {to_ts_type(retval, ts_context)}"
    if len(tps) == 0:
        return "Function"
    raise AssertionError(f"Expected Callable with 0 or 2 types, got {tps}")


def format_comment(comments: list[str]) -> str:
    comments = [c.strip() for c in comments if c.strip()]
    if not comments:
        return ""
    comment_string = ", ".join(comments)
    return f" /* {comment_string} */"


def maybe_add_comments(expr, comments: list[str]) -> str:
    formatted_comments = format_comment(comments)
    return f"{expr}{formatted_comments}"


def to_ts_type(field_type: type, ts_context: TypeScriptContext) -> str:  # noqa: C901, PLR0911, PLR0912
    if isinstance(field_type, typing.NewType):
        tp = to_ts_type(field_type.__supertype__, ts_context)  # pyright: ignore
        return f"{tp} /* {field_type.__name__} */"

    origin = typing.get_origin(field_type)

    annotations = []

    if origin is typing.Annotated:
        # Peel off outermost Annotated, if any...
        field_type, *annotations = typing.get_args(field_type)
        origin = typing.get_origin(field_type)

    comments = [c.comment for c in annotations if isinstance(c, Comment)]

    if origin is collections.abc.Callable:
        return maybe_add_comments(
            to_ts_function_declaration(field_type, ts_context),
            comments,
        )

    if origin in (typing.Union, types.UnionType):
        expr = " | ".join(unique_in_order(to_ts_type(sub, ts_context) for sub in typing.get_args(field_type)))
        return maybe_add_comments(expr, comments)

    if origin is tuple:
        tps = typing.get_args(field_type)
        if tps and tps[-1] is Ellipsis:
            if len(tps) != 2:
                raise AssertionError(f"Expected tuple with one type and Ellipsis, got {tps}")
            expr = f"[...{to_ts_type(tps[0], ts_context)}[]]"
        else:
            expr = f"[{', '.join(to_ts_type(tp, ts_context) for tp in tps)}]"
        return maybe_add_comments(expr, comments)

    if origin is typing.Literal:
        expr = " | ".join(unique_in_order(json.dumps(arg) for arg in typing.get_args(field_type)))
        if not expr:
            raise AssertionError(f"Literal with no arguments is not allowed: {field_type!r}")
        return maybe_add_comments(expr, comments)

    if origin in COLLECTION_ORIGINS:  # TODO: Smells like this could be done better with the ABCs...
        if origin is not list:
            comments.insert(0, origin.__name__)
        tps = typing.get_args(field_type)
        if len(tps) != 1:
            raise AssertionError(f"Expected list with one type, got {tps}")
        inner = to_ts_type(tps[0], ts_context)
        if inner.rstrip("[]").isalnum():
            expr = f"({inner})[]"
        else:
            expr = f"Array<{inner}>"
        return maybe_add_comments(expr, comments)

    if origin is collections.Counter:
        tps = typing.get_args(field_type)
        if len(tps) != 1:
            raise AssertionError(f"Expected Counter with one type, got {tps}")
        expr = f"Record<{to_ts_type(tps[0], ts_context)}, number>"
        return maybe_add_comments(expr, comments)

    if origin in MAPPING_ORIGINS:  # TODO: Smells like this could be done better with the ABCs...
        if origin is not dict:
            comments.insert(0, origin.__name__)
        tps = typing.get_args(field_type)
        if len(tps) != 2:
            raise AssertionError(f"Expected dict with two types, got {tps}")
        expr = f"Record<{to_ts_type(tps[0], ts_context)}, {to_ts_type(tps[1], ts_context)}>"
        return maybe_add_comments(expr, comments)

    if origin is not None:
        raise NotImplementedError(f"Unknown origin {origin!r} for {field_type!r}")  # pragma: no cover

    if hasattr(field_type, "_fields") and issubclass(field_type, tuple):
        # NamedTuple defined inline? I guess, why not...
        comments.insert(0, field_type.__name__)
        fields: list[str] = field_type._fields  # pyright: ignore
        contents = (f"unknown /* {name} */" for name in fields)
        expr = f"[{', '.join(contents)}]"
        return maybe_add_comments(expr, comments)

    plain_ref_ret = map_plain_type_ref(
        field_type,
        ts_context,
        elide_any_comment=bool(
            comments,  # If we have comments, we expect them to explain the situation better than "any"
        ),
    )
    if isinstance(plain_ref_ret, str):
        type_name = plain_ref_ret
    else:
        type_name = plain_ref_ret.name
        comments.extend(plain_ref_ret.comments)
    return maybe_add_comments(type_name, comments)


def get_struct_types(tp) -> list[FieldInfo] | None:
    if dataclasses.is_dataclass(tp):
        return [FieldInfo(name=f.name, type=f.type, required=True) for f in dataclasses.fields(tp)]

    if typing.is_typeddict(tp):
        # TODO: support __total__
        return [
            FieldInfo(
                name=name,
                type=type,
                required=True,  # TODO: support __required_keys__ / __optional_keys__
            )
            for (name, type) in typing.get_type_hints(tp, include_extras=True).items()
        ]

    try:
        from typtyp.pydantic import get_pydantic_fields, is_pydantic_model

        if is_pydantic_model(tp):
            return list(get_pydantic_fields(tp))
    except ImportError:  # pragma: no cover  # TODO: handle ImportError better
        pass

    try:
        from typtyp.drf import get_serializer_fields, is_drf_serializer

        if is_drf_serializer(tp):
            return list(get_serializer_fields(tp))
    except ImportError:  # pragma: no cover  # TODO: handle ImportError better
        pass

    try:
        from typtyp.django import get_model_fields, is_django_model

        if is_django_model(tp):
            return list(get_model_fields(tp))
    except ImportError:  # pragma: no cover  # TODO: handle ImportError better
        pass

    return None


def maybe_write_doc(ctx: TypeScriptContext, doc: str | None) -> None:
    if not doc:
        return
    lines = textwrap.dedent(doc).strip().splitlines()
    if len(lines) > 1:
        ctx.write("/**\n")
        for line in lines:
            ctx.write(f" * {line}\n")
        ctx.write(" */\n")
    else:
        ctx.write(f"/** {lines[0]} */\n")


_NO_OVERRIDE = object()


def merge_overrides(
    field_infos: Iterable[FieldInfo],
    field_overrides: dict[str, FieldInfo | FieldInfoDict | None],
) -> Iterable[FieldInfo]:
    for fi in field_infos:
        try:
            override = field_overrides[fi.name]
        except KeyError:
            yield fi  # No override
        else:
            if override is None:  # Skip the field
                continue
            if isinstance(override, FieldInfo):  # Full override
                yield override
                continue
            if isinstance(override, dict):  # Merge override
                yield dataclasses.replace(fi, **override)
                continue
            raise TypeError(f"Expected FieldInfo or FieldInfoDict, got {override!r} for field {fi.name!r}")


def write_structlike(ctx: TypeScriptContext, type_info: TypeInfo, field_infos: Iterable[FieldInfo]) -> None:
    ctx = ctx.sub(null_is_undefined=type_info.null_is_undefined)
    ctx.write(f"{ctx.get_export_modifier(type_info)}interface {type_info.name} {{\n")
    for fi in merge_overrides(field_infos, type_info.field_overrides):
        ts_type = to_ts_type(fi.type, ts_context=ctx).strip()
        field_suffix = ""
        if "| undefined" in ts_type or (type_info.non_required_fields_optional and not fi.required):
            ts_type = ts_type.replace("| undefined", "")
            field_suffix = "?"
        maybe_write_doc(ctx, fi.doc)
        ctx.write(f"{fi.name}{field_suffix}: {ts_type}\n")
    ctx.write("}\n")


def write_enum(ctx: TypeScriptContext, type_info: TypeInfo) -> None:
    type_name = type_info.name
    export_modifier = ctx.get_export_modifier(type_info)

    ctx.write(f"{export_modifier}const enum {type_name} {{\n")
    for name, value in get_enum_members(type_info.type):  # type: ignore
        ctx.write(f"{name} = {json.dumps(value.value)},\n")
    ctx.write("}\n")

    if type_info.enum_labels_field:
        if labels := get_enum_labels(type_info.type, type_info.enum_labels_field):
            ctx.write(f"{export_modifier}const {type_name}{type_info.enum_labels_type_suffix}")
            ctx.write(f": Record<{type_name}, string> = {{\n")
            for name, label in labels.items():
                ctx.write(f"[{type_name}.{name}]: {json.dumps(label)},\n")
            ctx.write("}\n")


def write_type(ctx: TypeScriptContext, type_info: TypeInfo) -> None:
    maybe_write_doc(ctx, type_info.doc)

    if type_info.import_from:
        mod, orig_name = type_info.import_from
        if type_info.name == orig_name:
            ctx.write(f"import {{ {orig_name} }} from {str(mod)!r}\n")
        else:
            ctx.write(f"import {{ {orig_name} as {type_info.name} }} from {str(mod)!r}\n")
        return

    if isinstance(type_info.type, type) and issubclass(type_info.type, enum.Enum):
        write_enum(ctx, type_info)
        return

    if (children := get_struct_types(type_info.type)) is not None:
        write_structlike(ctx, type_info, children)
    else:
        ctx.write(f"{ctx.get_export_modifier(type_info)}type {type_info.name} = {to_ts_type(type_info.type, ctx)}\n")


def write_ts(fp: typing.TextIO, world: World, *, options: TypeScriptOptions | None = None) -> None:
    if options is None:
        options = TypeScriptOptions()
    ctx = TypeScriptContext(fp=fp, world=world, options=options)
    for type_info in ctx.world:
        write_type(ctx, type_info)
    for name, typ in sorted(ctx.required_utility_types.items()):
        write_type(ctx, TypeInfo(name=name, type=typ))
