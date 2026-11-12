"""Wires the test environment around any planner that meets interfaces.Planner.

Deterministic single-process mode (Software Qualification Test Specification 4.1),
closed loop: Trajectory -> stand-in Lateral Controller -> stand-in EPS -> vehicle model.

Blocks and rates (4.1, 4.2):

| Block | Period | Output |
|---|---|---|
| Lane camera | 50 ms | LaneModel, delivered after 100 ms |
| IMU, steering, speed | 10, 10, 20 ms | Chassis signals, stamped at receive |
| State estimator | 20 ms | VehicleStateEstimate |
| ADAS function stand-in or scripted inputs | 25 ms | FunctionRequests |
| Longitudinal block: scripted, or stand-in ACC (4.7) | 25 ms | LongitudinalPlan |
| Planner | 25 ms | Trajectory, PathStatus |
| Lateral Controller | 10 ms | SteeringRequest |

Each block starts at a random phase from the seed. The planner is given from outside;
only eval/ knows which planner it is.
"""

import time
from bisect import bisect_left
from dataclasses import dataclass, field, replace
from math import atan2, cos, sin, tan

from interfaces import (
    TRAJECTORY_POINTS,
    BasicHeader,
    FrameId,
    Header,
    InterventionPhase,
    Pose2D,
    TrajectoryPoint,
    FUNCTION_REQUESTS_MAX_AGE_US,
    FUNCTION_REQUESTS_TIMEOUT_US,
    PLANNER_PERIOD_US,
    PATH_STATUS_TIMEOUT_US,
    ActiveFunction,
    EgoMotionRequest,
    EgoMotionResponse,
    FunctionRequest,
    FunctionRequests,
    LaneModel,
    LateralLimits,
    LineStatus,
    ObjectList,
    PathStatus,
    PlannerFactory,
    PlannerInputs,
    Received,
    Trajectory,
)
from interfaces.inputs.chassis_signals import IMU_TIMEOUT_US, SPEED_TIMEOUT_US, STEERING_TIMEOUT_US, Direction
from interfaces.inputs.lane_model import LANE_MODEL_MAX_AGE_US, LANE_MODEL_TIMEOUT_US
from interfaces.inputs.object_list import OBJECT_LIST_MAX_AGE_US, OBJECT_LIST_TIMEOUT_US
from interfaces.inputs.vehicle_state import VEHICLE_STATE_MAX_AGE_US, VEHICLE_STATE_TIMEOUT_US
from interfaces.inputs.longitudinal_plan import (LONGITUDINAL_PLAN_MAX_AGE_US, LONGITUDINAL_PLAN_TIMEOUT_US,
                                                 LongitudinalPlan)
import numpy as np

from sim.can.frames import CanReceiver, CanSender
from sim.faults.channel import ChannelFaultInjector
from sim.faults.ego_motion import EgoMotionFaults
from sim.faults.lane import LaneFaultInjector
from sim.faults import trigger as fault_trigger
from sim.faults import sensor as sensor_faults
from sim.runtime.clock import clocks
from sim.messages import DriverSignals, SteeringRequest
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
from sim.stand_ins.adas_function import AdasFunction, AdasInputs, PathFeedback
from sim.stand_ins.adas_observation import VehicleMotion
from sim.stand_ins.eps import Eps
from sim.stand_ins.hwa_view_gate import HwaViewGate
from sim.stand_ins.lateral_controller import CONTROLLER_PERIOD_US, EgoState, LateralController
from sim.stand_ins.acc import Acc, LeadSelector, LongitudinalActuator
from sim.stand_ins.scripted import ScriptedFunctionRequests, ScriptedLongitudinal
from sim.vehicle.bicycle import Bicycle, BicycleState, steady_cornering
from sim.vehicle.profiles import PROFILES
from sim.world.road import Road

TRUTH_PERIOD_US = 1_000  # Ground truth logged every step
DRIVER_TORQUE_PERIOD_US = 20_000  # ADAS Function Specification 12

# Fixed block priority within one step (4.2): producers before consumers.
PRIORITY = {"function_requests": 0, "longitudinal": 1, "planner": 2, "controller": 3}


@dataclass
class PlannerCycle:
    t0_us: int
    trajectory: Trajectory | None
    path_status: PathStatus | None
    lateral_limits: LateralLimits | None
    compute_ns: int  # Wall clock of planner.step, adapter included
    # Lane model given to the planner: capture stamp and the range end of L1, R1 the camera
    # really observed [m], before faults (Software Requirements Specification 4)
    lane_view: tuple[int, float] | None = None
    function_requests: Received[FunctionRequests] | None = None
    lane_view_reported: float | None = None  # Range end of L1, R1 as the lane model sent it [m]
    # Whether each input given to the planner was usable at t0 by the receiving checks of the
    # Interface Control Document 4 (received, valid, within timeout and maximum age); the lane
    # model also needs one line or road edge not LOST. For the scoring of PP-SWR-030.
    inputs_ok: dict[str, bool] | None = None
    t0_local_us: int | None = None  # t0 on the ADAS ECU clock, as the planner got it
    # (stamp_us, rx_us, valid) of each input as the planner got it, ADAS ECU clock
    input_times: dict[str, tuple[int, int, bool]] | None = None
    # (status, confidence) of lines L2, L1, R1, R2 and the left and right road edges given to the
    # planner, for "biên làn đủ tin" (Software Requirements Specification 4); None: no lane model
    lane_boundaries: tuple[tuple[LineStatus, float], ...] | None = None
    longitudinal_plan: Received[LongitudinalPlan] | None = None  # As the planner got it (PP-SWR-153, 154)


