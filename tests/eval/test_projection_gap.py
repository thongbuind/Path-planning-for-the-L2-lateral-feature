"""PP-PR-080: sau khoảng không chấm, bên chấm không được chiếu lên đường bằng gợi ý s cũ."""

from eval.metrics import evaluate
from interfaces import (
    BasicHeader, FrameId, Header, InterventionPhase, LateralLimits, PlannerId, Pose2D, Trajectory,
    TrajectoryPoint,
)
from sim.harness import PlannerCycle, RunLog
from sim.scenario import Scenario
from sim.stand_ins.arbitrator import ActiveFunction, SystemStatus
from sim.world.road import Road, Segment

SPEED = 20.0
KAPPA = 0.004  # a_y cần 1,6 m/s², dưới aysmax nên PP-SWR-051 được chấm.
GAP = (1_000_000, 4_000_000)  # Path không hợp lệ 3 s, xe đi 60 m, quá cửa sổ tìm 20 m.


def _log(duration_us=5_000_000):
    segments = (Segment("straight", 5.0), Segment("arc", 400.0, KAPPA))
    scenario = Scenario("synthetic", segments, 3.5, SPEED, hwa_request_s=None)
    road = Road(list(segments), 3.5)
    log = RunLog(scenario, 1, road, 1.9, 2.9, .61, 6.0, 15.0, 0)
    for t in range(0, duration_us + 1, 1_000):
        s = 10.0 + SPEED * t * 1e-6
        log.t_us.append(t)
        log.rear.append(road.pose_at(s))
        log.front.append(road.pose_at(s + 2.9))
        log.rear_v_y.append(0.0)
        log.yaw_rate.append(SPEED * KAPPA)
        log.speed.append(SPEED)
        log.a_y.append(SPEED ** 2 * KAPPA)
        log.eps_controlling.append(True)
    for n, t in enumerate(range(0, duration_us + 1, 25_000)):
        valid = not GAP[0] <= t < GAP[1]
        hdr = BasicHeader(t, n % 256, True)
        status = SystemStatus(hdr, valid, ActiveFunction.LCC if valid else ActiveFunction.NONE,
                              InterventionPhase.NONE, InterventionPhase.NONE, False, False)
        points = tuple(TrajectoryPoint(i / 10, Pose2D(2.0 * i, 0.0, 0.0), SPEED, 0.0, 0.0,
                                       SPEED ** 2 * KAPPA, KAPPA, 0.0, 0.0) for i in range(31))
        trajectory = Trajectory(Header(t, n % 256, valid, FrameId.BASE_LINK), points, 3.0, PlannerId.LCC)
        log.cycles.append(PlannerCycle(t, trajectory, status, LateralLimits(hdr, 30.0, 0.0, False), 0))
    return log


def test_dlc_after_gap_matches_centred_vehicle():
    result = evaluate(_log())
    dlc = next(c for c in result.criteria if c.id == "PP-SWR-051")
    # Xe ở tâm làn suốt lượt: DLC = (3,5 − 1,9) / 2 = 0,8 m, kể cả sau khoảng mất path.
    assert dlc.applicable
    assert abs(dlc.value - 0.8) < 0.02
    assert result.info["vehicle_offset_max_m"] < 0.02
