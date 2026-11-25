"""Bộ sinh kịch bản riêng cho dữ liệu MLP luồng C (PP-TS-031).

- Họ hình học đường riêng (FAMILIES), không lấy từ benchmark. Cấu hình nhiễu lane model riêng (NOISE).
- Trong miền: tốc độ 40–100 km/h, VP-0/1/2, seed harness từ 100. Ngoài miền (chỉ để kiểm, báo riêng):
  110–130 km/h với VP-0/1/2, và 40–100 km/h với VP-3/5.
- Chia train/validation theo ô (họ đường, cấu hình nhiễu) trước khi trích cửa sổ: mỗi họ có đúng một cấu hình
  nhiễu ở validation, mỗi cấu hình nhiễu có ở validation ít nhất một họ; validation không có ô nào của train.
- Loại tường minh mọi ca giống ca, anchor hay biến thể của PP-T7 (excluded()).
"""

import argparse
import json
import math

import numpy as np

from common import OUT, ROOT, sha256_json  # noqa: F401  (ROOT nạp sys.path)

FAMILIES = ("straight_offset", "single_curve", "s_curve", "curvature_chain", "truck_offset")
NOISE = {  # Không trùng mức F01 a/b/c (0,03/0,045/0,075).
    "N0": None,
    "N1": (0.02, 0.0012),
    "N2": (0.04, 0.0025),
    "N3": (0.06, 0.004),
}
NOISE_NAMES = tuple(NOISE)
# Ô validation: họ i ↔ cấu hình nhiễu (i mod 4); họ thứ 5 lấy N1 để mọi cấu hình đều có ở validation.
VALIDATION_CELLS = {(f, NOISE_NAMES[i % 4]) for i, f in enumerate(FAMILIES[:4])} | {(FAMILIES[4], "N2")}
IN_PROFILES = ("VP-0", "VP-1", "VP-2")
OOD_PROFILES = ("VP-3", "VP-5")
SEED_IN = 100
SEED_OOD = 5000
MASTER_SEED = 100
DURATION_S = 20.0
R_MIN, R_MAX = 180.0, 3000.0


def _radius(rng) -> float:
    return float(math.exp(rng.uniform(math.log(R_MIN), math.log(R_MAX))))


def _geometry(family: str, rng, v: float, lane: float) -> tuple[list, dict]:
    """Đoạn đường (kind, length, curvature_end) và tham số riêng của họ."""
    need = v * DURATION_S + 250.0
    extra = {}
    sign = 1.0 if rng.random() < 0.5 else -1.0
    if family == "straight_offset":
        segs = [("straight", need + 200.0, 0.0)]
        extra["start_offset_m"] = float(sign * rng.uniform(0.1, 0.7))
        extra["start_heading_rad"] = float(math.radians(rng.uniform(-2.0, 2.0)))
        extra["hold_until_hwa"] = bool(rng.random() < 0.7)
    elif family == "single_curve":
        k = sign / _radius(rng)
        lead = rng.uniform(60.0, 220.0)
        clo = rng.uniform(30.0, 160.0)
        segs = [("straight", lead, 0.0), ("clothoid", clo, k), ("arc", rng.uniform(80.0, 400.0), k),
                ("clothoid", rng.uniform(30.0, 160.0), 1e-12), ("straight", need, 0.0)]
    elif family == "s_curve":
        k1, k2 = sign / _radius(rng), -sign / _radius(rng)
        segs = [("straight", rng.uniform(60.0, 200.0), 0.0), ("clothoid", rng.uniform(15.0, 120.0), k1),
                ("arc", rng.uniform(5.0, 250.0), k1), ("clothoid", rng.uniform(10.0, 80.0), 1e-12),
                ("clothoid", rng.uniform(15.0, 120.0), k2), ("arc", rng.uniform(5.0, 250.0), k2),
                ("clothoid", rng.uniform(15.0, 120.0), 1e-12), ("straight", need, 0.0)]
    elif family == "curvature_chain":
        segs = [("straight", rng.uniform(40.0, 150.0), 0.0)]
        k = 0.0
        for _ in range(int(rng.integers(4, 8))):
            k = float(np.clip(k + rng.normal(0.0, 1.0 / 600.0), -1.0 / R_MIN, 1.0 / R_MIN))
            segs.append(("clothoid", rng.uniform(30.0, 150.0), k if abs(k) > 1e-9 else 1e-12))
            if rng.random() < 0.5:
                segs.append(("arc", rng.uniform(20.0, 200.0), segs[-1][2]))
        segs += [("clothoid", rng.uniform(40.0, 120.0), 1e-12), ("straight", need, 0.0)]
    elif family == "truck_offset":
        k = 0.0 if rng.random() < 0.5 else sign / rng.uniform(600.0, R_MAX)
        segs = [("straight", rng.uniform(60.0, 200.0), 0.0)]
        if k:
            segs += [("clothoid", rng.uniform(60.0, 150.0), k), ("arc", need, k)]
        else:
            segs += [("straight", need, 0.0)]
        side = 1.0 if rng.random() < 0.5 else -1.0
        extra["truck"] = dict(s0=float(rng.uniform(40.0, 110.0)), d=float(side * (lane + rng.uniform(-0.35, 0.1))),
                              slower=float(rng.uniform(1.0, 9.0)), width=float(rng.uniform(2.3, 2.55)))
    else:
        raise ValueError(family)
    return [(kind, float(length), float(kappa)) for kind, length, kappa in segs], extra