FUTURE_STAMP_TOLERANCE_US = 10_000  # PP-SWR-132: a stamp up to 10 ms ahead stays usable


def _usable(rx: Received | None, now_us: int, timeout_us: int, max_age_us: int | None = None):
    """As _fresh, but a stamp up to FUTURE_STAMP_TOLERANCE_US in the future is accepted."""
    if rx is None or not 0 <= now_us - rx.rx_us <= timeout_us or not rx.message.header.valid:
        return None
    age = now_us - rx.message.header.stamp_us
    if age < -FUTURE_STAMP_TOLERANCE_US or max_age_us is not None and age > max_age_us:
        return None
    return rx.message


def inputs_usable(inputs: PlannerInputs) -> dict[str, bool]:
    now = inputs.t0_us
    _fresh = _usable
    lane = _fresh(inputs.lane_model, now, LANE_MODEL_TIMEOUT_US, LANE_MODEL_MAX_AGE_US)
    return {
        "lane_model": lane is not None,  # received, valid, in time; boundaries judged by eval
        "object_list": _fresh(inputs.object_list, now, OBJECT_LIST_TIMEOUT_US, OBJECT_LIST_MAX_AGE_US) is not None,
        "imu": _fresh(inputs.imu, now, IMU_TIMEOUT_US) is not None,
        "steering": _fresh(inputs.steering, now, STEERING_TIMEOUT_US) is not None,
        "speed": _fresh(inputs.speed, now, SPEED_TIMEOUT_US) is not None,
        "vehicle_state": _fresh(inputs.vehicle_state, now, VEHICLE_STATE_TIMEOUT_US,
                                VEHICLE_STATE_MAX_AGE_US) is not None,
        "function_requests": _fresh(inputs.function_requests, now, FUNCTION_REQUESTS_TIMEOUT_US,
                                    FUNCTION_REQUESTS_MAX_AGE_US) is not None,
        "longitudinal_plan": _fresh(inputs.longitudinal_plan, now, LONGITUDINAL_PLAN_TIMEOUT_US,
                                    LONGITUDINAL_PLAN_MAX_AGE_US) is not None,
    }


@dataclass(frozen=True, slots=True)
class AdasComparison:
    t_us: int
    measured_requests: FunctionRequests  # Mode A
    ideal_requests: FunctionRequests  # Mode B
    measured_tlc_s: tuple[float, ...]  # L1, R1, left edge, right edge
    ideal_tlc_s: tuple[float, ...]


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
    rear_v_y: list[float] = field(default_factory=list)
    yaw_rate: list[float] = field(default_factory=list)
    adas: list[AdasComparison] = field(default_factory=list)
    actuator_delay_s: float = 0.0
    # Per channel fault of the scenario, in its order: indices of the messages it made unusable
    fault_hits: list[list[int]] = field(default_factory=list)
    can_stats: dict | None = None  # frames dropped and lost per frame ID, CAN receive layer
    # Faults started by a planner-output event (sim.faults.trigger): event -> planner t0 [us]
    # of the first cycle that showed it, None when it never happened (fault not injected)
    fault_events: dict[str, int | None] = field(default_factory=dict)
    # Lane of base_link as the camera indexes it, at each change: (capture stamp, lanes to the
    # left of the reference lane). Ground truth for lane-change cases (S17).
    lane_index_changes: list[tuple[int, int]] = field(default_factory=list)
    # Every occurrence of the planner-output events of sim.faults.trigger: event -> t0 [us]
    events: dict[str, list[int]] = field(default_factory=dict)


def _ego_view_end(lane: LaneModel) -> float | None:
    ends = [line.view_range_end for line in lane.lines[1:3] if line.status != LineStatus.LOST]
    return min(ends) if ends else None


def _fresh(rx: Received | None, now_us: int, timeout_us: int, max_age_us: int | None = None):
    if rx is None or not 0 <= now_us - rx.rx_us <= timeout_us or not rx.message.header.valid:
        return None
    age = now_us - rx.message.header.stamp_us
    if age < 0 or max_age_us is not None and age > max_age_us:
        return None
    return rx.message


