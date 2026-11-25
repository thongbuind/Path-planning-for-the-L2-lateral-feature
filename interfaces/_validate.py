"""Sinh từ interfaces/gen.py và interfaces/schema.

Kiểm độ dài mảng, miền kiểu unsigned và enum. Giới hạn giá trị như bề rộng xe
hoặc confidence do bên nhận kiểm, nên test vẫn tạo được payload sai giới hạn.
"""

from enum import IntEnum


def check_uint(value: int, bits: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 2**bits:
        raise ValueError(f"{name} must be an unsigned {bits}-bit integer, got {value!r}")


def check_array(obj: object, name: str, count: int) -> None:
    value = tuple(getattr(obj, name))
    if len(value) != count:
        raise ValueError(f"{name} needs exactly {count} elements, got {len(value)}")
    object.__setattr__(obj, name, value)


def check_enum(obj: object, name: str, enum: type[IntEnum]) -> None:
    object.__setattr__(obj, name, enum(getattr(obj, name)))
