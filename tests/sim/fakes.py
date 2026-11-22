from interfaces import (
    BasicHeader,
    FrameId,
    Header,
    InitResult,
    InterventionFunction,
    InterventionPhase,
    InterventionStatus,
    LateralLimits,
    LccMode,
    LccOutputs,
    LccStatus,
    LkaElkOutputs,
    PlannerId,
    PlannerSet,
    Pose2D,
    Trajectory,
    TrajectoryPoint,
)


def straight_trajectory(t0_us: int, counter: int, planner: PlannerId = PlannerId.LCC, valid: bool = True) -> Trajectory:
    points = tuple(TrajectoryPoint(0.1 * i, Pose2D(2.0 * i, 0.0, 0.0), 20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                   for i in range(31))
    return Trajectory(Header(t0_us, counter % 256, valid, FrameId.BASE_LINK), points, 3.0, planner)


class FakeLcc:
    init_result = InitResult.OK

    def __init__(self, _config):
        self.counter = 0

    def step(self, inputs, _ego_motion):
        header = BasicHeader(inputs.t0_us, self.counter % 256, True)
        out = LccOutputs(straight_trajectory(inputs.t0_us, self.counter),
                         LccStatus(header, True, LccMode.NONE, 0.0, False, False),
                         LateralLimits(header, 500.0, 0.0, False))
        self.counter += 1
        return out


class FakeLkaElk:
    init_result = InitResult.OK

    def __init__(self, _config):
        self.counter = 0

    def step(self, inputs, _ego_motion):
        status = InterventionStatus(BasicHeader(inputs.t0_us, self.counter % 256, True), True,
                                    InterventionFunction.NONE, InterventionPhase.NONE, InterventionPhase.NONE, False)
        self.counter += 1
        return LkaElkOutputs(intervention_status=status)


def planner_set(lka_elk=FakeLkaElk, lcc=FakeLcc):
    return lambda config: PlannerSet(lcc(config), lka_elk(config))
