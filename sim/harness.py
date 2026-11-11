"""Wires the test environment around any planner that meets interfaces.Planner.

Deterministic single-process mode (Software Qualification Test Specification 4.1),
closed loop: Trajectory -> stand-in Lateral Controller -> stand-in EPS -> vehicle model.

Blocks and rates (4.1, 4.2):

| Block | Period | Output |
|---|---|---|
| Lane camera | 50 ms | LaneModel, delivered after 100 ms |
| IMU, steering, speed | 10, 10, 20 ms | Chassis signals, stamped at receive |
| State estimator | 20 ms | VehicleStateEstimate |
| Scripted ADAS function block | 25 ms | FunctionRequests |
| Longitudinal block: scripted, or stand-in ACC (4.7) | 25 ms | LongitudinalPlan |
| Planner | 25 ms | Trajectory, PathStatus |
| Lateral Controller | 10 ms | SteeringRequest |

Each block starts at a random phase from the seed. The planner is given from outside;
only eval/ knows which planner it is.
"""

import time
from dataclasses import dataclass, field
from math import cos, sin, tan

from interfaces import (
    PLANNER_PERIOD_US,
    ActiveFunction,
    LateralLimits,
    LineStatus,
    PathStatus,
    PlannerFactory,
    PlannerInputs,
    Trajectory,
)
from sim.faults.lane import LaneFaultInjector
from sim.messages import SteeringRequest
from sim.runtime.channel import Channel
from sim.runtime.scheduler import STEP_US, Scheduler
from sim.runtime.seeds import random_phase_us, spawn_streams
from sim.scenario import Scenario
from sim.sensors import chassis, lane_camera, state_estimator
from sim.sensors.chassis import ChassisSensors, restamp
from sim.sensors.ego_motion import EgoMotion
from sim.sensors.lane_camera import CameraPose, LaneCamera
from sim.sensors import object_sensor
from sim.sensors.object_sensor import ObjectSensor
from sim.world.traffic import Traffic
from sim.sensors.state_estimator import StateEstimator
from sim.stand_ins import scripted
from sim.stand_ins.eps import Eps
from sim.stand_ins.lateral_controller import CONTROLLER_PERIOD_US, EgoState, LateralController
from sim.stand_ins.acc import Acc, LongitudinalActuator
from sim.stand_ins.scripted import ScriptedFunctionRequests, ScriptedLongitudinal
from sim.vehicle.bicycle import Bicycle, BicycleState, steady_cornering
from sim.vehicle.profiles import PROFILES
from sim.world.road import Road

TRUTH_PERIOD_US = 1_000  # Ground truth logged every step

# Fixed block priority within one step (4.2): producers before consumers.
PRIORITY = {"function_requests": 0, "longitudinal": 1, "planner": 2, "controller": 3}


@dataclass
class PlannerCycle:
    t0_us: int
    trajectory: Trajectory | None
    path_status: PathStatus | None
    lateral_limits: LateralLimits | None
    compute_ns: int  # Wall clock of planner.step, adapter included
    # Lane model given to the planner: capture stamp and observed range end of L1, R1 [m]
    lane_view: tuple[int, float] | None = None


@dataclass
class RunLog:
    """Everything eval/ needs; ground truth is the simulator's, never the planner's."""

    scenario: Scenario
    seed: int
    road: Road
    vehicle_width: float
    wheelbase: float
    max_wheel_angle: float
    max_steering_wheel_rate: float
    steering_ratio: float
    init_result: int
    # Ground truth per step: time, base_link pose, front axle pose, v_x, a_y, wheel angle
    t_us: list[int] = field(default_factory=list)
    rear: list[tuple[float, float, float]] = field(default_factory=list)
    front: list[tuple[float, float, float]] = field(default_factory=list)
    a_y: list[float] = field(default_factory=list)
    speed: list[float] = field(default_factory=list)  # [m/s] longitudinal
    wheel_angle: list[float] = field(default_factory=list)
    eps_controlling: list[bool] = field(default_factory=list)
    cycles: list[PlannerCycle] = field(default_factory=list)


