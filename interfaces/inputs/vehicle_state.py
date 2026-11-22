"""Sinh từ interfaces/gen.py và interfaces/schema. ICD 5.4."""

from __future__ import annotations

from dataclasses import dataclass

from interfaces.conventions import Header


VEHICLE_STATE_TIMEOUT_US = 60000
VEHICLE_STATE_MAX_DELTA_COUNTER = 4  # Bước counter lớn nhất theo ICD 4: floor((60 + 25) / 20), với thời gian tính bằng ms.
VEHICLE_STATE_MAX_AGE_US = 30000


@dataclass(frozen=True, slots=True)
class VehicleStateEstimate:
    header: Header  # stamp_us theo thời điểm ước lượng.
    lateral_velocity: float  # [m/s]; v_y tại tâm trục sau.
    lateral_velocity_variance: float  # [m^2/s^2]
    slip_angle: float  # [rad]
