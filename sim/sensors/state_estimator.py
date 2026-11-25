"""VehicleStateEstimate lấy v_y thật tại base_link. Nhiễu được tiêm ở bước sau (SQTS 4.5)."""

from interfaces import FrameId, Header, VehicleStateEstimate

PERIOD_US = 20_000
SIGMA_VY = 0.05


class StateEstimator:
    def __init__(self) -> None:
        self._counter = 0

    def message(self, now_us: int, lateral_velocity: float, slip_angle: float) -> VehicleStateEstimate:
        msg = VehicleStateEstimate(Header(now_us, self._counter, True, FrameId.BASE_LINK),
                                   lateral_velocity, SIGMA_VY ** 2, slip_angle)
        self._counter = (self._counter + 1) % 256
        return msg