def sample(index: int, rng, family: str, noise: str, split: str, ood: str | None = None, prefix: str = "g") -> dict:
    if ood == "speed":
        v_kmh, profile = rng.uniform(110.0, 130.0), str(rng.choice(IN_PROFILES))
    elif ood == "profile":
        v_kmh, profile = rng.uniform(40.0, 100.0), str(rng.choice(OOD_PROFILES))
    else:
        v_kmh, profile = rng.uniform(40.0, 100.0), str(rng.choice(IN_PROFILES))
    v = v_kmh / 3.6
    lane = float(rng.uniform(2.75, 5.0))
    segs, extra = _geometry(family, rng, v, lane)
    acc = str(rng.choice(["off", "on", "ignore_limits"], p=[0.5, 0.3, 0.2]))
    loop = "open" if rng.random() < 0.2 else "closed"
    # Tài xế override ngắn (1–2 lần, 0,3–1,2 s): chu kỳ start_from_car, không có path cũ, rồi bắt lại path.
    overrides = []
    if rng.random() < 0.5:
        t = rng.uniform(4.0, 9.0)
        for _ in range(int(rng.integers(1, 3))):
            dur = rng.uniform(0.3, 1.2)
            overrides.append([float(t), float(dur)])
            t += dur + rng.uniform(2.0, 6.0)
        overrides = [o for o in overrides if o[0] + o[1] < DURATION_S - 2.0]
    seed = (SEED_OOD if ood else SEED_IN) + index
    return dict(id=f"{'ood' if ood else prefix}{index:04d}", family=family, noise=noise, split=split, ood=ood,
                seed=int(seed), speed_mps=float(v), profile=profile, lane_width=lane, acc=acc, loop=loop,
                segments=segs, overrides=overrides, **extra)


def to_scenario(spec: dict):
    from sim.faults.lane import LaneFault
    from sim.scenario import Scenario
    from sim.world.road import Segment
    from sim.world.traffic import TrafficSpec
    faults = ()
    if NOISE[spec["noise"]] is not None:
        c0, c1 = NOISE[spec["noise"]]
        faults = (LaneFault(kind="noise", sigma_c0=c0, sigma_c1=c1),)
    traffic = ()
    if "truck" in spec:
        t = spec["truck"]
        traffic = (TrafficSpec(id=1, s0=t["s0"], d=t["d"], speed=spec["speed_mps"] - t["slower"], length=12.0,
                               width=t["width"], kind="TRUCK"),)
    events = []
    if spec.get("overrides"):
        from interfaces import CancelReason, ElkReason, FunctionRequest, RequestState, Side
        from sim.stand_ins.scripted import RequestEvent
        hwa = FunctionRequest(RequestState.REQUEST, Side.NONE, math.inf, ElkReason.NONE, CancelReason.NONE)
        off = FunctionRequest(RequestState.OFF, Side.NONE, math.inf, ElkReason.NONE, CancelReason.NONE)
        for t, dur in spec["overrides"]:
            events.append(RequestEvent(round(t * 1e6), (hwa, off, off), True))
            events.append(RequestEvent(round((t + dur) * 1e6), (hwa, off, off), False))
    return Scenario(name=f"mlp-{spec['id']}", request_events=tuple(events), segments=tuple(Segment(k, l, c) for k, l, c in spec["segments"]),
                    lane_width=spec["lane_width"], speed_mps=spec["speed_mps"], profile=spec["profile"],
                    duration_s=DURATION_S, start_offset_m=spec.get("start_offset_m", 0.0),
                    start_heading_rad=spec.get("start_heading_rad", 0.0),
                    hold_until_hwa=spec.get("hold_until_hwa", False), acc=spec["acc"], loop=spec["loop"],
                    lane_faults=faults, traffic=traffic, object_list_on_empty_road=True,
                    notes={"expected_outcome": "drive"})


# --- Loại PP-T7 tường minh ---------------------------------------------------------------------------

def _signature(sc) -> dict:
    return dict(kinds=[s.kind for s in sc.segments], kappa=[s.curvature_end for s in sc.segments],
                length=[s.length for s in sc.segments], v=sc.speed_mps, lane=sc.lane_width,
                traffic=sorted((t.speed, t.d) for t in sc.traffic))


def pp_t7_signatures() -> list[dict]:
    """Mọi lượt của PP-T7 (tuning và test) và mọi anchor của các kịch bản PP-T7 dùng."""
    from eval import loader, openx, sweep
    suite = sweep.load_suite("PP-T7")
    sigs, families = [], set()
    for part in ("tuning", "test"):
        for run in suite[part]["runs"]:
            sigs.append(_signature(sweep.load_run(run)))
            families.add(sweep.split_run(run)[0][0])
    for fam in sorted(families):
        for variant in openx.anchors(ROOT / "benchmark" / "scenarios" / f"{fam}.xosc"):
            sigs.append(_signature(loader.load(fam, variant)))
    return sigs


