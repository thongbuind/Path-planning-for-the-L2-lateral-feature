"""Messages between simulator blocks that are not the planner.

These are outside the planner's Interface Control Document (section 1, out of scope)
and so do not belong in interfaces/.
"""

from dataclasses import dataclass

from interfaces import Side


@dataclass(frozen=True, slots=True)
class DriverSignals:
    """Driver and ESC signals read by the stand-in ADAS function (ADAS-FS 8, 12)."""

    torque_nm: float = 0.0  # left positive at the steering wheel
    indicator: Side = Side.NONE
    hands_on: bool = False
    esc_enabled: bool = True
    esc_active: bool = False


@dataclass(frozen=True, slots=True)
class SteeringRequest:
    """Lateral Controller -> stand-in EPS (Software Qualification Test Specification 4.6).

    When `active` is false the controller no longer controls. The angle is the last
    command, and the EPS hands back to the driver over 1 s.
    """

    stamp_us: int
    steering_wheel_angle_rad: float
    active: bool
