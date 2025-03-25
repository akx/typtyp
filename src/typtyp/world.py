from __future__ import annotations

import io
from typing import Iterable

from typtyp.type_info import TypeInfo


class _Sentinel:
    pass


NOT_SET = _Sentinel()


class World:
    def __init__(self) -> None:
        self._types_by_name: dict[str, TypeInfo] = {}
        self._types_by_type: dict[type, TypeInfo] = {}

    def add(
        self,
        /,
        typ: type,
        *,
        name: str | None = None,
        doc: str | None | _Sentinel = NOT_SET,
        null_is_undefined: bool = False,
    ) -> TypeInfo:
        if name is None:
            name = typ.__name__
        if isinstance(doc, _Sentinel):
            # You're not a real doc...
            real_doc = getattr(typ, "__doc__", None)
        else:
            real_doc = doc
        assert name  # noqa: S101
        if name in self._types_by_name:
            raise KeyError(f"Type {name} already exists")
        info = TypeInfo(name=name, type=typ, doc=real_doc, null_is_undefined=null_is_undefined)
        self._types_by_name[name] = info
        self._types_by_type[typ] = info
        return info

    def add_many(
        self,
        types: tuple[type, ...] | list[type] | set[type] | dict[str, type],
        *,
        doc: str | None | _Sentinel = NOT_SET,
        null_is_undefined: bool = False,
    ) -> dict[type, TypeInfo]:
        types_it: Iterable[tuple[str | None, type]]
        if isinstance(types, dict):
            types_it = types.items()
        else:
            types_it = ((None, typ) for typ in types)
        ret = {}
        for name, typ in types_it:
            ret[typ] = self.add(typ, name=name, doc=doc, null_is_undefined=null_is_undefined)
        return ret

    def get_name_for_type(self, t: type) -> str:
        return self._types_by_type[t].name

    def __iter__(self):
        return iter(self._types_by_name.values())

    def get_typescript(self) -> str:
        from typtyp.typescript import write_ts

        sio = io.StringIO()
        write_ts(sio, self)
        return sio.getvalue()