class Harness:
    def __init__(self, scenario: Scenario, planner_factory: PlannerFactory, seed: int) -> None:
        self.scenario = scenario
        self.seed = seed
        self.rngs = spawn_streams(seed)
        self.road = Road(list(scenario.segments), scenario.lane_width)
        self.profile = PROFILES[scenario.profile]
        self.vehicle_config = self.profile.vehicle_config()
        self.planner = planner_factory(self.vehicle_config)

        # Car on the road, rear axle at start_s, aligned with the lane plus the given offset.
        # In a curve the fake driver is already steering it: steady-state cornering.
        x, y, heading = self.road.pose_at(scenario.start_s, scenario.start_offset_m)
        psi = heading + scenario.start_heading_rad
        lr = self.profile.lr
        kappa0 = self.road.project(x, y, scenario.start_s).curvature
        v_y0, r0, delta0 = steady_cornering(self.profile, scenario.speed_mps, kappa0)
        self.vehicle = Bicycle(self.profile, BicycleState(x + lr * cos(psi), y + lr * sin(psi),
                                                          psi, v_y0, r0))
        self.vehicle.v_x = scenario.speed_mps
        self._s_hint = scenario.start_s

        self.eps = Eps(self.vehicle_config)
        self.eps.hold_driver_angle(delta0 * self.vehicle_config.steering_ratio)
        # S2: the car keeps the start offset and heading until HWA starts driving.
        self._holding = scenario.hold_until_hwa
        self._hold_s = scenario.start_s
        if self._holding:
            self._place_held()
        self.controller = LateralController(self.vehicle_config, self.profile.understeer_gradient)
        self.camera = LaneCamera(self.road, view_end_m=scenario.camera_view_m)
        self.lane_faults = LaneFaultInjector(scenario.lane_faults, self.rngs["lane_camera"])
        self.traffic = Traffic(self.road, scenario.traffic)
        self.objects = ObjectSensor(self.rngs["perception"])
        self.chassis = ChassisSensors()
        self.estimator = StateEstimator()
        self.ego_motion = EgoMotion()
        self.function_requests = ScriptedFunctionRequests(round(scenario.hwa_request_s * 1e6))
        # Longitudinal side: scenario speed held ('off'), or the stand-in ACC that ignores
        # ('ignore_limits', R79 Annex 8 3.2.2 and the S14 second run) or reads LateralLimits.
        self.longitudinal = ScriptedLongitudinal(scenario.speed_mps)
        self.acc = (Acc(scenario.speed_mps, read_limits=scenario.acc == "on")
                    if scenario.acc != "off" else None)
        self.long_act = LongitudinalActuator(scenario.speed_mps)

        self.ch = {
            "lane_model": Channel("lane_model", latency_us=lane_camera.LATENCY_US),
            "object_list": Channel("object_list", latency_us=object_sensor.LATENCY_US),
            "imu": Channel("imu", on_deliver=restamp),
            "steering": Channel("steering", on_deliver=restamp),
            "speed": Channel("speed", on_deliver=restamp),
            "vehicle_state": Channel("vehicle_state"),
            "function_requests": Channel("function_requests"),
            "longitudinal_plan": Channel("longitudinal_plan"),
            "trajectory": Channel("trajectory"),
            "lateral_limits": Channel("lateral_limits"),
            "path_status": Channel("path_status"),
            "steering_request": Channel("steering_request"),
        }
        self.ch["imu"].subscribers.append(lambda m, rx: self.ego_motion.on_yaw_rate(m.yaw_rate_rps, rx))
        self.ch["speed"].subscribers.append(lambda m, rx: self.ego_motion.on_speed(m.speed_mps, rx))
        self.ch["vehicle_state"].subscribers.append(
            lambda m, rx: self.ego_motion.on_lateral_velocity(m.lateral_velocity, rx))
        self.ch["trajectory"].subscribers.append(self.controller.on_trajectory)
        self.ch["path_status"].subscribers.append(self.controller.on_path_status)
        self.ch["steering_request"].subscribers.append(self.eps.on_request)
        if self.acc is not None:
            self.ch["lateral_limits"].subscribers.append(self.acc.on_lateral_limits)
        self.ch["path_status"].subscribers.append(self._release_on_hwa)

        self.log = RunLog(
            scenario=scenario, seed=seed, road=self.road,
            vehicle_width=self.vehicle_config.vehicle_width,
            wheelbase=self.vehicle_config.wheelbase,
            max_wheel_angle=self.vehicle_config.max_wheel_angle,
            max_steering_wheel_rate=self.vehicle_config.max_steering_wheel_rate,
            steering_ratio=self.vehicle_config.steering_ratio,
            init_result=int(self.planner.init_result),
        )
        self.scheduler = self._build_scheduler()

    # ---- wiring -------------------------------------------------------------------------

    def _build_scheduler(self) -> Scheduler:
        sched = Scheduler(STEP_US)
        phases = self.rngs["phases"]

        def phase(period_us: int) -> int:
            return random_phase_us(phases, period_us, STEP_US)

        sched.add_physics(self._physics)
        sched.add_sensor("lane_camera", lane_camera.PERIOD_US, self._camera, phase(lane_camera.PERIOD_US))
        sched.add_sensor("imu", chassis.IMU_PERIOD_US, self._imu, phase(chassis.IMU_PERIOD_US))
        if self.scenario.traffic:
            sched.add_sensor("object_sensor", object_sensor.PERIOD_US, self._objects,
                             phase(object_sensor.PERIOD_US))
        sched.add_sensor("steering", chassis.STEERING_PERIOD_US, self._steering,
                         phase(chassis.STEERING_PERIOD_US))
        sched.add_sensor("speed", chassis.SPEED_PERIOD_US, self._speed, phase(chassis.SPEED_PERIOD_US))
        sched.add_sensor("state_estimator", state_estimator.PERIOD_US, self._state,
                         phase(state_estimator.PERIOD_US))
        for channel in self.ch.values():
            sched.add_channel(channel)
        sched.add_block("function_requests", scripted.PERIOD_US, self._function_requests,
                        PRIORITY["function_requests"], phase(scripted.PERIOD_US))
        sched.add_block("longitudinal", scripted.PERIOD_US, self._longitudinal,
                        PRIORITY["longitudinal"], phase(scripted.PERIOD_US))
        sched.add_block("planner", PLANNER_PERIOD_US, self._planner, PRIORITY["planner"],
                        phase(PLANNER_PERIOD_US))
        sched.add_block("controller", CONTROLLER_PERIOD_US, self._controller, PRIORITY["controller"],
                        phase(CONTROLLER_PERIOD_US))
        return sched

    # ---- physics and sensors ------------------------------------------------------------

    def _place_held(self) -> None:
        """Car at the start offset and heading at _hold_s, sliding along the lane: body v_y
        cancels the heading so sensors and ego-motion see motion parallel to the lane."""
        sc, p = self.scenario, self.profile
        x, y, heading = self.road.pose_at(self._hold_s, sc.start_offset_m)
        psi = heading + sc.start_heading_rad
        kappa = self.road.project(x, y, self._hold_s).curvature
        v_y, r, delta = steady_cornering(p, sc.speed_mps, kappa)
        self._held_v_y = v_y
        self.vehicle.state = BicycleState(x + p.lr * cos(psi), y + p.lr * sin(psi), psi,
                                          v_y - sc.speed_mps * tan(sc.start_heading_rad), r)
        self.eps.hold_driver_angle(delta * self.vehicle_config.steering_ratio)

    def _release_on_hwa(self, status: PathStatus, _rx_us: int) -> None:
        if self._holding and status.path_valid and status.active_function == ActiveFunction.HWA:
            self._holding = False
            st = self.vehicle.state
            self.vehicle.state = BicycleState(st.x, st.y, st.psi, self._held_v_y, st.r)

    def _physics(self, now_us: int, dt: float) -> None:
        if self._holding:
            self._hold_s += self.scenario.speed_mps * dt
            self._place_held()
        delta = self.eps.step(now_us, dt)
        if not self._holding:
            speed = self.long_act.step(now_us, dt) if self.acc is not None else self.scenario.speed_mps
            self.vehicle.step(dt, delta, speed)
        rear = self.vehicle.rear_axle()
        self._s_hint = self.road.project(rear[0], rear[1], self._s_hint).s
        if now_us % TRUTH_PERIOD_US == 0:
            log = self.log
            log.t_us.append(now_us)
            log.rear.append(rear)
            log.front.append(self.vehicle.front_axle())
            log.a_y.append(self.vehicle.a_y)
            log.speed.append(self.vehicle.v_x)
            log.wheel_angle.append(delta)
            log.eps_controlling.append(self.eps.controlling)

    def _camera(self, now_us: int) -> None:
        x, y, yaw = self.vehicle.rear_axle()
        msg = self.camera.capture(now_us, CameraPose(x, y, yaw, self._s_hint))
        self.ch["lane_model"].publish(self.lane_faults.apply(msg), now_us)

    def _objects(self, now_us: int) -> None:
        msg = self.objects.capture(now_us, self.vehicle.rear_axle(), self.vehicle.v_x,
                                   self.traffic.at(now_us * 1e-6))
        self.ch["object_list"].publish(msg, now_us)

    def _imu(self, now_us: int) -> None:
        st = self.vehicle.state
        self.ch["imu"].publish(self.chassis.imu(now_us, st.r, 0.0, self.vehicle.a_y), now_us)

    def _steering(self, now_us: int) -> None:
        self.ch["steering"].publish(self.chassis.steering(now_us, self.eps.angle, self.eps.rate), now_us)

    def _speed(self, now_us: int) -> None:
        self.ch["speed"].publish(self.chassis.speed(now_us, self.vehicle.v_x), now_us)

    def _state(self, now_us: int) -> None:
        msg = self.estimator.message(now_us, self.vehicle.rear_axle_lateral_velocity(),
                                     self.vehicle.slip_angle())
        self.ch["vehicle_state"].publish(msg, now_us)

    # ---- blocks -------------------------------------------------------------------------

    def _function_requests(self, now_us: int) -> None:
        self.ch["function_requests"].publish(self.function_requests.message(now_us), now_us)

    def _longitudinal(self, now_us: int) -> None:
        if self.acc is None:
            msg = self.longitudinal.message(now_us)
        else:
            msg = self.acc.step(now_us, self.vehicle.v_x)
            self.long_act.command(now_us, self.acc.command)
        self.ch["longitudinal_plan"].publish(msg, now_us)

    def _planner(self, now_us: int) -> None:
        ch = self.ch
        inputs = PlannerInputs(
            t0_us=now_us,
            lane_model=ch["lane_model"].latest,
            object_list=ch["object_list"].latest,
            imu=ch["imu"].latest,
            steering=ch["steering"].latest,
            speed=ch["speed"].latest,
            vehicle_state=ch["vehicle_state"].latest,
            function_requests=ch["function_requests"].latest,
            longitudinal_plan=ch["longitudinal_plan"].latest,
        )
        start = time.perf_counter_ns()
        out = self.planner.step(inputs, self.ego_motion.query)
        compute_ns = time.perf_counter_ns() - start
        if out.trajectory is not None:
            ch["trajectory"].publish(out.trajectory, now_us)
        if out.path_status is not None:
            ch["path_status"].publish(out.path_status, now_us)
        if out.lateral_limits is not None:
            ch["lateral_limits"].publish(out.lateral_limits, now_us)
        lane = inputs.lane_model
        lane_view = None
        if lane is not None:
            ends = [line.view_range_end for line in lane.message.lines[1:3]
                    if line.status != LineStatus.LOST]
            lane_view = (lane.message.header.stamp_us, min(ends)) if ends else None
        self.log.cycles.append(PlannerCycle(now_us, out.trajectory, out.path_status,
                                            out.lateral_limits, compute_ns, lane_view))

    def _controller(self, now_us: int) -> None:
        speed = self.ch["speed"].latest
        imu = self.ch["imu"].latest
        state = self.ch["vehicle_state"].latest
        if speed is None or imu is None:
            return
        ego = EgoState(speed.message.speed_mps,
                       state.message.lateral_velocity if state is not None else 0.0,
                       imu.message.yaw_rate_rps)
        request: SteeringRequest = self.controller.step(now_us, ego, self.ego_motion.query)
        self.ch["steering_request"].publish(request, now_us)

    # ---- run ----------------------------------------------------------------------------

    def run(self) -> RunLog:
        self.scheduler.run_until(round(self.scenario.duration_s * 1e6))
        return self.log

