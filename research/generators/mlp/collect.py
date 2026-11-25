"""Chạy teacher (qp_jerk_admm_teacher, build telemetry) trên các kịch bản của manifest, ghi bản ghi của các chu
kỳ được lấy mẫu vào build/lab/mlp/raw/<id>.npz. Mỗi kịch bản chạy trong tiến trình con riêng (eval.isolation),
cả lần chạy giữ slot của lab (bench/slots.py). Chạy lại thì bỏ qua kịch bản đã có file.

Cửa sổ = một chu kỳ generator được lấy mẫu: đặc trưng, nhãn và bài toán QP của chu kỳ đó. Lấy một chu kỳ trên
`stride` lần gọi generator, pha ngẫu nhiên theo seed của kịch bản, cộng các lần gọi EARLY (chu kỳ đầu sau khi
LCC bắt đầu lái: khởi động lạnh và quá độ, nơi warm start cũ chưa có hoặc kém), và cứ RARE_STRIDE lần gọi một
chu kỳ không nối path cũ (sau override của tài xế): điều kiện hiếm nhưng thật, cần có trong miền của MLP.
"""

import argparse
import json
import resource
import time

import numpy as np

import common
from common import OUT, TEACHER, TR, TR_DOUBLES

RAW = OUT / "raw"
TIMEOUT_S = 900
EARLY = (1, 3, 6)
RARE_STRIDE = 3  # Chu kỳ không nối path cũ (bắt đầu, override): lấy dày hơn để có trong miền.


RAW_DAGGER = OUT / "raw_dagger"


def build_teacher(drive: str = "qp"):
    """drive = "mlp": vòng DAgger, teacher lái bằng MLP hiện có của mlp_jerk_direct (model/weights.h)."""
    from eval import sweep
    cmake = (("PP_T7", "lab"), ("PP_T7_LAB", TEACHER), ("PP_T7_TELEMETRY", "ON"),
             ("TEACHER_DRIVE_MLP", "ON" if drive == "mlp" else "OFF"))
    return sweep._build(sweep.CalSet("teacher", {}, cmake), OUT / ("teacher-mlp" if drive == "mlp" else "teacher"))


def run_one(spec: dict, lib_dir: str, out_file: str, stride: int) -> dict:
    from pathlib import Path

    from adapters.sil.sil_planner import PlannerLibraries
    from eval import telemetry
    from sim.harness import Harness

    import scenarios
    phase = int(np.random.default_rng(spec["seed"]).integers(stride))
    kept, last = [], [None]
    calls = {"n": 0, "label_ok": 0, "drive_ok": 0}

    def capture(raw: bytes) -> None:
        rec = np.frombuffer(raw[:TR_DOUBLES * 8], dtype=np.float64)
        if rec[TR["LAYOUT"]] != common.LAYOUT:  # Generator chưa chạy lần nào: ws còn 0.
            return
        if rec[TR["SIZE"]] != TR_DOUBLES:
            raise RuntimeError("teacher record layout differs from common.py")
        if rec[TR["COUNT"]] == last[0]:
            return
        last[0] = rec[TR["COUNT"]]
        calls["n"] += 1
        calls["label_ok"] += int(rec[TR["LABEL_OK"]] == 1.0)
        calls["drive_ok"] += int(rec[TR["DRIVE_OK"]] == 1.0)
        rare = rec[TR["FROM_OLD"]] == 0.0 and calls["n"] % RARE_STRIDE == 0
        if calls["n"] in EARLY or rare or (calls["n"] + phase) % stride == 0:
            kept.append(np.array(rec, copy=True))

    t0, c0 = time.time(), time.process_time()
    planner = telemetry.Recording(PlannerLibraries.at(Path(lib_dir)), capture=capture)
    log = Harness(scenarios.to_scenario(spec), planner, spec["seed"]).run()
    cycles = len(log.cycles)
    del log
    records = np.stack(kept) if kept else np.zeros((0, TR_DOUBLES))
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_file, records=records, spec=json.dumps(spec))
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return {"id": spec["id"], "cycles": cycles, "calls": calls["n"], "label_ok": calls["label_ok"],
            "drive_ok": calls["drive_ok"], "windows": len(kept), "wall_s": time.time() - t0,
            "cpu_s": time.process_time() - c0, "maxrss_mb": rss / (1 << 20 if rss > 1 << 24 else 1 << 10)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect teacher records for the MLP data")
    parser.add_argument("--drive", choices=("qp", "mlp"), default="qp", help="mlp: DAgger round")
    parser.add_argument("--manifest")
    parser.add_argument("--stride", type=int, default=14)
    parser.add_argument("--limit", type=int, help="Only the first N scenarios of each split (tiny run)")
    parser.add_argument("--log")
    args = parser.parse_args()
    dagger = args.drive == "mlp"
    raw = RAW_DAGGER if dagger else RAW
    args.manifest = args.manifest or str(OUT / ("manifest_dagger.json" if dagger else "manifest.json"))
    args.log = args.log or str(OUT / ("collect_dagger.jsonl" if dagger else "collect.jsonl"))
    import slots
    from eval import isolation
    specs = json.loads(open(args.manifest, encoding="utf-8").read())["scenarios"]
    if args.limit:
        chosen = []
        for split in ("train", "validation", "ood"):
            chosen += [s for s in specs if s["split"] == split][:args.limit]
        specs = chosen
    with slots.hold(1, "mlp data"):
        lib = build_teacher(args.drive)
        tasks = [(s, str(lib), str(raw / f"{s['id']}.npz"), args.stride) for s in specs
                 if not (raw / f"{s['id']}.npz").exists()]
        print(f"{len(tasks)} scenarios to run ({len(specs) - len(tasks)} already done)", flush=True)
        start = time.time()
        with open(args.log, "a", encoding="utf-8") as log:
            for (spec, *_), (status, value) in zip(tasks, isolation.map_isolated(run_one, tasks, 1, TIMEOUT_S)):
                row = value if status == "ok" else {"id": spec["id"], "status": status, "error": str(value)[:400]}
                log.write(json.dumps(row) + "\n")
                log.flush()
                print(json.dumps(row), flush=True)
        print(f"done in {time.time() - start:.0f} s")


if __name__ == "__main__":
    main()
