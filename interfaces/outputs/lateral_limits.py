"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 6.4."""

from __future__ import annotations

from dataclasses import dataclass

from interfaces.conventions import BasicHeader


@dataclass(frozen=True, slots=True)
class LateralLimits:
    header: BasicHeader
    v_max: float  # [m/s]
    distance: float  # [m]; Khoảng cách tới điểm có kappa_max.
    lateral_limit_reached: bool  # Cùng giá trị với LccStatus trong chu kỳ này.
