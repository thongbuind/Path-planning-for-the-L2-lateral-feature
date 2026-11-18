"""Live worker of the workbench: the delivered planner in the SIL, cycle by cycle, paced to the
wall clock, streamed as NDJSON. Replaces web/simulation/tools/rt_run.py (PP-PR-064).

    python3 -m eval.live catalog          scenarios, faults and levels, combinations, vehicles
    python3 -m eval.live run <folder>     the run of <folder>/request.json; control lines on stdin:
                                          {"cmd":"pause"} {"cmd":"resume"} {"cmd":"rate","value":2}

`run` is started by execution.supervisor (workbench/server.py), which owns <folder>: it numbers
the lines, keeps them as frames.ndjson.gz and finalizes the bundle. This worker writes
resolved-case.json, evaluation.json, trace.mcap and manifest.json there (eval.run_bundle).

The case is built by eval.case from the web configuration, as eval.runner builds it, and the
run is the same Harness with an observer: after each planner cycle (25 ms) the observer builds
the frame of that cycle, waits for the wall clock, then sends it. Both planners are stepped in
real time; nothing is computed ahead. Pacing does not change the simulation (golden set, live
path). A rerun has "recipe", "seed", "rate" and "expect" in request.json instead of "config" alone.

Lines on stdout, field "type":
    phase  resolve | simulate | evaluate | write
    init   static information of the run: road, vehicle, faults, duration
    f      one planner cycle: planner output and simulator ground truth
    done   evaluator conclusion (criteria, targets)
    error  {"class": SUT_EXECUTION | SIM_ERROR | EVAL_ERROR | INFRA, "message": ...}
"""

import bisect
import faulthandler
import json
import math
import os
import re
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = sys.stdout


def sanitize(o):
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    return o