class Harness:
    def __init__(self, scenario: Scenario, planner_factory: PlannerFactory, seed: int) -> None:
        self.scenario = scenario
        self.seed = seed
        self.rngs = spawn_streams(seed)
        self.road = Road(list(scenario.segments), scenario.lane_width, scenario.road_layout)
        self.profile = PROFILES[scenario.profile]
        self.vehicle_config = self.profile.vehicle_config()
        self.planner = planner_factory(self.vehicle_config)

        # Car on the road, rear axle at start_s, aligned with the lane plus the given offset.
        # In a curve the fake driver is already steering it: steady-state cornering.
        x, y, heading = self.road.pose_at(scenario.start_s, scenario.start_offset_m)
        lr = self.profile.lr
        kappa0 = self._nominal_curvature(self.road.project(x, y, scenario.start_s))
        v_y0, r0, delta0 = steady_cornering(self.profile, scenario.speed_mps, kappa0)
        psi = heading + scenario.start_heading_rad
        if scenario.driver is not None:
            # Start the rear axle's velocity along the prescribed test path.
            # Body heading differs by the slip angle in a steady turn.
            psi -= atan2(v_y0 - lr * r0, scenario.speed_mps)
        self.vehicle = Bicycle(self.profile, BicycleState(x + lr * cos(psi), y + lr * sin(psi),
                                                          psi, v_y0, r0), mu=scenario.road_mu)
        self.vehicle.v_x = scenario.speed_mps
        self._s_hint = scenario.start_s
        self._road_curvature = kappa0

        self.eps = Eps(self.vehicle_config, scenario.eps_delay_s, moving_driver_target=scenario.driver is not None)
        self.eps.hold_driver_angle(delta0 * self.vehicle_config.steering_ratio)
        # S2: the car keeps the start offset and heading until HWA starts driving.
        self._holding = scenario.hold_until_hwa
        self._hold_s = scenario.start_s
        if self._holding:
            self._place_held()
        self.controller = LateralController(self.vehicle_config, self.profile.understeer_gradient)
        self.camera = LaneCamera(self.road, view_end_m=scenario.camera_view_m,
                                 view_start_m=scenario.camera_view_start_m)
        self.lane_faults = LaneFaultInjector(scenario.lane_faults, self.rngs["lane_camera"])
        self.traffic = Traffic(self.road, scenario.traffic)
        self.objects = ObjectSensor(self.rngs["perception"], scenario.perception_noise_scale)
        self.chassis = ChassisSensors()
        self.estimator = StateEstimator()
        self.ego_motion = EgoMotion()
        # Faults beyond the lane model (Software Qualification Test Specification 6). Every
        # stream is drawn in a fixed order whatever the faults, so adding one changes no other draw.
        base = self.rngs["faults"]
        self._channel_rng = np.random.default_rng(int(base.integers(0, 2**63)))
        nominal_rng = np.random.default_rng(int(base.integers(0, 2**63)))
        chassis_rng = self.rngs["chassis"]
        signal_rngs = {sig: np.random.default_rng(int(chassis_rng.integers(0, 2**63)))
                       for sig in ("yaw_rate", "accel_x", "accel_y", "speed", "steering_angle")}
        signal_rngs["lateral_velocity"] = self.rngs["state_estimator"]
        nominal = sensor_faults.nominal(nominal_rng)
        self.sensor_errors = sensor_faults.SensorErrors(
            scenario.sensor_faults + (nominal if scenario.realism else ()), signal_rngs)
        self.clocks = clocks(seed, scenario.realism, scenario.clock_faults)
        self._ideal_clocks = all(c.ideal for c in self.clocks.values())
        self.ego_faults = EgoMotionFaults(scenario.ego_motion_faults)
        self.can = scenario.can_bus or scenario.realism
        self._can_tx, self._can_rx = CanSender(), CanReceiver()
        self._open_counter = 0
        hwa_request_us = None if scenario.hwa_request_s is None else round(scenario.hwa_request_s * 1e6)
        self.function_requests = ScriptedFunctionRequests(hwa_request_us, scenario.request_events)
        # ADAS Function Specification 7: HWA leaves REQUEST when the preview stays too short.
        self._hwa_view_gate = HwaViewGate() if scenario.hwa_view_gate else None
        self._driver = DriverSignals()
        self._driver_torque = 0.0
        self._adas_modes: tuple[AdasFunction, AdasFunction] | None = None
        self._ideal_lane: LaneModel | None = None
        self._observed_view: dict[int, float | None] = {}  # capture stamp -> observed L1, R1 end
        self._ideal_objects: ObjectList | None = None
        if scenario.adas_mode != "scripted":
            self._adas_modes = (AdasFunction(self.vehicle_config, lka_enabled=scenario.lka_enabled,
                                             elk_enabled=scenario.elk_enabled),
                                AdasFunction(self.vehicle_config, lka_enabled=scenario.lka_enabled,
                                             elk_enabled=scenario.elk_enabled))
            self._ideal_camera = LaneCamera(self.road, view_end_m=scenario.camera_view_m,
                                            view_start_m=scenario.camera_view_start_m, ideal=True)
            self._ideal_object_sensor = ObjectSensor(self.rngs["perception"], ideal=True)
        # Longitudinal side: scenario speed held ('off'), or the stand-in ACC that ignores
        # ('ignore_limits', R79 Annex 8 3.2.2 and the S14 second run) or reads LateralLimits.
        self.longitudinal = ScriptedLongitudinal(scenario.speed_mps)
        self.acc = (Acc(scenario.speed_mps, read_limits=scenario.acc == "on")
                    if scenario.acc != "off" else None)
        self.long_act = LongitudinalActuator(scenario.speed_mps)
        self._lead = LeadSelector(self.vehicle_config.vehicle_width, self.vehicle_config.wheelbase)

        camera_us = round(scenario.camera_latency_ms * 1000)  # Software Qualification Test Specification 4.5, Q1
        jitter_us = round(scenario.camera_jitter_ms * 1000)
        receive = self._can_rx.decode if self.can else restamp
        self._injectors: dict[str, ChannelFaultInjector] = {}

        def faults(name: str):
            mine = tuple(f for f in scenario.channel_faults if f.channel == name)
            if not mine:
                return None
            self._injectors[name] = ChannelFaultInjector(mine, self._channel_rng)
            return self._injectors[name]

        self.ch = {
            "lane_model": Channel("lane_model", latency_us=camera_us, jitter_us=jitter_us,
                                  rng=self.rngs["latency"], faults=faults("lane_model")),
            "object_list": Channel("object_list", latency_us=camera_us, jitter_us=jitter_us,
                                   rng=self.rngs["latency"], faults=faults("object_list")),
            "imu": Channel("imu", on_deliver=receive, faults=faults("imu")),
            "steering": Channel("steering", on_deliver=receive, faults=faults("steering")),
            "speed": Channel("speed", on_deliver=receive, faults=faults("speed")),
            "vehicle_state": Channel("vehicle_state", faults=faults("vehicle_state")),
            "function_requests": Channel("function_requests",
                                         latency_us=round(scenario.function_requests_latency_ms * 1000),
                                         faults=faults("function_requests")),
            "longitudinal_plan": Channel("longitudinal_plan", faults=faults("longitudinal_plan")),
            "open_trajectory": Channel("open_trajectory"),
            "open_status": Channel("open_status"),
            "trajectory": Channel("trajectory"),
            "lateral_limits": Channel("lateral_limits"),
            "path_status": Channel("path_status"),
            "steering_request": Channel("steering_request"),
        }
        # Ego-motion integrates the valid chassis signals and v_y as received (4.5).
        self.ch["imu"].subscribers.append(
            lambda m, rx: m.header.valid and self.ego_motion.on_yaw_rate(m.yaw_rate_rps, rx))
        self.ch["speed"].subscribers.append(
            lambda m, rx: m.header.valid and self.ego_motion.on_speed(m.speed_mps, rx))
        self.ch["vehicle_state"].subscribers.append(
            lambda m, rx: m.header.valid and self.ego_motion.on_lateral_velocity(m.lateral_velocity, rx))
        # Open loop (4.1): the controller follows a predefined path, not the planner's.
        path_ch, status_ch = ("open_trajectory", "open_status") if scenario.loop == "open" else (
            "trajectory", "path_status")
        self.ch[path_ch].subscribers.append(self.controller.on_trajectory)
        self.ch[status_ch].subscribers.append(self.controller.on_path_status)
        self.ch["steering_request"].subscribers.append(self.eps.on_request)
        if self.acc is not None:
            self.ch["lateral_limits"].subscribers.append(self.acc.on_lateral_limits)
        self.ch["path_status"].subscribers.append(self._release_on_hwa)
        # Faults that wait for an event of the planner output: inactive until it happens.
        self._pending: list[tuple[object, int, object]] = []
        self._fault_events: dict[str, int | None] = {}
        self._events = fault_trigger.EventCounter()
        # Driver repeats that wait for an event (S16): inactive until the k-th occurrence.
        self._driver_spec = scenario.driver
        self._driver_waiting: list[tuple[float, float]] = []
        if scenario.driver is not None and scenario.driver.repeat_trigger is not None:
            self._driver_waiting = list(scenario.driver.repeats)
            self._driver_spec = replace(scenario.driver, repeats=tuple(
                (fault_trigger.NEVER_S, k) for _, k in scenario.driver.repeats))
        for owner in (self.lane_faults, self.sensor_errors, self.ego_faults, *self._injectors.values()):
            owner.faults = list(owner.faults)
            for i, fault in enumerate(owner.faults):
                if getattr(fault, "trigger", None) is not None:
                    owner.faults[i] = replace(fault, start_s=fault_trigger.NEVER_S)
                    self._pending.append((owner, i, fault))
                    self._fault_events[fault.trigger] = None

        self.log = RunLog(
            scenario=scenario, seed=seed, road=self.road,
            vehicle_width=self.vehicle_config.vehicle_width,
            wheelbase=self.vehicle_config.wheelbase,
            max_wheel_angle=self.vehicle_config.max_wheel_angle,
            max_steering_wheel_rate=self.vehicle_config.max_steering_wheel_rate,
            steering_ratio=self.vehicle_config.steering_ratio,
            init_result=int(self.planner.init_result),
            actuator_delay_s=self.vehicle_config.actuator_delay,
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
        if self.scenario.traffic or self._adas_modes is not None:
            sched.add_sensor("object_sensor", object_sensor.PERIOD_US, self._objects,
                             phase(object_sensor.PERIOD_US))
        sched.add_sensor("steering", chassis.STEERING_PERIOD_US, self._steering,
                         phase(chassis.STEERING_PERIOD_US))
        sched.add_sensor("speed", chassis.SPEED_PERIOD_US, self._speed, phase(chassis.SPEED_PERIOD_US))
        sched.add_sensor("state_estimator", state_estimator.PERIOD_US, self._state,
                         phase(state_estimator.PERIOD_US))
        if self._adas_modes is not None:
            sched.add_sensor("driver_torque", DRIVER_TORQUE_PERIOD_US, self._sample_driver_torque,
                             phase(DRIVER_TORQUE_PERIOD_US))
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

    def _nominal_curvature(self, projection) -> float:
        if self.scenario.driver is not None:
            scale = 1 - projection.curvature * projection.d
            if scale > 0:
                return projection.curvature / scale
        return projection.curvature

    def _physics(self, now_us: int, dt: float) -> None:
        if self._holding:
            self._hold_s += self.scenario.speed_mps * dt
            self._place_held()
        if self.scenario.driver is not None:
            angle, force, self._driver = self._driver_spec.command(
                now_us, self.profile, self.vehicle_config.steering_ratio, self.vehicle.v_x, self._road_curvature)
            self.eps.driver_angle = angle
            self.eps.driver_torque = self._driver.torque_nm
            self.vehicle.external_force_y = force
        delta = self.eps.step(now_us, dt)
        if not self._holding:
            speed = self.long_act.step(now_us, dt) if self.acc is not None else self.scenario.speed_mps
            self.vehicle.step(dt, delta, speed)
        rear = self.vehicle.rear_axle()
        projection = self.road.project(rear[0], rear[1], self._s_hint)
        self._s_hint, self._road_curvature = projection.s, self._nominal_curvature(projection)
        if now_us % TRUTH_PERIOD_US == 0:
            log = self.log
            log.t_us.append(now_us)
            log.rear.append(rear)
            log.front.append(self.vehicle.front_axle())
            log.a_y.append(self.vehicle.a_y)
            log.speed.append(self.vehicle.v_x)
            log.wheel_angle.append(delta)
            log.eps_controlling.append(self.eps.controlling)
            log.rear_v_y.append(self.vehicle.rear_axle_lateral_velocity())
            log.yaw_rate.append(self.vehicle.state.r)

    def _camera(self, now_us: int) -> None:
        x, y, yaw = self.vehicle.rear_axle()
        pose = CameraPose(x, y, yaw, self._s_hint)
        before = self.camera.lane_index
        msg = self.camera.capture(now_us, pose, self.lane_faults.view_limits(now_us))
        if self.camera.lane_index != before:
            self.log.lane_index_changes.append((now_us, self.camera.lane_index))
        sent = self._camera_stamp(self.lane_faults.apply(msg))
        self._observed_view[sent.header.stamp_us] = _ego_view_end(msg)
        for stamp in [t for t in self._observed_view if t < sent.header.stamp_us - 1_000_000]:
            del self._observed_view[stamp]
        self.ch["lane_model"].publish(sent, now_us)
        if self._adas_modes is not None:
            self._ideal_lane = self._ideal_camera.capture(now_us, pose)

    def _objects(self, now_us: int) -> None:
        pose, speed = self.vehicle.rear_axle(), self.vehicle.v_x
        traffic = self.traffic.at(now_us * 1e-6)
        msg = self.objects.capture(now_us, pose, speed, traffic)
        self.ch["object_list"].publish(self._camera_stamp(msg), now_us)
        if self._adas_modes is not None:
            self._ideal_objects = self._ideal_object_sensor.capture(now_us, pose, speed, traffic)

    def _imu(self, now_us: int) -> None:
        yaw_rate = self.vehicle.state.r
        delay_us = round(self.scenario.yaw_filter_delay_ms * 1000)
        if delay_us > 0 and self.log.t_us:
            # Filter delay the planner is not told about (Q2): the value of delay_us ago, stamped now.
            i = bisect_left(self.log.t_us, now_us - delay_us)
            yaw_rate = self.log.yaw_rate[min(i, len(self.log.yaw_rate) - 1)] if self.log.yaw_rate else yaw_rate
        err = self.sensor_errors.apply
        yaw_rate = err("yaw_rate", yaw_rate, now_us)
        accel_x = err("accel_x", 0.0, now_us)
        accel_y = err("accel_y", self.vehicle.a_y, now_us)
        msg = (self._can_tx.imu(yaw_rate, accel_x, accel_y) if self.can
               else self.chassis.imu(now_us, yaw_rate, accel_x, accel_y))
        self.ch["imu"].publish(msg, now_us)

    def _steering(self, now_us: int) -> None:
        angle = self.sensor_errors.apply("steering_angle", self.eps.angle, now_us)
        msg = (self._can_tx.steering(angle, self.eps.rate) if self.can
               else self.chassis.steering(now_us, angle, self.eps.rate))
        self.ch["steering"].publish(msg, now_us)

    def _speed(self, now_us: int) -> None:
        speed = self.sensor_errors.apply("speed", self.vehicle.v_x, now_us)
        msg = self._can_tx.speed(speed) if self.can else self.chassis.speed(now_us, speed)
        self.ch["speed"].publish(msg, now_us)

    def _state(self, now_us: int) -> None:
        v_y = self.sensor_errors.apply("lateral_velocity", self.vehicle.rear_axle_lateral_velocity(), now_us)
        msg = self.estimator.message(now_us, v_y, self.vehicle.slip_angle())
        self.ch["vehicle_state"].publish(msg, now_us)

    def _camera_stamp(self, message):
        """Capture time on the camera ECU clock (4.2)."""
        if self._ideal_clocks:
            return message
        stamp = self.clocks["camera"].local(message.header.stamp_us)
        return replace(message, header=replace(message.header, stamp_us=stamp))

    def _planner_view(self, name: str, rx: Received | None) -> Received | None:
        """An input as the planner gets it: rx_us, and stamps set on the ADAS ECU, on its clock."""
        if rx is None or self._ideal_clocks:
            return rx
        adas = self.clocks["adas"]
        message = rx.message
        if name not in ("lane_model", "object_list"):  # stamped on the ADAS ECU (or at receive, CAN)
            message = replace(message, header=replace(message.header, stamp_us=adas.local(message.header.stamp_us)))
        return Received(message, adas.local(rx.rx_us))

    def _open_loop_path(self, now_us: int) -> None:
        """Predefined path of the open loop (4.1): the true lane centre ahead, or nothing when a
        scripted driver steers the car (S4 to S8)."""
        if self.scenario.driver is not None:
            return
        x, y, yaw = self.vehicle.rear_axle()
        s0 = self.road.project(x, y, self._s_hint).s
        v = max(self.vehicle.v_x, 0.1)
        points = []
        for i in range(TRAJECTORY_POINTS):
            t = 0.1 * i
            px, py, ph = self.road.pose_at(s0 + v * t, 0.0)
            kappa = self.road.project(px, py, s0 + v * t).curvature
            dx, dy = px - x, py - y
            points.append(TrajectoryPoint(t, Pose2D(dx * cos(yaw) + dy * sin(yaw), -dx * sin(yaw) + dy * cos(yaw),
                                                    ph - yaw), v, 0.0, 0.0, v * kappa, kappa,
                                          atan2(self.vehicle_config.wheelbase * kappa, 1.0), 0.0))
        traj = Trajectory(Header(now_us, self._open_counter % 256, True, FrameId.BASE_LINK), tuple(points), 3.0)
        status = PathStatus(BasicHeader(now_us, self._open_counter % 256, True), True, ActiveFunction.HWA,
                            InterventionPhase.NONE, InterventionPhase.NONE, False, False)
        self._open_counter += 1
        self.ch["open_trajectory"].publish(traj, now_us)
        self.ch["open_status"].publish(status, now_us)

    def _sample_driver_torque(self, _now_us: int) -> None:
        self._driver_torque = self._driver.torque_nm

    # ---- blocks -------------------------------------------------------------------------

    def _function_requests(self, now_us: int) -> None:
        if self._adas_modes is None:
            message = self.function_requests.message(now_us)
            hwa = self._gated_hwa(message.requests[0], now_us)
            if hwa != message.requests[0]:
                message = replace(message, requests=(hwa,) + message.requests[1:])
        else:
            message = self._adas_function_requests(now_us)
        self.ch["function_requests"].publish(message, now_us)

    def _gated_hwa(self, hwa: FunctionRequest, now_us: int) -> FunctionRequest:
        if self._hwa_view_gate is None:
            return hwa
        speed = _fresh(self.ch["speed"].latest, now_us, SPEED_TIMEOUT_US)
        lane = _fresh(self.ch["lane_model"].latest, now_us, LANE_MODEL_TIMEOUT_US, LANE_MODEL_MAX_AGE_US)
        return self._hwa_view_gate.apply(hwa, now_us, lane,
                                         speed.speed_mps if speed is not None else self.vehicle.v_x)

    def _measured_motion(self, now_us: int) -> VehicleMotion | None:
        ch = self.ch
        speed = _fresh(ch["speed"].latest, now_us, SPEED_TIMEOUT_US)
        imu = _fresh(ch["imu"].latest, now_us, IMU_TIMEOUT_US)
        steering = _fresh(ch["steering"].latest, now_us, STEERING_TIMEOUT_US)
        state = _fresh(ch["vehicle_state"].latest, now_us, VEHICLE_STATE_TIMEOUT_US, VEHICLE_STATE_MAX_AGE_US)
        if speed is None or imu is None or steering is None or state is None:
            return None
        return VehicleMotion(speed.speed_mps if speed.direction == Direction.FORWARD else 0.0,
                             state.lateral_velocity, state.lateral_velocity_variance,
                             imu.yaw_rate_rps, steering.steering_wheel_rate_rps)

    def _truth_motion(self, request: EgoMotionRequest) -> EgoMotionResponse:
        log = self.log
        a = bisect_left(log.t_us, request.t1_us)
        b = bisect_left(log.t_us, request.t2_us)
        if b >= len(log.t_us) or a > b or log.t_us[a] != request.t1_us or log.t_us[b] != request.t2_us:
            return EgoMotionResponse(False, 0.0, 0.0, 0.0)
        x, y, yaw = log.rear[a]
        xx, yy, yaw_now = log.rear[b]
        dx, dy = xx - x, yy - y
        return EgoMotionResponse(True, dx * cos(yaw) + dy * sin(yaw),
                                 -dx * sin(yaw) + dy * cos(yaw), yaw_now - yaw)

    def _adas_function_requests(self, now_us: int) -> FunctionRequests:
        measured_adas, ideal_adas = self._adas_modes
        ch = self.ch
        status = _fresh(ch["path_status"].latest, now_us, PATH_STATUS_TIMEOUT_US)
        preview = PathFeedback(path_valid=status is not None and status.path_valid)
        feedback = PathFeedback(status.path_valid, status.lka_phase, status.elk_phase) if status else preview
        select_measured = self.scenario.adas_mode == "A"
        driver = DriverSignals(self._driver_torque, self._driver.indicator, self._driver.hands_on,
                               self._driver.esc_enabled, self._driver.esc_active)
        measured = AdasInputs(
            _fresh(ch["lane_model"].latest, now_us, LANE_MODEL_TIMEOUT_US, LANE_MODEL_MAX_AGE_US),
            _fresh(ch["object_list"].latest, now_us, OBJECT_LIST_TIMEOUT_US, OBJECT_LIST_MAX_AGE_US),
            self._measured_motion(now_us), driver, feedback if select_measured else preview,
        )
        ideal = AdasInputs(self._ideal_lane, self._ideal_objects,
                           VehicleMotion(self.vehicle.v_x, self.vehicle.rear_axle_lateral_velocity(),
                                         0.0, self.vehicle.state.r, self.eps.rate), driver,
                           preview if select_measured else feedback)
        hwa = self._gated_hwa(self.function_requests.hwa_request(now_us), now_us)
        message_a = measured_adas.message(now_us, measured, self.ego_motion.query, hwa)
        message_b = ideal_adas.message(now_us, ideal, self._truth_motion, hwa)
        self.log.adas.append(AdasComparison(now_us, message_a, message_b, measured_adas.tlc_s, ideal_adas.tlc_s))
        return message_a if select_measured else message_b

    def _longitudinal(self, now_us: int) -> None:
        if self.acc is None:
            msg = self.longitudinal.message(now_us)
        else:
            ch = self.ch
            lead = self._lead.update(
                now_us, _fresh(ch["object_list"].latest, now_us, OBJECT_LIST_TIMEOUT_US, OBJECT_LIST_MAX_AGE_US),
                ch["trajectory"].latest.message if ch["trajectory"].latest is not None else None,
                _fresh(ch["lane_model"].latest, now_us, LANE_MODEL_TIMEOUT_US, LANE_MODEL_MAX_AGE_US),
                self.vehicle.v_x)
            msg = self.acc.step(now_us, self.vehicle.v_x, lead)
            self.long_act.command(now_us, self.acc.command)
        self.ch["longitudinal_plan"].publish(msg, now_us)

    def _planner(self, now_us: int) -> None:
        ch = self.ch
        view = self._planner_view
        t0_local = now_us if self._ideal_clocks else self.clocks["adas"].local(now_us)
        inputs = PlannerInputs(
            t0_us=t0_local,
            lane_model=view("lane_model", ch["lane_model"].latest),
            object_list=view("object_list", ch["object_list"].latest),
            imu=view("imu", ch["imu"].latest),
            steering=view("steering", ch["steering"].latest),
            speed=view("speed", ch["speed"].latest),
            vehicle_state=view("vehicle_state", ch["vehicle_state"].latest),
            function_requests=view("function_requests", ch["function_requests"].latest),
            longitudinal_plan=view("longitudinal_plan", ch["longitudinal_plan"].latest),
        )
        ego_invalid = self.ego_faults.invalid(now_us)
        adas = self.clocks["adas"]

        def ego_motion(request: EgoMotionRequest) -> EgoMotionResponse:
            if ego_invalid:  # F20 (PP-SWR-143)
                return EgoMotionResponse(False, 0.0, 0.0, 0.0)
            if not self._ideal_clocks:
                request = EgoMotionRequest(adas.to_global(request.t1_us), adas.to_global(request.t2_us))
            return self.ego_motion.query(request)

        start = time.perf_counter_ns()
        out = self.planner.step(inputs, ego_motion)
        compute_ns = time.perf_counter_ns() - start
        if out.trajectory is not None:
            ch["trajectory"].publish(out.trajectory, now_us)
        if out.path_status is not None:
            ch["path_status"].publish(out.path_status, now_us)
        if out.lateral_limits is not None:
            ch["lateral_limits"].publish(out.lateral_limits, now_us)
        if out.path_status is not None:
            for event in self._events.update(out.path_status, now_us):
                self.function_requests.on_event(event, now_us)
                self._driver_event(event, now_us)
            if self._pending:
                self._start_triggered(out.path_status, now_us)
        lane = inputs.lane_model
        lane_view = None
        reported = None
        if lane is not None:
            stamp = lane.message.header.stamp_us
            reported = _ego_view_end(lane.message)
            observed = self._observed_view.get(stamp, reported)
            if reported is not None and observed is not None:
                lane_view = (stamp, min(observed, reported))
        usable = inputs_usable(inputs)
        usable["ego_motion"] = not ego_invalid
        times = {name: (rx.message.header.stamp_us, rx.rx_us, rx.message.header.valid)
                 for name in ("lane_model", "object_list", "imu", "steering", "speed", "vehicle_state",
                              "function_requests", "longitudinal_plan")
                 if (rx := getattr(inputs, name)) is not None}
        boundaries = (None if inputs.lane_model is None else
                      tuple((b.status, b.confidence) for b in (*inputs.lane_model.message.lines,
                                                               *inputs.lane_model.message.road_edges)))
        self.log.cycles.append(PlannerCycle(now_us, out.trajectory, out.path_status,
                                            out.lateral_limits, compute_ns, lane_view, inputs.function_requests,
                                            reported, usable, t0_local, times, boundaries,
                                            inputs.longitudinal_plan))
        if self.scenario.loop == "open":
            self._open_loop_path(now_us)

    def _driver_event(self, event: str, now_us: int) -> None:
        spec = self._driver_spec
        if spec is None or spec.repeat_trigger != event or not self._driver_waiting:
            return
        k = len(spec.repeats) - len(self._driver_waiting)
        offset, scale = self._driver_waiting.pop(0)
        repeats = list(spec.repeats)
        repeats[k] = (now_us * 1e-6 + offset, scale)
        self._driver_spec = replace(spec, repeats=tuple(repeats))

    def _start_triggered(self, status: PathStatus, now_us: int) -> None:
        for event, seen in self._fault_events.items():
            if seen is None and fault_trigger.happened(event, status):
                self._fault_events[event] = now_us
        waiting = []
        for owner, i, fault in self._pending:
            t_us = self._fault_events[fault.trigger]
            if t_us is None:
                waiting.append((owner, i, fault))
            else:
                owner.faults[i] = replace(fault, start_s=t_us * 1e-6 + fault.start_s)
        self._pending = waiting

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
        position = {name: 0 for name in self._injectors}
        for fault in self.scenario.channel_faults:
            injector = self._injectors[fault.channel]
            self.log.fault_hits.append(injector.fault_hits()[position[fault.channel]])
            position[fault.channel] += 1
        self.log.fault_events = dict(self._fault_events)
        self.log.events = {e: list(t) for e, t in self._events.times.items() if t}
        if self._fault_events:
            # Faults as injected: a triggered fault carries its real start (NEVER_S if not injected).
            channel = list(self.scenario.channel_faults)
            position = {name: 0 for name in self._injectors}
            for k, fault in enumerate(channel):
                channel[k] = self._injectors[fault.channel].faults[position[fault.channel]]
                position[fault.channel] += 1
            self.log.scenario = replace(
                self.scenario, lane_faults=tuple(self.lane_faults.faults), channel_faults=tuple(channel),
                sensor_faults=tuple(self.sensor_errors.faults[:len(self.scenario.sensor_faults)]),
                ego_motion_faults=tuple(self.ego_faults.faults))
        if self.can:
            self.log.can_stats = {"dropped": dict(self._can_rx.dropped), "lost": dict(self._can_rx.lost)}
        return self.log

