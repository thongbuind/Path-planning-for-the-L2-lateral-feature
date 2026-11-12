"""Timing and integrity fault mechanisms (Software Qualification Test Specification 4.2, 4.3,
4.5, 6: F05, F07, F08, F10 to F21)."""

import numpy as np
import pytest

import interfaces as I
from sim.can.frames import CanReceiver, CanSender, crc8_j1850
from sim.faults.channel import ChannelFault, ChannelFaultInjector, equivalent
from sim.faults.ego_motion import EgoMotionFault, EgoMotionFaults
from sim.faults.lane import LaneFault, LaneFaultInjector
from sim.faults.sensor import SensorErrors, SensorFault
from sim.runtime.channel import Channel
from sim.runtime.clock import SYNC_PERIOD_US, EcuClock, clocks


def _msg(k):
    return I.ImuSignals(I.BasicHeader(k * 10_000, k % 256, True), 0.0, 0.0, 0.0)


def _deliver_all(channel, n, period_us=10_000):
    got = []
    channel.subscribers.append(lambda m, rx: got.append((m.header.counter, rx, m.header.valid, m.header.stamp_us)))
    for k in range(n):
        channel.publish(_msg(k), k * period_us)
        channel.deliver(k * period_us + 500)
    channel.deliver(10 ** 9)
    return got


def test_drop_burst_stop_pick_messages_by_index():
    c = lambda f: _deliver_all(Channel("imu", faults=ChannelFaultInjector((f,))), 20)
    assert [m[0] for m in c(ChannelFault("drop", "imu", every=5))] == [k for k in range(20) if k % 5]
    assert [m[0] for m in c(ChannelFault("burst", "imu", every=10, count=2))] == [k for k in range(20) if k % 10 >= 2]
    assert [m[0] for m in c(ChannelFault("stop", "imu", start_s=0.05, duration_s=0.05))] == \
        [k for k in range(20) if not 5 <= k < 10]


def test_late_message_arrives_after_a_newer_one():
    got = _deliver_all(Channel("imu", latency_us=1_000, faults=ChannelFaultInjector(
        (ChannelFault("late", "imu", every=4, value=25.0),))), 9)
    order = [m[0] for m in got]
    assert order.index(0) > order.index(1) and sorted(order) == list(range(9))


def test_counter_faults_and_their_reference_twins():
    repeat = ChannelFaultInjector((ChannelFault("counter_repeat", "imu", every=3, value=2.0),))
    got = _deliver_all(Channel("imu", faults=repeat), 6)
    assert [m[0] for m in got] == [0, 0, 1, 2, 3, 3, 4, 5]
    assert equivalent(repeat.faults[0], []) is None  # PP-SWR-129: like no fault
    stuck = ChannelFaultInjector((ChannelFault("counter_stuck", "imu", start_s=0.02, duration_s=0.03),))
    got = _deliver_all(Channel("imu", faults=stuck), 6)
    assert [m[0] for m in got] == [0, 1, 1, 1, 1, 5]
    twin = equivalent(stuck.faults[0], stuck.fault_hits()[0])
    assert twin.kind == "drop_listed" and twin.indices == (2, 3, 4)  # PP-SWR-130: loss of those messages


def test_future_stamp_and_invalid():
    got = _deliver_all(Channel("imu", faults=ChannelFaultInjector(
        (ChannelFault("future_stamp", "imu", value=15.0, count=1),))), 3)
    assert [m[3] for m in got] == [15_000, 10_000, 20_000]
    got = _deliver_all(Channel("imu", faults=ChannelFaultInjector((ChannelFault("invalid", "imu", duration_s=0.015),))), 3)
    assert [m[2] for m in got] == [False, False, True]


def test_can_frames_round_by_the_dbc_and_the_receiver_checks_crc_and_counter():
    assert crc8_j1850(b"123456789") == 0x4B  # SAE J1850 check value
    tx, rx = CanSender(), CanReceiver()
    msg = rx.decode(tx.imu(0.123456, 0.0, 1.23456), 1000)
    assert msg.yaw_rate_rps == pytest.approx(round(0.123456 / (np.pi / 180) / 0.01) * 0.01 * np.pi / 180)
    assert msg.accel_y_mps2 == pytest.approx(1.235) and msg.header.valid
    frame = tx.imu(0.0, 0.0, 0.0)
    assert rx.decode(frame.with_bad_crc(), 2000) is None  # F17: dropped
    assert rx.decode(frame, 3000) is not None and rx.decode(frame, 4000) is None  # repeated counter: dropped
    assert rx.decode(tx.imu(0, 0, 0).with_byte6(frame.counter + 3, 3), 5000).header.valid is False  # FAULT
    assert rx.lost[0x1A0] == 2


def test_ecu_clock_drifts_between_synchronisations_and_without_them():
    c = EcuClock(drift_ppm=100.0, residual_us=50.0, seed=1)
    for t in range(0, 2_000_000, 7_919):
        assert abs(c.local(t) - t) <= 50 + 100e-6 * SYNC_PERIOD_US + 1
    lost = EcuClock(drift_ppm=100.0, residual_us=50.0, seed=1, sync_loss=((1_000_000, 11_000_000),))
    assert lost.local(10_999_999) - 10_999_999 == pytest.approx(1000, abs=60)  # 100 ppm x 10 s
    assert abs(lost.to_global(lost.local(5_000_000)) - 5_000_000) <= 1
    assert all(k.ideal for k in clocks(1, False, ()).values())


def test_sensor_errors_and_ego_motion_faults():
    errors = SensorErrors((SensorFault("bias", "yaw_rate", 0.01, start_s=1.0),
                           SensorFault("noise", "speed", 0.02)),
                          {"yaw_rate": np.random.default_rng(1), "speed": np.random.default_rng(2)})
    assert errors.apply("yaw_rate", 0.0, 500_000) == 0.0 and errors.apply("yaw_rate", 0.0, 1_500_000) == 0.01
    assert np.std([errors.apply("speed", 20.0, t) for t in range(2000)]) == pytest.approx(0.02, rel=0.1)
    hit = [EgoMotionFaults((EgoMotionFault(kind, start_s=0.1, duration_s=0.1),)) for kind in ("once", "continuous", "alternate")]
    pattern = [[f.invalid(k * 25_000) for k in range(12)] for f in hit]
    assert pattern[0].count(True) == 1 and pattern[1].count(True) == 4 and pattern[2].count(True) == 2


def test_lose_all_predicts_then_loses_every_boundary():
    line = I.LaneLine(1.75, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 80.0, 0.9, I.LineType.DASHED, True, I.LineStatus.MEASURED, 0.0)
    edge = I.RoadEdge(7.0, 0.0, 0.0, 0.0, (0.0,) * 4, 0.0, 80.0, 0.9, I.RoadEdgeType.CURB, I.LineStatus.MEASURED, 0.0)
    injector = LaneFaultInjector((LaneFault("lose_all", start_s=1.0, value=0.5),), np.random.default_rng(1))

    def at(t_us):
        lane = I.LaneModel(I.Header(t_us, 0, True, I.FrameId.BASE_LINK), (line,) * 4, (edge,) * 2, 3.5,
                           I.LaneWidthSource.MEASURED, I.Side.NONE)
        return injector.apply(lane)

    assert {b.status for b in (*at(1_200_000).lines, *at(1_200_000).road_edges)} == {I.LineStatus.PREDICTED}
    assert at(1_200_000).lines[0].predicted_duration == pytest.approx(0.2)
    assert {b.status for b in (*at(1_600_000).lines, *at(1_600_000).road_edges)} == {I.LineStatus.LOST}
