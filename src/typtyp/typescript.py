from __future__ import annotations

import collections
import collections.abc
import dataclasses
import datetime
import decimal
import enum
import inspect
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

from typtyp.excs import UnreferrableTypeError
from typtyp.type_info import TypeInfo

if TYPE_CHECKING:
    from typtyp.world import World


RECORD_KEY_TS_TYPE = "string | number | symbol"


def is_pydantic_model(t) -> bool:
    try:
        from pydantic import BaseModel

        return issubclass(t, BaseModel)
    except ImportError:  # pragma: no cover
        return False


class TypeAndKind(NamedTuple):
    type: type
    kind: str | None


@dataclasses.dataclass(frozen=True)
class TypeScriptContext:
    fp: TextIO
    world: World
    null_is_undefined: bool = False
    required_utility_types: dict[str, type] = dataclasses.field(default_factory=dict)

    def sub(self, **replacements):
        return dataclasses.replace(self, **replacements)

    def write(self, s: str) -> None:
        self.fp.write(s)


def map_plain_type_ref(field_type: type, ts_context: TypeScriptContext) -> str:  # noqa: C901, PLR0911, PLR0912
    try:
        # This will handle enums as well – they need to have been registered
        return ts_context.world.get_name_for_type(field_type)
    except KeyError:
        pass

    # Special types

    if isinstance(field_type, ForwardRef):
        return f"unknown /* {field_type.__forward_arg__} */"
    if type(field_type) is TypeVar:
        return f"unknown /* {field_type} */"
    if type(field_type) is type(Ellipsis):
        return "unknown /* ... */"
    if field_type is Any:
        return "unknown /* any */"

    if issubclass(field_type, (bytes, bytearray, memoryview)):
        return f"unknown /* {field_type.__name__} */"

    if issubclass(field_type, bool):
        return "boolean"

    if issubclass(field_type, complex):
        return "[number, number] /* complex */"

    if issubclass(field_type, (pathlib.Path, ipaddress._IPAddressBase, re.Pattern)):
        return f"string /* {field_type.__name__} */"

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
        return f"Record<{RECORD_KEY_TS_TYPE}, number> /* Counter */"

    if issubclass(field_type, dict):
        comment = f" /* {field_type.__name__} */" if field_type is not dict else ""
        return f"Record<{RECORD_KEY_TS_TYPE}, unknown>{comment}"

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


def to_ts_type(field_type: type, ts_context: TypeScriptContext) -> str:  # noqa: C901, PLR0911, PLR0912
    if isinstance(field_type, typing.NewType):
        tp = to_ts_type(field_type.__supertype__, ts_context)  # pyright: ignore
        return f"{tp} /* {field_type.__name__} */"

    origin = typing.get_origin(field_type)

    if origin is collections.abc.Callable:
        return to_ts_function_declaration(field_type, ts_context)

    if origin in (typing.Union, types.UnionType):
        return " | ".join(to_ts_type(sub, ts_context) for sub in typing.get_args(field_type))

    if origin is tuple:
        tps = typing.get_args(field_type)
        if tps and tps[-1] is Ellipsis:
            if len(tps) != 2:
                raise AssertionError(f"Expected tuple with one type and Ellipsis, got {tps}")
            return f"[...{to_ts_type(tps[0], ts_context)}[]]"

        return f"[{', '.join(to_ts_type(tp, ts_context) for tp in tps)}]"

    if origin is typing.Literal:
        return " | ".join(json.dumps(arg) for arg in typing.get_args(field_type))

    # TODO: Smells like this could be done better with the ABCs...
    if origin in (
        list,
        collections.deque,
        set,
        frozenset,
        collections.abc.Iterable,
        collections.abc.Iterator,
        collections.abc.Sequence,
    ):
        comment = f" /* {origin.__name__} */" if origin is not list else ""
        tps = typing.get_args(field_type)
        if len(tps) != 1:
            raise AssertionError(f"Expected list with one type, got {tps}")
        inner = to_ts_type(tps[0], ts_context)
        if inner.rstrip("[]").isalnum():
            return f"({inner})[]{comment}"
        return f"Array<{inner}>{comment}"

    if origin is collections.Counter:
        tps = typing.get_args(field_type)
        if len(tps) != 1:
            raise AssertionError(f"Expected Counter with one type, got {tps}")
        return f"Record<{to_ts_type(tps[0], ts_context)}, number>"

    if origin in (
        dict,
        collections.defaultdict,
        collections.abc.Mapping,
        collections.abc.MutableMapping,
        collections.OrderedDict,
    ):
        comment = f" /* {origin.__name__} */" if origin is not dict else ""
        tps = typing.get_args(field_type)
        if len(tps) != 2:
            raise AssertionError(f"Expected dict with two types, got {tps}")
        return f"Record<{to_ts_type(tps[0], ts_context)}, {to_ts_type(tps[1], ts_context)}>{comment}"

    if origin is not None:
        raise NotImplementedError(f"Unknown origin {origin!r} for {field_type!r}")  # pragma: no cover

    if hasattr(field_type, "_fields") and issubclass(field_type, tuple):
        # NamedTuple defined inline? I guess, why not...
        fields: list[str] = field_type._fields  # pyright: ignore
        contents = (f"unknown /* {name} */" for name in fields)
        return f"[{', '.join(contents)}] /* {field_type.__name__} */"

    return map_plain_type_ref(field_type, ts_context)


