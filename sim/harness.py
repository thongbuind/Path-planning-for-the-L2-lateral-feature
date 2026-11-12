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
from sim.faults.lane import LaneFaultInjector
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
from sim.stand_ins.acc import Acc, LongitudinalActuator
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
                                                          psi, v_y0, r0))
        self.vehicle.v_x = scenario.speed_mps
        self._s_hint = scenario.start_s
        self._road_curvature = kappa0

        self.eps = Eps(self.vehicle_config, moving_driver_target=scenario.driver is not None)
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
        self.objects = ObjectSensor(self.rngs["perception"])
        self.chassis = ChassisSensors()
        self.estimator = StateEstimator()
        self.ego_motion = EgoMotion()
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

        camera_us = round(scenario.camera_latency_ms * 1000)  # Software Qualification Test Specification 4.5, Q1
        jitter_us = round(scenario.camera_jitter_ms * 1000)
        self.ch = {
            "lane_model": Channel("lane_model", latency_us=camera_us, jitter_us=jitter_us,
                                  rng=self.rngs["latency"]),
            "object_list": Channel("object_list", latency_us=camera_us, jitter_us=jitter_us,
                                   rng=self.rngs["latency"]),
            "imu": Channel("imu", on_deliver=restamp),
            "steering": Channel("steering", on_deliver=restamp),
            "speed": Channel("speed", on_deliver=restamp),
            "vehicle_state": Channel("vehicle_state"),
            "function_requests": Channel("function_requests",
                                         latency_us=round(scenario.function_requests_latency_ms * 1000)),
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
            angle, force, self._driver = self.scenario.driver.command(
                now_us, self.profile, self.vehicle_config.steering_ratio, self.vehicle.v_x, self._road_curvature)
            self.eps.driver_angle = angle
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
        msg = self.camera.capture(now_us, pose, self.lane_faults.view_limits(now_us))
        self._observed_view[now_us] = _ego_view_end(msg)
        for stamp in [t for t in self._observed_view if t < now_us - 1_000_000]:
            del self._observed_view[stamp]
        self.ch["lane_model"].publish(self.lane_faults.apply(msg), now_us)
        if self._adas_modes is not None:
            self._ideal_lane = self._ideal_camera.capture(now_us, pose)

    def _objects(self, now_us: int) -> None:
        pose, speed = self.vehicle.rear_axle(), self.vehicle.v_x
        traffic = self.traffic.at(now_us * 1e-6)
        msg = self.objects.capture(now_us, pose, speed, traffic)
        self.ch["object_list"].publish(msg, now_us)
        if self._adas_modes is not None:
            self._ideal_objects = self._ideal_object_sensor.capture(now_us, pose, speed, traffic)

    def _imu(self, now_us: int) -> None:
        yaw_rate = self.vehicle.state.r
        delay_us = round(self.scenario.yaw_filter_delay_ms * 1000)
        if delay_us > 0 and self.log.t_us:
            # Filter delay the planner is not told about (Q2): the value of delay_us ago, stamped now.
            i = bisect_left(self.log.t_us, now_us - delay_us)
            yaw_rate = self.log.yaw_rate[min(i, len(self.log.yaw_rate) - 1)] if self.log.yaw_rate else yaw_rate
        self.ch["imu"].publish(self.chassis.imu(now_us, yaw_rate, 0.0, self.vehicle.a_y), now_us)

    def _steering(self, now_us: int) -> None:
        self.ch["steering"].publish(self.chassis.steering(now_us, self.eps.angle, self.eps.rate), now_us)

    def _speed(self, now_us: int) -> None:
        self.ch["speed"].publish(self.chassis.speed(now_us, self.vehicle.v_x), now_us)

    def _state(self, now_us: int) -> None:
        msg = self.estimator.message(now_us, self.vehicle.rear_axle_lateral_velocity(),
                                     self.vehicle.slip_angle())
        self.ch["vehicle_state"].publish(msg, now_us)

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
        reported = None
        if lane is not None:
            stamp = lane.message.header.stamp_us
            reported = _ego_view_end(lane.message)
            observed = self._observed_view.get(stamp, reported)
            if reported is not None and observed is not None:
                lane_view = (stamp, min(observed, reported))
        self.log.cycles.append(PlannerCycle(now_us, out.trajectory, out.path_status,
                                            out.lateral_limits, compute_ns, lane_view, inputs.function_requests,
                                            reported))

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

