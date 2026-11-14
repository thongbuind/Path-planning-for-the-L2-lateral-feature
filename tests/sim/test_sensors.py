"""Lane camera and ego-motion (Software Qualification Test Specification 4.5)."""

from math import cos, isclose, sin

import pytest

from interfaces import EgoMotionRequest, LineStatus, LineType, RoadEdgeType
from sim.sensors.ego_motion import EgoMotion
from sim.sensors.lane_camera import CameraPose, LaneCamera
from sim.world.road import Marking, Road, RoadEdgeSpec, RoadLayout, Segment


def test_lane_camera_on_arc_centre():
    radius = 1000.0
    road = Road([Segment("straight", 20.0), Segment("arc", 400.0, 1 / radius)], 3.5)
    s = 100.0
    x, y, heading = road.pose_at(s)
    lane = LaneCamera(road).capture(0, CameraPose(x, y, heading, s))
    l2, l1, r1, r2 = lane.lines
    assert all(line.status == LineStatus.MEASURED for line in lane.lines)
    assert isclose(l1.c0, 1.75, abs_tol=1e-3) and isclose(r1.c0, -1.75, abs_tol=1e-3)
    assert isclose(l2.c0, 5.25, abs_tol=1e-3) and isclose(r2.c0, -5.25, abs_tol=1e-3)
    assert isclose(l1.c1, 0.0, abs_tol=1e-4)
    # Parallel at +1.75 m of a left curve has radius R - 1.75.
    assert isclose(2 * l1.c2, 1 / (radius - 1.75), rel_tol=1e-2)
    assert l1.view_range_end <= 80.0 and l1.view_range_end > 79.0
    assert all(edge.status == LineStatus.LOST for edge in lane.road_edges)


def test_lane_camera_sees_offset_and_heading():
    road = Road([Segment("straight", 300.0)], 3.5)
    lane = LaneCamera(road).capture(0, CameraPose(50.0, 0.3, 0.01, 50.0))
    l1 = lane.lines[1]
    assert isclose(l1.c0, (1.75 - 0.3) / cos(0.01), abs_tol=1e-3)
    assert isclose(l1.c1, -sin(0.01) / cos(0.01), abs_tol=1e-5)


def test_lane_camera_reports_double_marking_and_measured_barrier():
    layout = RoadLayout((None, Marking(1.675, LineType.DOUBLE, True), None, None),
                        (None, RoadEdgeSpec(-1.75, RoadEdgeType.BARRIER)))
    road = Road([Segment("straight", 300.0)], 3.5, layout)
    pose = CameraPose(50.0, 0.0, 0.0, 50.0)
    measured = LaneCamera(road).capture(0, pose)
    ideal = LaneCamera(road, ideal=True).capture(0, pose)
    assert measured.lines[1].type == LineType.DOUBLE and measured.lines[1].crossable
    assert isclose(measured.lines[1].c0, 1.675, abs_tol=1e-6)
    assert measured.lines[2].status == LineStatus.LOST
    edge = measured.road_edges[1]
    assert edge.type == RoadEdgeType.BARRIER and edge.status == LineStatus.MEASURED
    assert isclose(edge.c0, -1.75, abs_tol=1e-6)
    assert edge.variance[0] > 0 and ideal.road_edges[1].variance == (0.0,) * 4


def _feed(motion: EgoMotion, v: float, r: float, until_us: int) -> None:
    for t in range(0, until_us + 1, 10_000):
        motion.on_yaw_rate(r, t)
        if t % 20_000 == 0:
            motion.on_speed(v, t)


def test_ego_motion_constant_turn():
    motion = EgoMotion()
    v, r = 25.0, 0.025
    _feed(motion, v, r, 600_000)
    out = motion.query(EgoMotionRequest(400_000, 500_000))
    assert out.valid
    assert isclose(out.dyaw, r * 0.1, rel_tol=1e-9)
    assert isclose(out.dx, v / r * sin(r * 0.1), rel_tol=1e-9)
    assert isclose(out.dy, v / r * (1 - cos(r * 0.1)), rel_tol=1e-9)


def test_ego_motion_includes_lateral_slip():
    """ICD 5.5: true motion of base_link, lateral slip included."""
    v, r, vy = 25.0, 0.025, -0.11
    motion = EgoMotion()
    _feed(motion, v, r, 600_000)
    for t in range(0, 600_001, 20_000):
        motion.on_lateral_velocity(vy, t)
    out = motion.query(EgoMotionRequest(400_000, 500_000))
    h = 0.1
    assert isclose(out.dx, (v * sin(r * h) + vy * (cos(r * h) - 1)) / r, rel_tol=1e-9)
    assert isclose(out.dy, (v * (1 - cos(r * h)) + vy * sin(r * h)) / r, rel_tol=1e-9)

    straight = EgoMotion()
    _feed(straight, v, 0.0, 600_000)
    straight.on_lateral_velocity(vy, 0)
    out = straight.query(EgoMotionRequest(400_000, 500_000))
    assert isclose(out.dy, vy * h, rel_tol=1e-9)


def test_ego_motion_rejects_unknown_past():
    assert not EgoMotion().query(EgoMotionRequest(0, 10_000)).valid   # nothing received yet
    motion = EgoMotion()
    for t in range(100_000, 200_001, 10_000):
        motion.on_yaw_rate(0.0, t)
        motion.on_speed(25.0, t)
    assert motion.query(EgoMotionRequest(120_000, 180_000)).valid
    assert not motion.query(EgoMotionRequest(50_000, 180_000)).valid  # before the first sample
    assert not motion.query(EgoMotionRequest(180_000, 120_000)).valid  # t2 before t1


def test_lane_camera_view_start_hides_the_near_road():
    road = Road([Segment("straight", 300.0)], 3.5)
    lane = LaneCamera(road, view_start_m=6.0).capture(0, CameraPose(50.0, 0.0, 0.0, 50.0))
    assert lane.lines[1].view_range_start >= 6.0
    assert lane.lines[1].c0 == pytest.approx(1.75, abs=1e-3)
