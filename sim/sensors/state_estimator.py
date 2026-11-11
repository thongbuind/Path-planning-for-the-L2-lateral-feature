"""VehicleStateEstimate (Software Qualification Test Specification 4.5; Interface Control
Document 5.4): true v_y at base_link. Noise (sigma 0.05 m/s) is fault injection later;
the reported variance is that sigma.
"""

from interfaces import FrameId, Header, VehicleStateEstimate

PERIOD_US = 20_000  # 50 Hz (Interface Control Document 5.4)
SIGMA_VY = 0.05  # [m/s] 4.5


class StateEstimator:
    def __init__(self) -> None:
        self._counter = 0

    def message(self, now_us: int, lateral_velocity: float, slip_angle: float) -> VehicleStateEstimate:
        msg = VehicleStateEstimate(Header(now_us, self._counter, True, FrameId.BASE_LINK),
                                   lateral_velocity, SIGMA_VY ** 2, slip_angle)
        self._counter = (self._counter + 1) % 256
        return msg
