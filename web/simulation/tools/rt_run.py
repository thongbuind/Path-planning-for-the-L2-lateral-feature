#!/usr/bin/env python3
"""Chạy planner thật theo thời gian thực, đẩy từng chu kỳ ra stdout (NDJSON).

Chỉ ĐỌC repo (eval/, sim/, adapters/, benchmark/, build/planner). Không ghi file nào.

    rt_run.py catalog                 danh mục: kịch bản, lỗi và mức lỗi, tổ hợp, xe
    rt_run.py run '<json cấu hình>'   chạy một lượt; lệnh điều khiển đọc từ stdin, mỗi dòng một JSON:
                                      {"cmd":"pause"} {"cmd":"resume"} {"cmd":"rate","value":2}

Một lượt chạy là Harness của sim (cùng simulator, cùng mô hình cảm biến, cùng lỗi tiêm như
eval.runner) với planner là libpp_planner. Harness được kế thừa ngay trong file này: sau mỗi lần
planner.step() (chu kỳ 25 ms) ta lấy kết quả của chu kỳ đó, chờ cho kịp đồng hồ thật rồi mới gửi đi.
Nên pp_step() được gọi lần lượt theo thời gian thực, không có gì được tính trước.

Giao thức, mỗi dòng một đối tượng JSON, trường "type":
    init   thông tin tĩnh của lượt chạy: đường, xe, danh sách lỗi, thời lượng
    f      một chu kỳ planner: output của planner và ground truth của simulator
    done   kết luận của evaluator (tiêu chí, chỉ tiêu) sau khi chạy hết
    error  lỗi
"""

import bisect
import json
import math
import os
import re
import sys
import threading
import time
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO))
os.chdir(REPO)

OUT = sys.stdout
sys.stdout = sys.stderr  # thư viện lỡ in gì thì không lẫn vào giao thức


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
        return "HWA"
    return "Khác"


