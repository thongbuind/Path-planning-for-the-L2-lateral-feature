"""Chassis CAN frames by the DBC of Interface Control Document 5.3, standard library only.

Sender side (ESC, SAS, IMU ECUs): physical value -> integer by the factor (rounded, clamped
to the field; F18), 4-bit counter, qualifier, CRC. Receiver side (CAN receive layer of the
ADAS ECU platform, not the planner): CRC check and counter check, then SI units.

| Frame | Bytes 0-5 | Data ID |
|---|---|---|
| IMU_Data 0x1A0 | YawRate int16 x 0.01 deg/s; AccelX, AccelY int16 x 0.001 m/s^2 | 0x10 |
| SAS_Steering 0x1B0 | SteeringWheelAngle int16 x 0.1 deg; SteeringWheelSpeed int16 x 0.1 deg/s | 0x11 |
| ESC_Speed 0x1C0 | VehicleSpeed uint16 x 0.01 km/h; byte 2 bits 0-1 Direction | 0x12 |

Byte 6: bits 0-3 counter, bits 4-5 qualifier {VALID, INIT, DEGRADED, FAULT}. Byte 7: CRC-8
SAE J1850 (polynomial 0x1D, start 0xFF, final XOR 0xFF) over the Data ID (low byte, then a
zero high byte) and bytes 0-6, as in AUTOSAR E2E Profile 1. Intel byte order; signs follow
base_link (yaw rate, a_y, steering angle positive to the left).
"""

import struct
from dataclasses import dataclass, replace
from math import pi

from interfaces import BasicHeader, Direction, ImuSignals, SpeedSignals, SteeringSignals

IMU_ID, STEERING_ID, SPEED_ID = 0x1A0, 0x1B0, 0x1C0
DATA_ID = {IMU_ID: 0x10, STEERING_ID: 0x11, SPEED_ID: 0x12}
VALID, INIT, DEGRADED, FAULT = 0, 1, 2, 3
DEG = pi / 180.0
KMH = 1 / 3.6
_I16, _U16 = (-32768, 32767), (0, 65535)


def crc8_j1850(data: bytes) -> int:
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1D) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc ^ 0xFF


def _crc(can_id: int, payload7: bytes) -> int:
    return crc8_j1850(bytes((DATA_ID[can_id] & 0xFF, 0)) + payload7)


def _raw(value: float, factor: float, limits: tuple[int, int]) -> int:
    return max(limits[0], min(limits[1], round(value / factor)))


@dataclass(frozen=True, slots=True)
class CanFrame:
    can_id: int
    data: bytes  # 8 bytes

    @property
    def counter(self) -> int:
        return self.data[6] & 0x0F

    @property
    def qualifier(self) -> int:
        return (self.data[6] >> 4) & 0x03

    def crc_ok(self) -> bool:
        return self.data[7] == _crc(self.can_id, self.data[:7])

    def with_byte6(self, counter: int, qualifier: int) -> "CanFrame":
        """The sender changes counter or qualifier: CRC computed again."""
        head = self.data[:6] + bytes(((qualifier & 0x03) << 4 | (counter & 0x0F),))
        return replace(self, data=head + bytes((_crc(self.can_id, head),)))

    def with_bad_crc(self) -> "CanFrame":
        return replace(self, data=self.data[:7] + bytes((self.data[7] ^ 0xFF,)))


def _frame(can_id: int, payload6: bytes, counter: int, qualifier: int) -> CanFrame:
    head = payload6 + bytes(((qualifier & 0x03) << 4 | (counter & 0x0F),))
    return CanFrame(can_id, head + bytes((_crc(can_id, head),)))


class CanSender:
    """One sending ECU per frame: counter 0-15 per frame ID."""

    def __init__(self) -> None:
        self._counter = {IMU_ID: 0, STEERING_ID: 0, SPEED_ID: 0}

    def _next(self, can_id: int) -> int:
        c = self._counter[can_id]
        self._counter[can_id] = (c + 1) % 16
        return c

    def imu(self, yaw_rate_rps: float, accel_x: float, accel_y: float) -> CanFrame:
        payload = struct.pack("<hhh", _raw(yaw_rate_rps / DEG, 0.01, _I16), _raw(accel_x, 0.001, _I16),
                              _raw(accel_y, 0.001, _I16))
        return _frame(IMU_ID, payload, self._next(IMU_ID), VALID)

    def steering(self, angle_rad: float, rate_rps: float) -> CanFrame:
        payload = struct.pack("<hhxx", _raw(angle_rad / DEG, 0.1, _I16), _raw(rate_rps / DEG, 0.1, _I16))
        return _frame(STEERING_ID, payload, self._next(STEERING_ID), VALID)

    def speed(self, speed_mps: float) -> CanFrame:
        direction = Direction.FORWARD if speed_mps > 0.0 else Direction.STANDSTILL
        payload = struct.pack("<HBxxx", _raw(speed_mps / KMH, 0.01, _U16), int(direction) & 0x03)
        return _frame(SPEED_ID, payload, self._next(SPEED_ID), VALID)


class CanReceiver:
    """CAN receive layer (Interface Control Document 5.3, "Hợp lệ"): a frame with a wrong CRC
    or a repeated counter is dropped (None); a counter jump is counted as lost frames.
    `valid` = qualifier VALID. The message is stamped with the receive time and gets its own
    8-bit counter, one per accepted frame (Interface Control Document 4)."""

    def __init__(self) -> None:
        self._last: dict[int, int] = {}
        self._out_counter: dict[int, int] = {IMU_ID: 0, STEERING_ID: 0, SPEED_ID: 0}
        self.lost = {IMU_ID: 0, STEERING_ID: 0, SPEED_ID: 0}
        self.dropped = {IMU_ID: 0, STEERING_ID: 0, SPEED_ID: 0}

    def decode(self, frame: CanFrame, rx_us: int):
        cid = frame.can_id
        if not frame.crc_ok() or self._last.get(cid) == frame.counter:
            self.dropped[cid] += 1
            return None
        if cid in self._last:
            self.lost[cid] += (frame.counter - self._last[cid] - 1) % 16
        self._last[cid] = frame.counter
        counter = self._out_counter[cid]
        self._out_counter[cid] = (counter + 1) % 256
        header = BasicHeader(rx_us, counter, frame.qualifier == VALID)
        d = frame.data
        if cid == IMU_ID:
            yaw, ax, ay = struct.unpack_from("<hhh", d)
            return ImuSignals(header, yaw * 0.01 * DEG, ax * 0.001, ay * 0.001)
        if cid == STEERING_ID:
            angle, rate = struct.unpack_from("<hh", d)
            return SteeringSignals(header, angle * 0.1 * DEG, rate * 0.1 * DEG)
        speed, direction = struct.unpack_from("<HB", d)
        return SpeedSignals(header, speed * 0.01 * KMH, Direction(direction & 0x03))
