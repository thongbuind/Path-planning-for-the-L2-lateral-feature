"""Python interface dataclasses <-> ctypes structs, driven by pp_ctypes.FIELD_SPECS."""

import ctypes
from typing import Any

import interfaces
from adapters.sil import pp_ctypes


def c_class(type_name: str) -> type[ctypes.Structure]:
    return getattr(pp_ctypes, f"{type_name}C")


def py_class(type_name: str) -> type:
    return getattr(interfaces, type_name)


def to_c(obj: Any, type_name: str, target: ctypes.Structure | None = None) -> ctypes.Structure:
    """Fill a ctypes struct from a dataclass of the same interface type."""
    out = target if target is not None else c_class(type_name)()
    for name, kind, ref in pp_ctypes.FIELD_SPECS[type_name]:
        value = getattr(obj, name)
        if kind == "received":
            slot = getattr(out, name)
            slot.present = value is not None
            if value is not None:
                slot.rx_us = value.rx_us
                to_c(value.message, ref, slot.message)
        elif kind == "sent":
            setattr(out, f"{name}_sent", value is not None)
            if value is not None:
                to_c(value, ref, getattr(out, name))
        elif kind == "struct":
            to_c(value, ref, getattr(out, name))
        elif kind == "array_struct":
            array = getattr(out, name)
            for i, item in enumerate(value):
                to_c(item, ref, array[i])
        elif kind == "array_scalar" or kind == "array_enum":
            array = getattr(out, name)
            for i, item in enumerate(value):
                array[i] = int(item) if kind == "array_enum" else item
        elif kind == "enum":
            setattr(out, name, int(value))
        else:
            setattr(out, name, value)
    return out


def from_c(cobj: ctypes.Structure, type_name: str) -> Any:
    """Build a dataclass from a ctypes struct of the same interface type."""
    values = {}
    for name, kind, ref in pp_ctypes.FIELD_SPECS[type_name]:
        raw = getattr(cobj, name)
        if kind == "received":
            values[name] = (interfaces.Received(from_c(raw.message, ref), raw.rx_us)
                            if raw.present else None)
        elif kind == "sent":
            values[name] = from_c(raw, ref) if getattr(cobj, f"{name}_sent") else None
        elif kind == "struct":
            values[name] = from_c(raw, ref)
        elif kind == "array_struct":
            values[name] = tuple(from_c(item, ref) for item in raw)
        elif kind == "array_enum":
            enum = py_class(ref)
            values[name] = tuple(enum(item) for item in raw)
        elif kind == "array_scalar":
            values[name] = tuple(raw)
        elif kind == "enum":
            values[name] = py_class(ref)(raw)
        else:
            values[name] = raw
    return py_class(type_name)(**values)
