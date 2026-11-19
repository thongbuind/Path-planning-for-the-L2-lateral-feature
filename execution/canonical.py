"""Canonical values: c14n/1 JSON for identities and a typed digest for behaviour.

c14n/1 (identity of a resolved case, readable):
  dataclass  -> {"@type": class name, field: value, ...} minus the excluded fields
  enum       -> member name
  tuple/list -> list;  dict -> dict with string keys
  float      -> JSON number written by repr (shortest text that reads back to the same bits)
  inf, NaN   -> {"@float": "inf"}, {"@float": "-inf"}, {"@float": "nan"} (JSON has no such number)
  bytes as text: keys sorted, separators "," ":", UTF-8, no ASCII escaping.

Digest (behaviour checksum, bit exact and fast): every value is fed with a type tag; floats as
IEEE-754 binary64 little endian, so two digests are equal only if every float is equal bit for
bit. Objects with `dtype` and `tobytes` (numpy arrays and scalars) are fed as raw bytes with
their dtype and shape, without importing numpy here.
"""

import dataclasses
import enum
import hashlib
import json
import math
import operator
import struct
import typing

C14N = "c14n/1"

_PACK_D = struct.Struct("<d").pack
_PACK_Q = struct.Struct("<Q").pack


def _fields(cls, exclude: dict[str, set[str]]) -> tuple[str, ...]:
    skip = exclude.get(cls.__name__, ())
    return tuple(f.name for f in dataclasses.fields(cls) if f.name not in skip)


def to_plain(value, exclude: dict[str, set[str]] | None = None):
    """JSON-ready copy of `value` by the c14n/1 rules; `exclude` maps class name -> field names."""
    exclude = exclude or {}
    cache: dict[type, tuple[str, ...]] = {}

    def walk(v):
        if v is None or isinstance(v, (bool, str)):
            return v
        if isinstance(v, enum.Enum):
            return v.name
        if isinstance(v, int):
            return int(v)
        if isinstance(v, float):
            if not math.isfinite(v):  # JSON has no inf or NaN; tagged so no string can match it
                return {"@float": "nan" if math.isnan(v) else ("inf" if v > 0 else "-inf")}
            return float(v)
        if dataclasses.is_dataclass(v) and not isinstance(v, type):
            cls = type(v)
            names = cache.get(cls)
            if names is None:
                names = cache[cls] = _fields(cls, exclude)
            out = {"@type": cls.__name__}
            for name in names:
                out[name] = walk(getattr(v, name))
            return out
        if isinstance(v, (list, tuple)):
            return [walk(x) for x in v]
        if isinstance(v, dict):
            return {str(k): walk(x) for k, x in v.items()}
        if hasattr(v, "dtype") and hasattr(v, "tolist"):  # numpy scalar or array
            return walk(v.tolist())
        raise TypeError(f"no canonical form for {type(v).__name__}")

    return walk(value)