def _close(a: float, b: float, rel: float, abs_: float) -> bool:
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def excluded(spec: dict, sigs: list[dict]) -> bool:
    """Trùng một ca PP-T7 khi cùng chuỗi loại đoạn, độ cong và chiều dài lệch ≤ 5 %, tốc độ ≤ 1 km/h, làn ≤ 0,1 m.
    Ngoài ra loại mọi ca thẳng có xe tải mà tốc độ và chênh tốc độ gần S3 (≤ 1 km/h, ≤ 0,5 m/s)."""
    sc = to_scenario(spec)
    mine = _signature(sc)
    for s in sigs:
        if not (_close(mine["v"], s["v"], 0.0, 1.0 / 3.6) and _close(mine["lane"], s["lane"], 0.0, 0.1)):
            continue
        if mine["kinds"] == s["kinds"] and all(_close(a, b, 0.05, 1e-6) for a, b in zip(mine["kappa"], s["kappa"])) \
                and all(_close(a, b, 0.05, 1.0) for a, b in zip(mine["length"][:-1], s["length"][:-1])):
            return True
        if mine["traffic"] and s["traffic"] and all(k == "straight" for k in mine["kinds"]) and any(
                abs((mine["v"] - mt[0]) - (s["v"] - st[0])) <= 0.5 for mt in mine["traffic"] for st in s["traffic"]):
            return True
    return False


def manifest(per_cell: int, ood_count: int) -> dict:
    rng = np.random.default_rng(MASTER_SEED)
    sigs = pp_t7_signatures()
    specs, rejected = [], []
    index = 0
    for family in FAMILIES:
        for noise in NOISE_NAMES:
            split = "validation" if (family, noise) in VALIDATION_CELLS else "train"
            made = 0
            while made < per_cell:
                spec = sample(index, rng, family, noise, split)
                index += 1
                if excluded(spec, sigs):
                    rejected.append(spec["id"])
                    continue
                specs.append(spec)
                made += 1
    ood_rng = np.random.default_rng(MASTER_SEED + 1)
    for i in range(ood_count):
        family = FAMILIES[i % len(FAMILIES)]
        noise = NOISE_NAMES[(i // len(FAMILIES)) % len(NOISE_NAMES)]
        spec = sample(i, ood_rng, family, noise, "ood", "speed" if i % 2 == 0 else "profile")
        if excluded(spec, sigs):
            rejected.append(spec["id"])
            continue
        specs.append(spec)
    return {"master_seed": MASTER_SEED, "families": list(FAMILIES), "noise": {k: v for k, v in NOISE.items()},
            "validation_cells": sorted(map(list, VALIDATION_CELLS)), "pp_t7_signatures": len(sigs),
            "excluded_as_pp_t7": rejected, "scenarios": specs}


DAGGER_INDEX = 1000  # Kịch bản DAgger: id d1000…, seed 1100…, không trùng bộ đầu (100…219) hay OOD (5000…).


def dagger_manifest(per_cell: int) -> dict:
    """Kịch bản mới cho vòng DAgger, cùng họ đường, cùng ô (họ, nhiễu) và cùng cách chia train/validation."""
    rng = np.random.default_rng(MASTER_SEED + 2)
    sigs = pp_t7_signatures()
    specs, rejected = [], []
    index = DAGGER_INDEX
    for family in FAMILIES:
        for noise in NOISE_NAMES:
            split = "validation" if (family, noise) in VALIDATION_CELLS else "train"
            made = 0
            while made < per_cell:
                spec = sample(index, rng, family, noise, split, prefix="d")
                index += 1
                if excluded(spec, sigs):
                    rejected.append(spec["id"])
                    continue
                specs.append(spec)
                made += 1
    return {"master_seed": MASTER_SEED + 2, "dagger": True, "families": list(FAMILIES),
            "validation_cells": sorted(map(list, VALIDATION_CELLS)), "pp_t7_signatures": len(sigs),
            "excluded_as_pp_t7": rejected, "scenarios": specs}


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the scenario manifest of the MLP data")
    parser.add_argument("--per-cell", type=int, default=6)
    parser.add_argument("--ood", type=int, default=16)
    parser.add_argument("--dagger", action="store_true", help="Scenarios of the DAgger round instead")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    if args.out is None:
        args.out = str(OUT / ("manifest_dagger.json" if args.dagger else "manifest.json"))
    m = dagger_manifest(args.per_cell) if args.dagger else manifest(args.per_cell, args.ood)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
    by = {}
    for s in m["scenarios"]:
        by[s["split"]] = by.get(s["split"], 0) + 1
    print(f"{args.out}: {by}; excluded as PP-T7: {len(m['excluded_as_pp_t7'])}; hash {sha256_json(m)[:12]}")


if __name__ == "__main__":
    main()
