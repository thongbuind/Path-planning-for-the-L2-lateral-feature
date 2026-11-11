"""Other vehicles and the ObjectList sensor (Software Qualification Test Specification 4.5)."""

from math import isclose

import numpy as np

from interfaces import FrameId
from sim.sensors import object_sensor
from sim.sensors.object_sensor import ObjectSensor
from sim.world.road import Road, Segment
from sim.world.traffic import Traffic, TrafficSpec


def _road() -> Road:
    return Road([Segment("straight", 2000.0)], 3.5)


def test_traffic_moves_along_the_road_at_constant_offset():
    traffic = Traffic(_road(), (TrafficSpec(7, s0=80.0, d=-3.5, speed=20.0, length=12.0, width=2.5),))
    (truck,) = traffic.at(2.0)
    assert truck.id == 7 and isclose(truck.s, 120.0) and truck.d == -3.5
    assert isclose(truck.x, 120.0, abs_tol=1e-6) and isclose(truck.y, -3.5, abs_tol=1e-6)
    assert truck.length == 12.0 and truck.width == 2.5


def test_sensor_reports_truck_in_base_link():
    truck = Traffic(_road(), (TrafficSpec(1, 80.0, -3.5, 20.0, 12.0, 2.5),)).at(0.0)
    sensor = ObjectSensor(np.random.default_rng(1), noise_scale=0.0)
    xs = []
    for k in range(200):
        out = sensor.capture(k * object_sensor.PERIOD_US, (50.0, 0.0, 0.0), 25.0, truck)
        assert out.header.frame_id == FrameId.BASE_LINK and len(out.objects) == 32
        real = [o for o in out.objects[:out.num_objects] if o.id == 1]
        xs.extend((o.x, o.y, o.vx, o.width) for o in real)
    # Without noise the truck is at its true place; about 2 % of the frames miss it.
    assert all(isclose(x, 30.0, abs_tol=1e-9) and isclose(y, -3.5, abs_tol=1e-9) for x, y, _, _ in xs)
    assert all(isclose(vx, 20.0, abs_tol=1e-9) and w == 2.5 for _, _, vx, w in xs)
    assert 180 <= len(xs) <= 200


def test_sensor_range_and_noise():
    far = Traffic(_road(), (TrafficSpec(1, 400.0, 0.0, 25.0),)).at(0.0)
    sensor = ObjectSensor(np.random.default_rng(2))
    out = sensor.capture(0, (50.0, 0.0, 0.0), 25.0, far)
    assert out.num_objects == 0 or all(o.id != 1 for o in out.objects[:out.num_objects])  # beyond 150 m

    near = Traffic(_road(), (TrafficSpec(1, 100.0, -3.5, 25.0),)).at(0.0)
    ys = [o.y for k in range(2000)
          for out in [sensor.capture(k * object_sensor.PERIOD_US, (50.0, 0.0, 0.0), 25.0, near)]
          for o in out.objects[:out.num_objects] if o.id == 1]
    # Range 50 m: y sigma = 0.1 + 0.5 % of range = 0.35 m.
    assert isclose(float(np.std(ys)), 0.1 + 0.005 * np.hypot(50.0, 3.5), rel_tol=0.1)


def test_sensor_ghosts_are_rare_and_short():
    sensor = ObjectSensor(np.random.default_rng(3))
    frames = 20 * 60 * 10  # 10 minutes
    ghost_frames = sum(sensor.capture(k * object_sensor.PERIOD_US, (0.0, 0.0, 0.0), 25.0, []).num_objects > 0
                       for k in range(frames))
    # 0.05 ghosts per second living 0.2 s: about 1 % of the frames.
    assert 0.003 * frames < ghost_frames < 0.03 * frames