def dumps(plain) -> bytes:
    """c14n/1 bytes of a plain value (output of to_plain)."""
    return json.dumps(plain, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Digest:
    """Streaming sha256 of typed values. `exclude` maps class name -> field names left out.

    Encoding (tag, then payload): N None; T/0 bool; f binary64; i decimal int; s UTF-8 str;
    e enum "Class.member"; [ list or tuple; { dict, keys sorted as text; D dataclass name then
    fields in declaration order; a raw array (dtype, shape, bytes). Lengths are uint64."""

    _FLUSH = 1 << 20

    def __init__(self, exclude: dict[str, set[str]] | None = None) -> None:
        self._h = hashlib.sha256()
        self._buf = bytearray()
        self._exclude = exclude or {}
        # type -> (header, field names) for dataclasses, None for any other type
        self._cache: dict[type, tuple[bytes, tuple[str, ...]] | None] = {}

    def _flush(self) -> None:
        # In place: callers up the recursion hold a reference to this same buffer.
        if self._buf:
            self._h.update(self._buf)
            self._buf.clear()

    def hexdigest(self) -> str:
        self._flush()
        return self._h.hexdigest()

    def raw(self, tag: bytes, data: bytes) -> None:
        """A block of bytes the caller already encoded (for example a float64 array)."""
        self._flush()
        self._h.update(tag + _PACK_Q(len(data)) + data)

    def floats(self, values) -> None:
        """A sequence of floats or of equal-length float tuples, packed in one block."""
        flat = []
        for v in values:
            if isinstance(v, tuple):
                flat.extend(v)
            else:
                flat.append(v)
        self.raw(b"F", struct.pack(f"<{len(flat)}d", *flat))

    def ints(self, values) -> None:
        self.raw(b"I", struct.pack(f"<{len(values)}q", *values))

    def _float_paths(self, cls) -> list[str] | None:
        """Dotted paths of every field when all of them, nested dataclasses included, are
        annotated float; None otherwise."""
        try:
            hints = typing.get_type_hints(cls)
        except Exception:  # noqa: BLE001  unresolvable annotation: no fast path
            return None
        paths = []
        for f in dataclasses.fields(cls):
            if f.name in self._exclude.get(cls.__name__, ()):
                continue
            kind = hints.get(f.name)
            if kind is float:
                paths.append(f.name)
            elif isinstance(kind, type) and dataclasses.is_dataclass(kind):
                inner = self._float_paths(kind)
                if inner is None:
                    return None
                paths += [f"{f.name}.{p}" for p in inner]
            else:
                return None
        return paths

    def _dataclass(self, cls):
        """(header, field getter, Struct of a float record or None), or None for a non-dataclass."""
        if cls not in self._cache:
            entry = None
            if dataclasses.is_dataclass(cls):
                name = cls.__name__.encode()
                head = b"D" + _PACK_Q(len(name)) + name
                paths = self._float_paths(cls)
                if paths and len(paths) > 1:
                    # All floats: one record "R", fetched and packed in C (Trajectory points).
                    entry = (b"R" + head[1:], operator.attrgetter(*paths), struct.Struct(f"<{len(paths)}d"))
                else:
                    names = _fields(cls, self._exclude)
                    getter = (operator.attrgetter(*names) if len(names) > 1
                              else (lambda obj, n=names: tuple(getattr(obj, a) for a in n)))
                    entry = (head, getter, None)
            self._cache[cls] = entry
        return self._cache[cls]

    def _records(self, seq) -> bool:
        """A non-empty sequence of float records of one class, encoded at once; False when
        the sequence is anything else (the caller then encodes member by member)."""
        cls = type(seq[0])
        if cls is float or cls is int or cls is tuple:
            return False
        entry = self._dataclass(cls)
        if entry is None or entry[2] is None:
            return False
        head, getter, record = entry
        pack = record.pack
        try:
            if any(type(x) is not cls for x in seq):
                return False
            data = b"".join([head + pack(*getter(x)) for x in seq])
        except struct.error:
            return False
        self._buf += data
        return True

    def _items(self, values) -> None:
        """Members of a sequence or the fields of a dataclass; floats and ints inline (hot path)."""
        buf = self._buf
        update = self.update
        for x in values:
            tx = type(x)
            if tx is float:
                buf += b"f"
                buf += _PACK_D(x)
            elif tx is int:
                text = str(x).encode()
                buf += b"i"
                buf += _PACK_Q(len(text))
                buf += text
            else:
                update(x)

    def update(self, v) -> None:
        buf = self._buf
        t = type(v)
        if t is float:
            buf += b"f"
            buf += _PACK_D(v)
        elif t is int:
            text = str(v).encode()
            buf += b"i"
            buf += _PACK_Q(len(text))
            buf += text
        elif v is None:
            buf += b"N"
        elif t is bool:
            buf += b"T" if v else b"0"
        elif t is tuple or t is list:
            buf += b"["
            buf += _PACK_Q(len(v))
            if v and not self._records(v):
                self._items(v)
        else:
            entry = self._dataclass(t)
            if entry is not None:
                head, getter, record = entry
                values = getter(v)
                if record is not None:
                    try:
                        data = record.pack(*values)
                    except struct.error:  # a None in a float field: field by field
                        buf += b"D" + head[1:]
                        self._items(values)
                    else:
                        buf += head
                        buf += data
                else:
                    buf += head
                    self._items(values)
            elif isinstance(v, enum.Enum):
                text = f"{t.__name__}.{v.name}".encode()
                buf += b"e" + _PACK_Q(len(text)) + text
            elif isinstance(v, float):
                buf += b"f" + _PACK_D(v)
            elif isinstance(v, bool):
                buf += b"T" if v else b"0"
            elif isinstance(v, int):
                text = str(int(v)).encode()
                buf += b"i" + _PACK_Q(len(text)) + text
            elif isinstance(v, str):
                data = v.encode("utf-8")
                buf += b"s" + _PACK_Q(len(data)) + data
            elif isinstance(v, (list, tuple)):
                buf += b"[" + _PACK_Q(len(v))
                for x in v:
                    self.update(x)
            elif isinstance(v, dict):
                buf += b"{" + _PACK_Q(len(v))
                for k in sorted(v, key=str):
                    self.update(str(k))
                    self.update(v[k])
            elif hasattr(v, "dtype") and hasattr(v, "tobytes"):
                shape = str(getattr(v, "shape", ())).encode()
                self.raw(b"a" + str(v.dtype.str).encode() + shape, v.tobytes())
            else:
                raise TypeError(f"no digest for {t.__name__}")
        if len(self._buf) > self._FLUSH:
            self._flush()
