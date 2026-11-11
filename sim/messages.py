"""Messages between simulator blocks that are not the planner.

These are outside the planner's Interface Control Document (section 1, out of scope)
and so do not belong in interfaces/.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SteeringRequest:
    """Lateral Controller -> stand-in EPS (Software Qualification Test Specification 4.6).

    When `active` is false the controller no longer controls. The angle is the last
    command, and the EPS hands back to the driver over 1 s.
    """

    stamp_us: int
    steering_wheel_angle_rad: float
    active: bool
