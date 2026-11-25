from dataclasses import replace

from interfaces import BasicHeader, Direction, ImuSignals, SpeedSignals, SteeringSignals

IMU_PERIOD_US = 10_000
STEERING_PERIOD_US = 10_000
SPEED_PERIOD_US = 20_000


def restamp(message, rx_us: int):
    """ChassisSignals mang stamp lúc nhận theo ICD 4."""
    return replace(message, header=replace(message.header, stamp_us=rx_us))


class ChassisSensors:
    def __init__(self) -> None:
        self._imu = 0
        self._steering = 0
        self._speed = 0

    def imu(self, now_us: int, yaw_rate: float, accel_x: float, accel_y: float) -> ImuSignals:
        msg = ImuSignals(BasicHeader(now_us, self._imu, True), yaw_rate, accel_x, accel_y)
        self._imu = (self._imu + 1) % 256
        return msg

    def steering(self, now_us: int, angle: float, rate: float) -> SteeringSignals:
        msg = SteeringSignals(BasicHeader(now_us, self._steering, True), angle, rate)
        self._steering = (self._steering + 1) % 256
        return msg

    def speed(self, now_us: int, speed: float) -> SpeedSignals:
        direction = Direction.FORWARD if speed > 0.0 else Direction.STANDSTILL
        msg = SpeedSignals(BasicHeader(now_us, self._speed, True), speed, direction)
        self._speed = (self._speed + 1) % 256
        return msg