def send(obj):
    OUT.write(json.dumps(sanitize(obj), ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")
    OUT.flush()


def vn(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


# ---------------------------------------------------------------------------------------
# Danh mục
# ---------------------------------------------------------------------------------------

FAULT_GROUP = {
    "F01": "Perception", "F02": "Perception", "F03": "Perception", "F04": "Perception", "F05": "Perception",
    "F06": "Perception", "F07": "Perception", "F08": "Perception", "F21": "Perception", "F22": "Perception",
    "F10": "Timing", "F11": "Timing", "F12": "Timing", "F13": "Timing", "F14": "Timing", "F19": "Timing",
    "F15": "Integrity", "F16": "Integrity", "F17": "Integrity", "F18": "Integrity", "F20": "Integrity",
    "F23": "Integrity",
}


def function_of(sc):
    lka, elk = sc.lka_enabled, sc.elk_enabled
    if lka and elk:
        return "LKA+ELK"
    if lka:
        return "LKA"
    if elk:
        return "ELK"
    if sc.hwa_request_s is not None:
        return "LCC"
    return "Khác"


def catalog():
    import glob
    import yaml
    from eval import loader, openx
    from sim.vehicle.profiles import PROFILES

    sids = sorted({os.path.basename(p).split(".")[0] for p in glob.glob(str(ROOT / "benchmark/scenarios/S*.xosc"))},
                  key=lambda s: (int(re.match(r"S(\d+)", s).group(1)), s))
    scenarios = []
    for sid in sids:
        for v in "abcdefghij":
            try:
                sc = loader.load(sid, v)
            except Exception:
                continue
            n = sc.notes or {}
            scenarios.append(dict(
                id=f"{sid}/{v}", sid=sid, v=v, code=f"{sid} {v}", fn=function_of(sc), desc=n.get("description", ""),
                expected=n.get("expected_outcome"), speed=round(sc.speed_mps * 3.6), dur=sc.duration_s,
                w=sc.lane_width, traffic=len(sc.traffic), profile=sc.profile))

    faults = []
    for path in sorted((ROOT / "benchmark/faults").glob("F*.xosc")):
        if ".anchors" in path.name or ".ranges" in path.name:
            continue
        fid = path.stem
        levels = openx.anchors(path)
        header = re.search(r'FileHeader[^>]*description="([^"]*)"', path.read_text(encoding="utf-8"))
        title = header.group(1) if header else fid
        first = next(iter(levels.values()))
        if title == fid:
            title = first.get("description", fid)
        lv = []
        for k, p in sorted(levels.items()):
            extra = {kk[6:]: vv for kk, vv in p.items() if kk.startswith("fault_") and kk not in
                     ("fault_kind", "fault_start_s", "fault_duration_s", "fault_lines", "fault_value")}
            desc = p.get("description", "")
            if extra:
                desc += " (" + ", ".join(f"{a} {b}" for a, b in extra.items()) + ")"
            lv.append(dict(id=k, desc=desc))
        faults.append(dict(id=fid, title=title, group=FAULT_GROUP.get(fid, "Khác"), levels=lv))

    combos = []
    for path in sorted((ROOT / "benchmark/combinations").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        combos.append(dict(id=data["id"], title=data["title"], faults=[list(f) for f in data["faults"]],
                           sim=data.get("sim", {}), hosts=[list(h) for h in data["hosts"]]))

    vehicles = [dict(id=p.name, wb=p.wheelbase, w=p.width_with_mirrors, mass=p.mass) for p in PROFILES.values()]
    from adapters.sil.sil_planner import PlannerLibraries
    try:
        pp = PlannerLibraries.default().version()
    except Exception as e:  # noqa: BLE001
        pp = f"không đọc được: {e}"
    return dict(scenarios=scenarios, faults=faults, combos=combos, vehicles=vehicles,
                triggers=["lka_active", "elk_active", "intervention_active", "lcc_follow"],
                acc=["off", "on", "ignore_limits"], pp=pp)


# ---------------------------------------------------------------------------------------
# Một lượt chạy
# ---------------------------------------------------------------------------------------

LINE_VI = {0: "trái ngoài (L2)", 1: "trái làn mình (L1)", 2: "phải làn mình (R1)", 3: "phải ngoài (R2)"}
CH_VI = {"lane_model": "lane model", "object_list": "object list", "imu": "IMU", "steering": "góc lái",
         "speed": "tốc độ", "vehicle_state": "vehicle state", "function_requests": "FunctionRequests",
         "longitudinal_plan": "LongitudinalPlan", "lead_target": "LeadTarget"}


def recipe_from_config(cfg: dict) -> dict:
    """eval.case recipe of a web run configuration; faults start at the trigger event (offset 0)."""
    scenario = cfg.get("scenario") or {}
    recipe = {"kind": "catalog", "sid": scenario.get("sid"), "v": scenario.get("v")}
    if cfg.get("faults"):
        recipe["faults"] = [list(f) for f in cfg["faults"]]
    if cfg.get("trigger"):
        recipe["trigger"] = cfg["trigger"]
        recipe["offset_s"] = 0.0
    if cfg.get("vehicle"):
        recipe["vehicle"] = cfg["vehicle"]
    sim = {k: v for k, v in (cfg.get("sim") or {}).items() if v is not None}
    if sim:
        recipe["sim"] = sim
    if cfg.get("acc"):
        recipe["acc"] = cfg["acc"]
    return recipe


def fault_items(sc):
    """Mọi lỗi của kịch bản, theo thứ tự cố định. Khung "f" mang cờ đang-tiêm theo cùng thứ tự."""
    items = []
    for f in sc.lane_faults:
        it = dict(kind="lane", plan=None if f.trigger else [f.start_s, f.start_s + f.duration_s if f.duration_s else None],
                  trigger=f.trigger)
        if f.kind == "noise":
            it.update(short="Nhiễu vạch", label=f"Nhiễu vạch: σ c0 = {vn(f.sigma_c0 * 100)} cm, σ c1 = {vn(f.sigma_c1, 3)}")
        elif f.kind == "lose_line":
            it.update(short="Mất vạch", lost=list(f.lines), label="Mất vạch " + ", ".join(LINE_VI[i] for i in f.lines))
        elif f.kind == "c0_jump":
            it.update(short="c0 nhảy", label=f"c0 nhảy {vn(f.value, 2)} m, không có cờ")
        elif f.kind == "lose_all":
            it.update(short="Mất mọi biên", label="Mất mọi vạch và biên đường")
        elif f.kind in ("view_short", "view_flicker", "view_extend"):
            it.update(short="Tầm nhìn", label=f"Tầm nhìn lane model: {f.kind} {f.value:g} m")
        else:
            it.update(short=f.kind, label=f"Lỗi lane model: {f.kind}")
        items.append(it)
    for f in sc.channel_faults:
        ch = CH_VI.get(f.channel, f.channel)
        short, label = {
            "burst": ("Mất chuỗi gói", f"Mất {f.count} gói {ch} liên tiếp, cứ {f.every} gói một lần"),
            "drop": ("Mất gói", f"Mất 1 trong {f.every} gói {ch}"),
            "counter_stuck": ("Counter đứng yên", f"Counter {ch} đứng yên"),
            "counter_jump": ("Counter nhảy", f"Counter {ch} nhảy {f.count}"),
            "counter_repeat": ("Counter lặp", f"Counter {ch} lặp"),
            "future_stamp": ("Stamp sớm", f"Stamp {ch} sớm +{f.value:g} ms so với thời điểm nhận"),
            "crc": ("CRC sai", f"CRC sai trên khung {ch}"),
            "invalid": ("valid = false", f"valid = false trên {ch}"),
            "jitter": ("Jitter", f"Jitter ±{f.value:g} ms trên {ch}"),
            "late": ("Gói đến muộn", f"Gói {ch} đến muộn sau gói mới hơn"),
            "stop": ("Ngừng gửi", f"Ngừng gửi {ch}"),
            "out_of_range": ("Ngoài dải", f"{ch} ngoài dải: {f.field} = {f.value:g}"),
        }.get(f.kind, (f.kind, f"{f.kind} trên {ch}"))
        items.append(dict(kind="channel", short=short, label=label, trigger=f.trigger,
                          plan=None if f.trigger else [f.start_s, f.start_s + f.duration_s if f.duration_s else None]))
    for f in sc.sensor_faults:
        items.append(dict(kind="sensor", short=f"{f.signal} {f.kind}", label=f"Lỗi cảm biến {f.signal}: {f.kind} {f.value:g}",
                          trigger=f.trigger, plan=None if f.trigger else [f.start_s, None]))
    for f in sc.ego_motion_faults:
        items.append(dict(kind="ego", short="Ego-motion lỗi", label="Ego-motion không hợp lệ", trigger=None, plan=None))
    return items


def road_lines(road):
    """Bốn vạch L2, L1, R1, R2 của đường thật.

    Đường hằng số: độ lệch so với tim làn và kiểu vạch. Đường có hình học đoạn (làn đổi bề rộng, S6b):
    camera của sim lấy vạch theo hình học đó, nên gửi luôn đường vạch theo toạ độ thế giới."""
    lay = road.layout
    geo = lay.geometry
    if geo is None:
        return [None if m is None else dict(o=round(m.offset_m, 3), t=m.type.name) for m in lay.markings]
    from sim.world.road import lane_boundaries
    right, left = lane_boundaries(geo.id_at_index(0))
    out = []
    for boundary, side in zip((left + 1, left, right, right - 1), (1, 1, -1, -1)):
        paint = geo.paint_ahead(boundary, 0.0)
        if paint is None:
            out.append(None)
            continue
        xs, ys = road.marking_parallel(boundary, side, 0.0, road.length)
        segs, cur = [], []
        for k in range(0, len(xs), 10):   # mỗi 1 m; chỗ đứt quãng (hết sơn) thì tách đoạn
            if cur and math.hypot(float(xs[k]) - cur[-2], float(ys[k]) - cur[-1]) > 1.6:
                segs.append(cur)
                cur = []
            cur += [round(float(xs[k]), 2), round(float(ys[k]), 2)]
        if cur:
            segs.append(cur)
        o = geo.section_at(0.0).boundary_at(boundary, 0.0) - side * paint.width / 2
        out.append(dict(o=round(float(o), 3), t=paint.type.name, segs=segs))
    return out


def road_extent(road):
    """Giới hạn ngang của mặt đường theo từng mét, chỉ khi bề rộng đổi theo đoạn."""
    geo = road.layout.geometry
    if geo is None:
        return None
    lo, hi = [], []
    for k in range(int(road.length) + 1):
        a, b = geo.section_at(float(k)).extent(float(k))
        lo.append(round(float(a), 2))
        hi.append(round(float(b), 2))
    return dict(lo=lo, hi=hi)


def sim_conditions(sc):
    out = []
    if sc.camera_latency_ms != 100.0:
        out.append(f"Camera trễ {sc.camera_latency_ms:g} ms (mặc định 100 ms)")
    if sc.camera_jitter_ms:
        out.append(f"Camera jitter ±{sc.camera_jitter_ms:g} ms")
    if sc.road_mu != 1.0:
        out.append(f"Mặt đường ướt, μ = {vn(sc.road_mu)}")
    if sc.perception_noise_scale != 1.0:
        out.append(f"Nhiễu cảm biến vật thể ×{vn(sc.perception_noise_scale)}")
    if sc.eps_delay_s:
        out.append(f"Trễ EPS thật {sc.eps_delay_s * 1000:g} ms")
    return out


class Pace:
    """Nhịp thời gian thực: chờ tới lúc đồng hồ thật bằng thời gian mô phỏng chia cho tốc độ."""

    def __init__(self, rate):
        self.rate = rate
        self.paused = False
        self.cv = threading.Condition()
        self.anchor = None

    def command(self, msg):
        with self.cv:
            c = msg.get("cmd")
            if c == "pause":
                self.paused = True
            elif c == "resume":
                self.paused = False
            elif c == "rate":
                self.rate = max(0.0, float(msg.get("value", 1)))
            self.anchor = None
            self.cv.notify_all()

    def wait(self, t_sim):
        with self.cv:
            while True:
                if self.paused:
                    self.cv.wait()
                    continue
                if self.rate <= 0:       # tối đa: không canh nhịp
                    return
                now = time.monotonic()
                if self.anchor is None:
                    self.anchor = (now, t_sim)
                wall0, sim0 = self.anchor
                left = wall0 + (t_sim - sim0) / self.rate - now
                if left <= 0:
                    return
                self.cv.wait(timeout=left)


def path_points(trajectory):
    """x, y of the 31 path points in cm, or None when there is no full path."""
    if trajectory is None or len(trajectory.points) != 31:
        return None
    out = []
    for p in trajectory.points:
        out += [round(p.pose.x * 100), round(p.pose.y * 100)]
    return out


def system_share(eps, steering_angle):
    """Share of the steering done by the system, or None when no physical quantity defines it:
    with driver torque present the EPS stand-in has no motor torque to compare it with."""
    share = eps.system_steering_share
    if share == 1 and eps.controlling and eps.driver_torque:
        return None
    if not (share or eps.driver_torque or steering_angle or round(eps.driver_angle, 5)):
        return None
    return share


class LiveView:
    """Builds the frame of each planner cycle from the harness; reads, never writes. Display
    only: nothing here is scored (the evaluator runs on the RunLog after the run)."""

    def prepare(self, h):
        self.items = fault_items(h.scenario)
        self.s_rear = self.s_front = None
        self.lm_stamp = None
        self.ay_n = 0
        self.zi = self.sos = None
        self.road_view, self.road_changes = None, 0
        self.half_car = 0.5 * h.profile.width_with_mirrors
        # cùng thứ tự với fault_items: lane, channel (theo kênh), sensor, ego
        pos = {}
        self.channel_view = []
        for f in h.scenario.channel_faults:
            i = pos.get(f.channel, 0)
            pos[f.channel] = i + 1
            self.channel_view.append((f.channel, i))

    def active_flags(self, h, now_us):
        t = now_us * 1e-6
        flags = [int(f.active(t)) for f in h.lane_faults.faults]
        flags += [int(h._injectors[ch].faults[i].active(now_us)) for ch, i in self.channel_view]
        flags += [int(f.active(now_us)) for f in h.sensor_errors.faults[:len(h.scenario.sensor_faults)]]
        flags += [int(h.ego_faults.invalid(now_us))] * len(h.scenario.ego_motion_faults)
        return flags

    def lane_road(self, h):
        """Đường nhìn từ làn xe đang ở, như bên chấm dùng (làn đổi bề rộng, xe đã đổi làn)."""
        from eval import metrics
        changes = len(getattr(h.log, "lane_index_changes", None) or ())
        if self.road_view is None or changes != self.road_changes:
            self.road_view, self.road_changes = metrics.lane_relative(h.log).road, changes
        return self.road_view

    def clearance(self, road, x, y, s_hint):
        """Khoảng hở thật hai bên [m] từ xe tới biên làn tại vị trí (x, y) của bánh trước."""
        from eval import metrics
        from interfaces import Side
        front = road.project(x, y, s_hint)
        left = metrics._boundary_offset(road, Side.LEFT, front.s)
        right = metrics._boundary_offset(road, Side.RIGHT, front.s)
        return left - front.d - self.half_car, front.d - right - self.half_car

    def lane_model_points(self, h, msg):
        """Vạch và mép đường mà lane model báo cho planner, chuyển sang toạ độ thế giới.

        Lane model ở khung base_link tại lúc camera chụp. Stamp theo đồng hồ camera nên đổi về
        thời gian toàn cục rồi mới tra tư thế xe. Đa thức y = c0 + c1 x + c2 x^2 + c3 x^3 trong
        đoạn tầm nhìn; bỏ vạch LOST."""
        log = h.log
        capture_us = h.clocks["camera"].to_global(msg.header.stamp_us)
        i = min(max(bisect.bisect_left(log.t_us, capture_us), 0), len(log.t_us) - 1)
        rx, ry, yaw = log.rear[i]
        c, s = math.cos(yaw), math.sin(yaw)
        out = []
        for idx, ln in enumerate((*msg.lines, *msg.road_edges)):   # L2, L1, R1, R2, mép trái, mép phải
            if int(ln.status) == 2:
                continue
            a, b = max(0.0, ln.view_range_start), min(ln.view_range_end, 126.0)
            if not b > a:
                continue
            n = max(2, int((b - a) / 4.0) + 1)
            pts = []
            for j in range(n):
                x = a + (b - a) * j / (n - 1)
                y = ln.c0 + x * (ln.c1 + x * (ln.c2 + x * ln.c3))
                pts += [round(rx + x * c - y * s, 2), round(ry + x * s + y * c, 2)]
            # D đứt, S liền, B kép, U chưa rõ; mép đường: E gờ liền (CURB, BARRIER, GUARDRAIL, WALL), G cỏ sỏi hoặc chưa rõ
            kind = ("G" if int(ln.type) in (1, 5) else "E") if idx >= 4 else "DSBU"[int(ln.type)]
            out.append(dict(i=idx, p=int(int(ln.status) == 1), t=kind, pts=pts))
        return dict(ls=out)

    def frame(self, h, cyc, now_us):
        import numpy as np
        from scipy.signal import butter, sosfilt, sosfilt_zi
        from eval import metrics
        from sim.logging import run_log as RL
        log = h.log
        i = len(log.t_us) - 1
        rear, front = log.rear[i], log.front[i]
        pr = h.road.project(rear[0], rear[1], self.s_rear)
        pf = h.road.project(front[0], front[1], self.s_front)
        self.s_rear, self.s_front = pr.s, pf.s
        chunk = np.asarray(log.a_y[self.ay_n:i + 1], dtype=float)
        if self.sos is None:
            fs = 1e6 / max(1, (log.t_us[1] - log.t_us[0]) if len(log.t_us) > 1 else 1000)
            self.sos = butter(metrics.R79_FILTER_ORDER, metrics.R79_FILTER_HZ, btype="low", fs=fs, output="sos")
            self.zi = sosfilt_zi(self.sos) * chunk[0]
        filtered, self.zi = sosfilt(self.sos, chunk, zi=self.zi)
        self.ay_n = i + 1

        ps = RL._plain(cyc.path_status) if cyc.path_status is not None else {}
        tr = cyc.trajectory
        lm = cyc.lateral_limits
        fr = RL._plain(cyc.function_requests.message) if cyc.function_requests is not None else None
        lv = cyc.lane_view
        traj = path_points(tr) or [0] * 62
        chosen = ps.get("chosen", "LCC")
        other = cyc.ka_trajectory if chosen == "LCC" else cyc.lcc_trajectory
        lcc = RL._plain(cyc.lcc_status) if cyc.lcc_status is not None else None
        ka = RL._plain(cyc.intervention_status) if cyc.intervention_status is not None else None
        lead = cyc.lead_target.message if cyc.lead_target is not None else None
        lmodel = None
        rx = h._planner_view("lane_model", h.ch["lane_model"].latest)
        if rx is not None and rx.message.header.stamp_us != self.lm_stamp:   # chỉ gửi khi có frame camera mới
            self.lm_stamp = rx.message.header.stamp_us
            lmodel = self.lane_model_points(h, rx.message)
        objs = []
        for st in h.traffic.at(now_us * 1e-6):
            objs += [round(st.x, 2), round(st.y, 2), round(st.heading, 4)]
        steering_angle = round(h.eps.angle, 5)
        share = system_share(h.eps, steering_angle)
        road = self.lane_road(h)
        left, right = self.clearance(road, front[0], front[1], pf.s)
        capture_us = h.clocks["camera"].to_global(lv[0]) if lv else None
        return dict(
            type="f", t=round(now_us * 1e-6, 3),
            x=round(rear[0], 2), y=round(rear[1], 2), yaw=round(rear[2], 4),
            v=round(log.speed[i], 2), ay=round(log.a_y[i], 3), ayf=round(float(filtered[-1]), 3),
            whl=round(log.wheel_angle[i], 5), off=round(road.project(rear[0], rear[1], pr.s).d, 3),
            steering_angle=steering_angle, steering_system_share=share,
            dl=round(left, 3), dr=round(right, 3),
            fn=ps.get("active_function", "NONE"), lk=ps.get("lka_phase", "NONE"), el=ps.get("elk_phase", "NONE"),
            pv=int(bool(ps.get("path_valid"))), tv=int(bool(tr is not None and tr.header.valid)),
            lim=int(bool(ps.get("lateral_limit_reached"))), nar=int(bool(ps.get("lane_too_narrow"))),
            vmax=round(lm.v_max, 2) if lm is not None else None,
            dist=round(lm.distance, 1) if lm is not None else None,
            hor=round(tr.observed_horizon_s, 2) if tr is not None else None,
            cms=round(cyc.compute_ns * 1e-6, 3),
            view=round(lv[1], 1) if lv else None,
            age=round((now_us - capture_us) / 1e3, 1) if lv else None,
            rq=[r["state"] for r in fr["requests"]] if fr else ["—", "—", "—"],
            tlc=[r["tlc"] for r in fr["requests"][1:]] if fr else [None, None],
            ovr=int(bool(fr and fr.get("driver_override"))),
            traj=traj, tr=objs, fa=self.active_flags(h, now_us), lm=lmodel,
            ch=chosen, alt=path_points(other) if other is not None and other.header.valid else None,
            lcc=None if lcc is None else dict(v=int(bool(lcc["path_valid"])), m=lcc["lcc_mode"],
                                              d=round(lcc["follow_distance"], 1),
                                              lim=int(bool(lcc["lateral_limit_reached"])),
                                              nar=int(bool(lcc["lane_too_narrow"]))),
            ka=None if ka is None else dict(v=int(bool(ka["path_valid"])), f=ka["active_function"],
                                            lk=ka["lka_phase"], el=ka["elk_phase"],
                                            lim=int(bool(ka["lateral_limit_reached"]))),
            lead=None if lead is None else dict(id=lead.id, c=lead.classification.name, gap=round(lead.gap, 1),
                                                y=round(lead.y, 2), v=int(bool(lead.header.valid))),
            cl=round(cyc.compute_lcc_ns * 1e-6, 3), ck=round(cyc.compute_ka_ns * 1e-6, 3))


def init_message(h, recipe, planner, seed):
    import numpy as np
    from sim.vehicle.profiles import STEERING_RATIO
    sc = h.scenario
    road = h.road
    lay = road.layout
    step = 10
    prof = h.profile
    return dict(
        type="init", name=sc.name, desc=(sc.notes or {}).get("description", ""), dur=sc.duration_s, dt=0.025, seed=seed,
        pp=planner.version(),
        veh=dict(name=prof.name, wb=prof.wheelbase, w=prof.width_with_mirrors, lr=prof.lr, mass=prof.mass, sr=STEERING_RATIO),
        road=dict(len=round(road.length, 1), w=sc.lane_width,
                  x=np.round(road.x[::step], 2).tolist(), y=np.round(road.y[::step], 2).tolist(),
                  th=np.round(road.theta[::step], 4).tolist(),
                  lines=road_lines(road), ext=road_extent(road),
                  edges=[None if e is None else dict(o=round(e.offset_m, 3), t=e.type.name) for e in lay.edges]),
        tr=dict(dims=[[sp.length, sp.width] for sp in sc.traffic]),
        faults=fault_items(sc), conds=sim_conditions(sc),
        env=dict(rain=bool(sc.road_mu < 1.0 or sc.perception_noise_scale > 1.0)),
        acc=sc.acc, trigger=recipe.get("trigger") or None)


def done_message(result):
    r = result.to_dict()
    info = r["info"]
    keep = ("first_hwa_s", "hwa_share_after_request", "vehicle_offset_max_m", "free_space_each_side_m", "speed_min_mps",
            "decel_max_mps2", "ay_vehicle_r79_max", "jerk_vehicle_r79_max", "ay_vehicle_r79_over_sustained_s",
            "ay_vehicle_r79_limits", "fault_events_s", "faults_not_injected")
    return dict(type="done", res=dict(
        passed=r["passed"] is True, judged=r["passed"] is not None,
        criteria=[dict(id=c["id"], metric=c["metric"], value=c["value"], limit=c["limit"], passed=bool(c["passed"]),
                       first_fail_s=c.get("first_fail_s"))
                  for c in r["criteria"] if c["applicable"]],
        targets=[dict(id=c["id"], metric=c["metric"], value=c["value"], unit=c["unit"]) for c in r["targets"]],
        info={k: info.get(k) for k in keep}, failures=list(r.get("case_failures", [])),
        not_judged=[i["text"] for i in r["issues"] if i["kind"] == "not_judged"]),
        lim_ay=info.get("ay_vehicle_r79_limits") if info.get("ay_vehicle_r79_max") is not None else None)


def make_harness(scenario, planner, seed, emit=None, pace=None):
    """Harness with the LiveView observer: after each cycle the frame is built, the wall clock
    waited for (pace), then the frame sent (emit). Without emit and pace frames are dropped."""
    from sim.harness import Harness
    view = LiveView()

    def observer(h, now_us):
        frame = view.frame(h, h.log.cycles[-1], now_us)
        if pace is not None:
            pace.wait(now_us * 1e-6)
        if emit is not None:
            emit(frame)

    h = Harness(scenario, planner, seed, observer=observer)
    view.prepare(h)
    return h


def simulate(scenario, planner, seed):
    """The run as the live web runs it, at full speed, frames dropped (golden set, live path)."""
    return make_harness(scenario, planner, seed).run()


class Failure(Exception):
    def __init__(self, cls, message):
        super().__init__(message)
        self.cls = cls


def _blames_sut(error: BaseException) -> bool:
    return any("adapters" in f.filename and "sil" in f.filename for f in traceback.extract_tb(error.__traceback__))


def run(folder: Path) -> None:
    from eval import case, differential, metrics, planner_choice, run_bundle
    request = json.loads((folder / "request.json").read_text(encoding="utf-8"))
    cfg = request.get("config") or {}
    seed = int(request.get("seed", cfg.get("seed", 1)))
    expected_case = (request.get("expect") or {}).get("case_hash")  # set by a rerun (SIM-REQ-029)

    send(dict(type="phase", phase="resolve"))
    try:
        recipe = request.get("recipe") or recipe_from_config(cfg)
        scenario = case.resolve(recipe)
        doc = case.document(recipe, scenario)
        from execution import bundle
        bundle.write_json(folder / "resolved-case.json", doc)  # identity kept even if the run fails
        planner = planner_choice.resolve(None, request.get("planner_only"))
    except SystemExit as error:
        raise Failure("INFRA", str(error)) from error
    except Exception as error:  # noqa: BLE001  invalid request: no test result
        raise Failure("INFRA", f"{type(error).__name__}: {error}") from error
    if expected_case and doc["case_hash"] != expected_case:
        raise Failure("INFRA", f"Ca đã đổi: case_hash {doc['case_hash'][:12]} khác bản gốc {expected_case[:12]}")

    # T_timeout: 6 x the simulated duration + 30 s, wall clock without pauses (slowest rate 0.5x).
    send(dict(type="budget", timeout_s=6 * scenario.duration_s + 30))
    pace = Pace(float(request.get("rate", cfg.get("rate", 1))))
    threading.Thread(target=lambda: [pace.command(json.loads(line)) for line in sys.stdin if line.strip()],
                     daemon=True).start()
    try:
        h = make_harness(scenario, planner, seed, emit=send, pace=pace)
        send(init_message(h, recipe, planner, seed))
        send(dict(type="phase", phase="simulate"))
        log = h.run()
    except Exception as error:  # noqa: BLE001
        raise Failure("SUT_EXECUTION" if _blames_sut(error) else "SIM_ERROR",
                      f"{type(error).__name__}: {error}") from error

    send(dict(type="phase", phase="evaluate"))
    try:
        result = metrics.evaluate(log)
        result.criteria.extend(differential.criteria(h.scenario, log, planner, seed))
    except Exception as error:  # noqa: BLE001
        raise Failure("EVAL_ERROR", f"{type(error).__name__}: {error}") from error

    send(dict(type="phase", phase="write"))
    try:
        run_bundle.write(folder, run_id=request["run_id"], parent=request.get("parent_run_id"), kind="live",
                         doc=doc, planner=planner, seed=seed, log=log, result=result)
    except Exception as error:  # noqa: BLE001
        raise Failure("INFRA", f"{type(error).__name__}: {error}") from error
    send(done_message(result))


def main():
    global OUT
    OUT = sys.stdout
    sys.stdout = sys.stderr  # thư viện lỡ in gì thì không lẫn vào giao thức
    if len(sys.argv) >= 2 and sys.argv[1] == "catalog":
        try:
            send(catalog())
        except Exception as e:  # noqa: BLE001
            send(dict(type="error", message=f"{type(e).__name__}: {e}"))
        return
    if len(sys.argv) == 3 and sys.argv[1] == "run":
        faulthandler.enable(sys.stderr)  # a native crash leaves its Python stack in worker.log
        try:
            run(Path(sys.argv[2]))
        except BrokenPipeError:
            pass
        except Failure as error:
            traceback.print_exc()
            send(dict(type="error", **{"class": error.cls}, message=str(error)))
            raise SystemExit(3)
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
