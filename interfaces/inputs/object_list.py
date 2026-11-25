"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.2."""

from __future__ import annotations

from dataclasses import dataclass

from interfaces._validate import check_array, check_uint
from interfaces.conventions import Header


MAX_OBJECTS = 32
OBJECT_LIST_TIMEOUT_US = 150000
OBJECT_LIST_MAX_DELTA_COUNTER = 3  # Bước counter lớn nhất theo ICD 4: floor((150 + 25) / 50), với thời gian tính bằng ms.
OBJECT_LIST_MAX_AGE_US = 250000


@dataclass(frozen=True, slots=True)
class Object:
    """Tâm vật thể trong base_link lúc đo; vận tốc so với mặt đất."""

    id: int  # Ổn định giữa các frame.
    x: float  # [m]
    y: float  # [m]
    vx: float  # [m/s]
    vy: float  # [m/s]
    heading: float  # [rad]; Góc của vector vận tốc.
    length: float  # [m]
    width: float  # [m]
    existence_probability: float  # [0..1]

    def __post_init__(self) -> None:
        check_uint(self.id, 32, "id")


@dataclass(frozen=True, slots=True)
class ObjectList:
    header: Header
    num_objects: int
    objects: tuple[Object, ...]

    def __post_init__(self) -> None:
        check_uint(self.num_objects, 8, "num_objects")
        check_array(self, "objects", MAX_OBJECTS)
