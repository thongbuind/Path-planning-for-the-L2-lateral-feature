"""c14n/1 and the typed digest of execution.canonical."""

import enum
import math
from dataclasses import dataclass

import pytest

from execution import canonical


class Mode(enum.IntEnum):
    OFF = 0
    ON = 1


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Item:
    name: str
    mode: Mode
    point: Point
    values: tuple[float, ...] = ()
    note: str = ""


def _digest(value, exclude=None):
    d = canonical.Digest(exclude)
    d.update(value)
    return d.hexdigest()


def test_c14n_is_independent_of_key_order_and_keeps_float_bits():
    a = canonical.dumps(canonical.to_plain({"b": 0.1, "a": [1, 2.5]}))
    b = canonical.dumps(canonical.to_plain({"a": [1, 2.5], "b": 0.1}))
    assert a == b == b'{"a":[1,2.5],"b":0.1}'
    near = math.nextafter(0.1, 1.0)
    assert canonical.dumps(canonical.to_plain(near)) != canonical.dumps(canonical.to_plain(0.1))


def test_c14n_dataclass_enum_and_exclusion():
    item = Item("p", Mode.ON, Point(1.0, 2.0), (0.5,), note="free text")
    plain = canonical.to_plain(item, {"Item": {"note"}})
    assert plain == {"@type": "Item", "name": "p", "mode": "ON",
                     "point": {"@type": "Point", "x": 1.0, "y": 2.0}, "values": [0.5]}


def test_c14n_tags_non_finite_floats():
    plain = canonical.to_plain({"a": float("inf"), "b": -float("inf"), "c": float("nan")})
    assert plain == {"a": {"@float": "inf"}, "b": {"@float": "-inf"}, "c": {"@float": "nan"}}
    assert canonical.to_plain("inf") != plain["a"]
    canonical.dumps(plain)  # valid JSON


def test_digest_sees_one_bit_of_one_float():
    a = Item("p", Mode.ON, Point(1.0, 2.0), (0.5, 0.25))
    b = Item("p", Mode.ON, Point(1.0, math.nextafter(2.0, 3.0)), (0.5, 0.25))
    assert _digest(a) != _digest(b)
    assert _digest(a) == _digest(Item("p", Mode.ON, Point(1.0, 2.0), (0.5, 0.25)))


def test_digest_excludes_fields_and_tells_types_apart():
    a = Item("p", Mode.ON, Point(1.0, 2.0), note="x")
    b = Item("p", Mode.ON, Point(1.0, 2.0), note="y")
    assert _digest(a, {"Item": {"note"}}) == _digest(b, {"Item": {"note"}})
    assert _digest(a) != _digest(b)
    assert _digest(1) != _digest(1.0) != _digest(True)
    assert _digest(Mode.OFF) != _digest(0)
    assert _digest((1.0, 2.0)) != _digest([1.0, 2.0, 3.0])


def test_float_record_fast_path_and_fallback_agree_on_order_and_none():
    points = tuple(Point(float(i), float(i) / 3) for i in range(40))
    assert _digest(points) == _digest(tuple(points))
    reordered = points[1:] + points[:1]
    assert _digest(points) != _digest(reordered)

    @dataclass(frozen=True)
    class Maybe:
        x: float
        y: float

    assert _digest(Maybe(1.0, None)) != _digest(Maybe(1.0, 0.0))  # None falls back, no error


def test_numpy_like_arrays_are_hashed_by_bytes():
    np = pytest.importorskip("numpy")
    assert _digest(np.array([1.0, 2.0])) == _digest(np.array([1.0, 2.0]))
    assert _digest(np.array([1.0, 2.0])) != _digest(np.array([1.0, 2.0], dtype=np.float32))
