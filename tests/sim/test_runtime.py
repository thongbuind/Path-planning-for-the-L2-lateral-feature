"""Scheduler, channel, seeds (Software Qualification Test Specification 4.2) and the stand-in EPS (4.6)."""

from math import isclose

from sim.messages import SteeringRequest
from sim.runtime.channel import Channel
from sim.runtime.scheduler import Scheduler
from sim.runtime.seeds import random_phase_us, spawn_streams
from sim.stand_ins.eps import Eps
from sim.vehicle.profiles import PROFILES


def test_order_within_a_step_and_periods():
    sched = Scheduler()
    events = []
    channel = Channel("c", latency_us=0)
    channel.subscribers.append(lambda m, rx: events.append(("deliver", rx, m)))
    sched.add_physics(lambda now, dt: events.append(("physics", now)))
    sched.add_sensor("s", 2_000, lambda now: (events.append(("sensor", now)), channel.publish("m", now)))
    sched.add_channel(channel)
    sched.add_block("late", 2_000, lambda now: events.append(("late", now)), priority=5)
    sched.add_block("early", 2_000, lambda now: events.append(("early", now)), priority=1)
    sched.run_until(2_000)
    assert events == [("physics", 1000), ("physics", 2000), ("sensor", 2000),
                      ("deliver", 2000, "m"), ("early", 2000), ("late", 2000)]


def test_channel_latency_and_newest():
    channel = Channel("c", latency_us=5_000)
    channel.publish("a", 0)
    channel.publish("b", 1_000)
    channel.deliver(4_000)
    assert channel.latest is None
    channel.deliver(6_000)
    assert channel.latest.message == "b" and channel.latest.rx_us == 6_000


def test_seeds_are_reproducible():
    a, b = spawn_streams(7), spawn_streams(7)
    assert [random_phase_us(a["phases"], 25_000, 1_000) for _ in range(5)] == \
           [random_phase_us(b["phases"], 25_000, 1_000) for _ in range(5)]


def test_eps_delay_lag_and_handover():
    cfg = PROFILES["VP-0"].vehicle_config()
    eps = Eps(cfg)
    eps.on_request(SteeringRequest(0, 0.15, True), 0)
    for t in range(1_000, 50_000, 1_000):
        eps.step(t, 1e-3)
    assert eps.angle == 0.0                                  # pure delay 50 ms
    for t in range(50_000, 1_050_000, 1_000):
        eps.step(t, 1e-3)
    assert isclose(eps.angle, 0.15, rel_tol=1e-3)            # tau 0.1 s, settled after 1 s
    eps.on_request(SteeringRequest(1_050_000, 0.15, False), 1_050_000)
    for t in range(1_051_000, 3_200_000, 1_000):
        delta = eps.step(t, 1e-3)
    assert isclose(eps.angle, 0.0, abs_tol=1e-3)             # back to the driver (0) within 1 s
    assert isclose(delta, eps.angle / cfg.steering_ratio)