def get_struct_types(tp) -> list[tuple[str, Any]] | None:
    if dataclasses.is_dataclass(tp):
        return [(f.name, f.type) for f in dataclasses.fields(tp)]

    if typing.is_typeddict(tp):
        # TODO: support __total__
        # TODO: support __required_keys__
        # TODO: support __optional_keys__
        return list(inspect.get_annotations(tp).items())

    try:
        if is_pydantic_model(tp):
            return [(name, f.annotation) for (name, f) in sorted(tp.model_fields.items(), key=lambda item: item[0])]
    except TypeError:  # pragma: no cover
        pass

    return None


def write_structlike(ctx: TypeScriptContext, type_info: TypeInfo, name_and_type: Iterable[tuple[str, type]]) -> None:
    ctx = ctx.sub(null_is_undefined=type_info.null_is_undefined)
    ctx.write(f"interface {type_info.name} {{\n")
    for name, typ in name_and_type:
        ts_type = to_ts_type(typ, ts_context=ctx).strip()
        field_suffix = ""
        if "| undefined" in ts_type:
            ts_type = ts_type.replace("| undefined", "")
            field_suffix = "?"
        ctx.write(f"{name}{field_suffix}: {ts_type}\n")
    ctx.write("}\n")


def write_enum(ctx: TypeScriptContext, type_info: TypeInfo) -> None:
    ctx.write(f"const enum {type_info.name} {{\n")
    for name, value in type_info.type.__members__.items():  # type: ignore
        ctx.write(f"{name} = {json.dumps(value.value)},\n")
    ctx.write("}\n")


def write_type(ctx: TypeScriptContext, type_info: TypeInfo) -> None:
    if type_info.doc:
        ctx.write("/**\n")
        for line in textwrap.dedent(type_info.doc).strip().splitlines():
            ctx.write(f" * {line}\n")
        ctx.write(" */\n")

    if isinstance(type_info.type, type) and issubclass(type_info.type, enum.Enum):
        return write_enum(ctx, type_info)

    if (nt := get_struct_types(type_info.type)) is not None:
        write_structlike(ctx, type_info, nt)
    else:
        ctx.write(f"type {type_info.name} = {to_ts_type(type_info.type, ctx)}\n")


def write_ts(fp: typing.TextIO, world: World) -> None:
    ctx = TypeScriptContext(fp=fp, world=world)
    for type_info in ctx.world:
        write_type(ctx, type_info)
    for name, typ in sorted(ctx.required_utility_types.items()):
        write_type(ctx, TypeInfo(name=name, type=typ))