def catalog():
    import glob
    import yaml
    from eval import loader, openx
    from sim.vehicle.profiles import PROFILES

    sids = sorted({os.path.basename(p).split(".")[0] for p in glob.glob(str(REPO / "benchmark/scenarios/S*.xosc"))},
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
    for path in sorted((REPO / "benchmark/faults").glob("F*.xosc")):
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
    for path in sorted((REPO / "benchmark/combinations").glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        combos.append(dict(id=data["id"], title=data["title"], faults=[list(f) for f in data["faults"]],
                           sim=data.get("sim", {}), hosts=[list(h) for h in data["hosts"]]))

    vehicles = [dict(id=p.name, wb=p.wheelbase, w=p.width_with_mirrors, mass=p.mass) for p in PROFILES.values()]
    from adapters.sil.sil_planner import library_path, library_version
    try:
        pp = library_version(library_path())
    except Exception as e:  # noqa: BLE001
        pp = f"không đọc được: {e}"
    return dict(scenarios=scenarios, faults=faults, combos=combos, vehicles=vehicles,
                triggers=["lka_active", "elk_active", "intervention_active"],
                acc=["off", "on", "ignore_limits"], pp=pp)


# ---------------------------------------------------------------------------------------
# Một lượt chạy
# ---------------------------------------------------------------------------------------

SIM_KEYS = {"road_mu": (0.1, 1.0), "camera_latency_ms": (0.0, 500.0), "perception_noise_scale": (0.0, 10.0)}
LINE_VI = {0: "trái ngoài (L2)", 1: "trái làn mình (L1)", 2: "phải làn mình (R1)", 3: "phải ngoài (R2)"}
CH_VI = {"lane_model": "lane model", "object_list": "object list", "imu": "IMU", "steering": "góc lái",
         "speed": "tốc độ", "vehicle_state": "vehicle state", "function_requests": "FunctionRequests",
         "longitudinal_plan": "LongitudinalPlan"}


def build_scenario(cfg):
    from eval import loader
    sid, v = cfg["scenario"]["sid"], cfg["scenario"]["v"]
    if not (re.fullmatch(r"S\d+[a-z]?", sid) and re.fullmatch(r"[a-z]", v)):
        raise ValueError("kịch bản không hợp lệ")
    sc = loader.load(sid, v)
    trigger = cfg.get("trigger") or None
    for fid, level in cfg.get("faults", []):
        if not (re.fullmatch(r"F\d{2}", fid) and re.fullmatch(r"[a-z]", level)):
            raise ValueError("lỗi không hợp lệ")
        sc = loader.with_fault(sc, fid, level, trigger, 0.0)
    veh = cfg.get("vehicle")
    if veh:
        from sim.vehicle.profiles import PROFILES
        if veh not in PROFILES:
            raise ValueError("xe không hợp lệ")
        sc = replace(sc, profile=veh)
    sim = {}
    for k, (lo, hi) in SIM_KEYS.items():
        if cfg.get("sim", {}).get(k) is not None:
            x = float(cfg["sim"][k])
            if not lo <= x <= hi:
                raise ValueError(f"{k} ngoài dải")
            sim[k] = x
    if sim:
        sc = replace(sc, **sim)
    acc = cfg.get("acc") or None
    if acc:
        if acc not in ("off", "on", "ignore_limits"):
            raise ValueError("acc không hợp lệ")
        sc = replace(sc, acc=acc)
    return replace(sc, name=f"{sid}{v}")


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


def run(cfg):
    import numpy as np
    from scipy.signal import butter, sosfilt, sosfilt_zi
    from adapters.sil.sil_planner import library_version
    from eval import differential, metrics, planner_choice
    from sim.harness import Harness
    from sim.logging import run_log as RL

    sc = build_scenario(cfg)
    seed = int(cfg.get("seed", 1))
    planner = planner_choice.resolve(None)
    pace = Pace(float(cfg.get("rate", 1)))
    threading.Thread(target=control_loop, args=(pace,), daemon=True).start()

    class Live(Harness):
        def _planner(self, now_us):
            super()._planner(now_us)
            frame = self.frame(self.log.cycles[-1], now_us)
            pace.wait(now_us * 1e-6)
            send(frame)

        def prepare(self):
            self.items = fault_items(self.scenario)
            self.s_rear = self.s_front = None
            self.lm_stamp = None
            self.ay_n = 0
            self.zi = self.sos = None
            self.half_lane = 0.5 * self.road.lane_width
            self.half_car = 0.5 * self.profile.width_with_mirrors
            sc_ = self.scenario
            # cùng thứ tự với fault_items: lane, channel (theo kênh), sensor, ego
            pos = {}
            self.channel_view = []
            for f in sc_.channel_faults:
                i = pos.get(f.channel, 0)
                pos[f.channel] = i + 1
                self.channel_view.append((f.channel, i))

        def active_flags(self, now_us):
            t = now_us * 1e-6
            flags = [int(f.active(t)) for f in self.lane_faults.faults]
            flags += [int(self._injectors[ch].faults[i].active(now_us)) for ch, i in self.channel_view]
            flags += [int(f.active(now_us)) for f in self.sensor_errors.faults[:len(self.scenario.sensor_faults)]]
            flags += [int(self.ego_faults.invalid(now_us))] * len(self.scenario.ego_motion_faults)
            return flags

        def lane_model_points(self, msg):
            """Vạch và mép đường mà lane model báo cho planner, chuyển sang toạ độ thế giới.

            Lane model ở khung base_link tại lúc camera chụp (stamp), nên đặt theo tư thế xe lúc đó.
            Đa thức y = c0 + c1 x + c2 x^2 + c3 x^3 trong đoạn tầm nhìn; bỏ vạch LOST."""
            log = self.log
            i = min(max(bisect.bisect_left(log.t_us, msg.header.stamp_us), 0), len(log.t_us) - 1)
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

        def frame(self, cyc, now_us):
            log = self.log
            i = len(log.t_us) - 1
            rear, front = log.rear[i], log.front[i]
            pr = self.road.project(rear[0], rear[1], self.s_rear)
            pf = self.road.project(front[0], front[1], self.s_front)
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
            traj = []
            if tr is not None:
                for p in tr.points:
                    traj += [round(p.pose.x * 100), round(p.pose.y * 100)]
            if len(traj) != 62:
                traj = [0] * 62
            lmodel = None
            rx = self._planner_view("lane_model", self.ch["lane_model"].latest)
            if rx is not None and rx.message.header.stamp_us != self.lm_stamp:   # chỉ gửi khi có frame camera mới
                self.lm_stamp = rx.message.header.stamp_us
                lmodel = self.lane_model_points(rx.message)
            objs = []
            for st in self.traffic.at(now_us * 1e-6):
                objs += [round(st.x, 2), round(st.y, 2), round(st.heading, 4)]
            steering_angle = round(self.eps.angle, 5)
            system_share = self.eps.system_steering_share
            if system_share == 1 and self.eps.controlling and self.eps.driver_torque:
                # Driver torque is present, but the EPS stand-in has no motor torque to compare it with.
                system_share = 0.5
            elif not (system_share or self.eps.driver_torque or steering_angle or round(self.eps.driver_angle, 5)):
                system_share = None
            return dict(
                type="f", t=round(now_us * 1e-6, 3),
                x=round(rear[0], 2), y=round(rear[1], 2), yaw=round(rear[2], 4),
                v=round(log.speed[i], 2), ay=round(log.a_y[i], 3), ayf=round(float(filtered[-1]), 3),
                whl=round(log.wheel_angle[i], 5), off=round(pr.d, 3),
                steering_angle=steering_angle, steering_system_share=system_share,
                dl=round(self.half_lane - pf.d - self.half_car, 3), dr=round(self.half_lane + pf.d - self.half_car, 3),
                fn=ps.get("active_function", "NONE"), lk=ps.get("lka_phase", "NONE"), el=ps.get("elk_phase", "NONE"),
                pv=int(bool(ps.get("path_valid"))), tv=int(bool(tr is not None and tr.header.valid)),
                lim=int(bool(ps.get("lateral_limit_reached"))), nar=int(bool(ps.get("lane_too_narrow"))),
                vmax=round(lm.v_max, 2) if lm is not None else None,
                dist=round(lm.distance, 1) if lm is not None else None,
                hor=round(tr.observed_horizon_s, 2) if tr is not None else 0.0,
                cms=round(cyc.compute_ns * 1e-6, 3),
                view=round(lv[1], 1) if lv else None,
                age=round(now_us / 1e3 - lv[0] / 1e3, 1) if lv else None,
                rq=[r["state"] for r in fr["requests"]] if fr else ["OFF", "OFF", "OFF"],
                tlc=[r["tlc"] for r in fr["requests"][1:]] if fr else [None, None],
                ovr=int(bool(fr and fr.get("driver_override"))),
                traj=traj, tr=objs, fa=self.active_flags(now_us), lm=lmodel)

    h = Live(sc, planner, seed)
    h.prepare()
    road = h.road
    lay = road.layout
    step = 10
    prof = h.profile
    from sim.vehicle.profiles import STEERING_RATIO
    items = h.items
    send(dict(
        type="init", name=sc.name, desc=(sc.notes or {}).get("description", ""), dur=sc.duration_s, dt=0.025, seed=seed,
        pp=library_version(planner.path),
        veh=dict(name=prof.name, wb=prof.wheelbase, w=prof.width_with_mirrors, lr=prof.lr, mass=prof.mass, sr=STEERING_RATIO),
        road=dict(len=round(road.length, 1), w=sc.lane_width,
                  x=np.round(road.x[::step], 2).tolist(), y=np.round(road.y[::step], 2).tolist(),
                  th=np.round(road.theta[::step], 4).tolist(),
                  lines=road_lines(road), ext=road_extent(road),
                  edges=[None if e is None else dict(o=round(e.offset_m, 3), t=e.type.name) for e in lay.edges]),
        tr=dict(dims=[[sp.length, sp.width] for sp in sc.traffic]),
        faults=items, conds=sim_conditions(sc),
        env=dict(rain=bool(sc.road_mu < 1.0 or sc.perception_noise_scale > 1.0)),
        acc=sc.acc, trigger=cfg.get("trigger") or None))

    log = h.run()
    result = metrics.evaluate(log)
    result.criteria.extend(differential.criteria(h.scenario, log, planner, seed))
    r = result.to_dict()
    info = r["info"]
    keep = ("first_hwa_s", "hwa_share_after_request", "vehicle_offset_max_m", "free_space_each_side_m", "speed_min_mps",
            "decel_max_mps2", "ay_vehicle_r79_max", "jerk_vehicle_r79_max", "ay_vehicle_r79_over_sustained_s",
            "ay_vehicle_r79_limits")
    send(dict(type="done", res=dict(
        passed=bool(r["passed"]),
        criteria=[dict(id=c["id"], metric=c["metric"], value=c["value"], limit=c["limit"], passed=bool(c["passed"]))
                  for c in r["criteria"] if c["applicable"]],
        targets=[dict(id=c["id"], metric=c["metric"], value=c["value"], unit=c["unit"]) for c in r["targets"]],
        info={k: info.get(k) for k in keep}, failures=list(r.get("case_failures", []))),
        lim_ay=info.get("ay_vehicle_r79_limits") if info.get("ay_vehicle_r79_max") is not None else None))


def control_loop(pace):
    for line in sys.stdin:
        try:
            pace.command(json.loads(line))
        except Exception:  # noqa: BLE001
            pass


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "catalog":
        try:
            send(catalog())
        except Exception as e:  # noqa: BLE001
            send(dict(type="error", message=f"{type(e).__name__}: {e}"))
        return
    if len(sys.argv) == 3 and sys.argv[1] == "run":
        try:
            run(json.loads(sys.argv[2]))
        except BrokenPipeError:
            pass
        except SystemExit as e:
            send(dict(type="error", message=str(e)))
        except Exception as e:  # noqa: BLE001
            send(dict(type="error", message=f"{type(e).__name__}: {e}"))
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
