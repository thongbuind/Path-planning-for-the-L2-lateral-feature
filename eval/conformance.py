"""B0 planner conformance C1, C2, C3 (Software Qualification Test Specification 11).

    python3 -m eval.conformance [--planner LIB] [--out DIR] [--record]

Only what is observable through interfaces/c/pp_planner.h is checked: no scenario, no
simulator. Every group of checks runs in its own child process, so a planner that crashes
or hangs is reported as a failure instead of stopping the evaluator. C1 or C2 failed: the
planner is blocked and no other suite runs. C3 failed: the other suites still run, without
the Integrable flag. Exit status 1 when blocked.
"""

import argparse
import json
import math
import platform
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import interfaces as I
from adapters.sil import pp_ctypes
from eval import contract_io as io
from eval import planner_choice, provenance

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "build" / "conformance"
CHILD_TIMEOUT_S = 120
VP0 = I.VehicleConfig(2.9, 1.45, 1.9, 15.0, 0.61, 6.0, 0.05)  # Software Qualification Test Specification 4.4

# id: (level, what is checked, source)
CHECKS = {
    "C1.symbols": ("C1", "Có đủ pp_state_size, pp_init, pp_step, pp_version", "Interface Control Document 4"),
    "C1.layout": ("C1", "Build từ pp_types.h cùng phiên bản schema; layout struct khớp header sinh ra",
                  "Interface Control Document 4"),
    "C1.state_size": ("C1", "pp_state_size trả cùng một số > 0", "Interface Control Document 4"),
    "C1.alignment": ("C1", "Chạy được với vùng nhớ trạng thái căn theo PP_STATE_ALIGNMENT",
                     "interfaces/c/pp_planner.h"),
    "C2.init_ok": ("C2", "pp_init trả OK với VehicleConfig hợp lệ (VP-0)", "Interface Control Document 4"),
    "C2.init_missing": ("C2", "VehicleConfig thiếu: pp_init không trả OK, không chu kỳ nào gửi Trajectory",
                        "PP-SWR-146"),
    "C2.init_out_of_limits": ("C2", "VehicleConfig ngoài giới hạn: pp_init không trả OK, không chu kỳ nào "
                              "gửi Trajectory", "Interface Control Document 5.8 (bề rộng ≤ 2,5 m)"),
    "C2.outputs_every_cycle": ("C2", "Trajectory, PathStatus, LateralLimits gửi mỗi chu kỳ",
                               "PP-SWR-010, 150"),
    "C2.filled": ("C2", "pp_step điền mọi trường của output mỗi chu kỳ", "interfaces/c/pp_planner.h"),
    "C2.counter": ("C2", "header.counter tăng 1 mỗi message, quay vòng 0–255", "PP-SWR-014"),
    "C2.stamp": ("C2", "header.stamp_us của output là t0 của chu kỳ", "Interface Control Document 4, 6"),
    "C2.enum": ("C2", "Enum trong tập giá trị, bool là 0 hoặc 1", "Interface Control Document 4"),
    "C2.trajectory_format": ("C2", "31 điểm, bước 0,1 s, phủ 0–3 s, frame_id BASE_LINK, rear_wheel_angle 0",
                             "PP-SWR-011; Interface Control Document 6.1"),
    "C2.finite": ("C2", "Không có NaN hoặc vô cực trong output đã gửi", "Software Qualification Test Specification 11"),
    "C2.robust": ("C2", "Input chưa nhận, valid = false, giá trị ở hai đầu dải không làm planner dừng",
                  "Interface Control Document 4, 5"),
    "C2.version": ("C2", "pp_version trả cùng một chuỗi có phiên bản, commit, mã bộ calibration",
                   "Interface Control Document 4"),
    "C3.deterministic": ("C3", "Cùng chuỗi input cho cùng output từng bit", "PP-ADR-013"),
    "C3.interleaved": ("C3", "Hai instance chạy xen kẽ cho cùng output như khi chạy riêng", "PP-ADR-013"),
    "C3.memory": ("C3", "Không ghi ra ngoài vùng nhớ trạng thái (byte canh hai đầu)",
                  "Interface Control Document 4"),
    "C3.symbols": ("C3", "Bảng symbol không có cấp phát động, đọc file, đọc đồng hồ hệ thống",
                   "Interface Control Document 4; PP-ADR-013"),
}

# VehicleConfig values without a limit in the Software Requirements Specification: run and
# reported as information only, never graded (no requirement to judge them against).
_INFO_CONFIGS = {
    "wheelbase = 0": replace(VP0, wheelbase=0.0),
    "rear_axle_to_cg < 0": replace(VP0, rear_axle_to_cg=-0.1),
    "rear_axle_to_cg > wheelbase": replace(VP0, rear_axle_to_cg=3.0),
    "steering_ratio = 0": replace(VP0, steering_ratio=0.0),
    "max_wheel_angle = 0": replace(VP0, max_wheel_angle=0.0),
    "max_steering_wheel_rate = 0": replace(VP0, max_steering_wheel_rate=0.0),
    "actuator_delay < 0": replace(VP0, actuator_delay=-0.01),
    **{f"{name} = NaN": replace(VP0, **{name: float("nan")})
       for name in ("wheelbase", "rear_axle_to_cg", "vehicle_width", "steering_ratio",
                    "max_wheel_angle", "max_steering_wheel_rate", "actuator_delay")},
}
_GRADED_CONFIGS = {"vehicle_width = 2,51 m": replace(VP0, vehicle_width=2.51)}

FORBIDDEN_SYMBOLS = {
    "cấp phát động": {"malloc", "calloc", "realloc", "reallocf", "free", "aligned_alloc",
                      "posix_memalign", "valloc", "memalign", "mmap", "sbrk", "brk"},
    "đọc file": {"fopen", "fdopen", "freopen", "fread", "fgets", "fgetc", "getc", "fscanf",
                 "open", "openat", "read", "pread", "readv", "opendir"},
    "đọc đồng hồ hệ thống": {"time", "clock", "clock_gettime", "clock_gettime_nsec_np",
                             "gettimeofday", "mach_absolute_time", "mach_approximate_time",
                             "mach_continuous_time", "timespec_get", "ftime", "clock_getres"},
}

_OUT = pp_ctypes.PlannerOutputsC
_MESSAGES = ("trajectory", "path_status", "lateral_limits")
_ALL = io.leaves(_OUT)
_BY_MESSAGE = {m: io.sub_leaves(_OUT, m + ".") for m in _MESSAGES}
_FLAGS = {m: next(l for l in _ALL if l.path == f"{m}_sent") for m in _MESSAGES}


def _byte(raw: bytes, leaf: io.Leaf) -> int:
    return raw[leaf.offset]


# ---- checks on one output sequence -----------------------------------------------------

class OutputChecker:
    """Contract checks on every cycle of one sequence; failures keyed by check id."""

    def __init__(self, name: str, expect_trajectory: bool = True) -> None:
        self.name = name
        self.expect_trajectory = expect_trajectory
        self.failures: dict[str, list[str]] = {}
        self._counters: dict[str, int] = {}
        self._sentinel_hits = [0] * len(_ALL)
        self._sentinels_seen: set[int] = set()
        self.trajectories_sent = 0
        self.cycles = 0

    def fail(self, check: str, message: str) -> None:
        items = self.failures.setdefault(check, [])
        if len(items) < 5:
            items.append(f"{self.name}: {message}")

    def cycle(self, k: int, t0: int, result: io.StepResult) -> None:
        raw = result.raw
        self._sentinels_seen.add(result.sentinel)
        pattern = result.sentinel
        for i, leaf in enumerate(_ALL):
            if all(b == pattern for b in raw[leaf.offset:leaf.offset + leaf.size]):
                self._sentinel_hits[i] += 1
        sent = {}
        for m, flag in _FLAGS.items():
            value = _byte(raw, flag)
            if value not in (0, 1):
                self.fail("C2.enum", f"chu kỳ {k}: {flag.path} = {value}")
            sent[m] = value == 1
        self.trajectories_sent += sent["trajectory"]
        wanted = [m for m in _MESSAGES if m != "trajectory" or self.expect_trajectory]
        missing = [m for m in wanted if not sent[m]]
        if missing:
            self.fail("C2.outputs_every_cycle", f"chu kỳ {k}: không gửi {', '.join(missing)}")
        for m in _MESSAGES:
            if sent[m]:
                self._message(k, t0, m, raw)

    def _message(self, k: int, t0: int, m: str, raw: bytes) -> None:
        values = {leaf.path: leaf for leaf in _BY_MESSAGE[m]}
        counter = values[f"{m}.header.counter"].read(raw)
        if m in self._counters and counter != (self._counters[m] + 1) % I.COUNTER_MODULO:
            self.fail("C2.counter", f"chu kỳ {k}: {m} counter {self._counters[m]} → {counter}")
        self._counters[m] = counter
        stamp = values[f"{m}.header.stamp_us"].read(raw)
        if stamp != t0:
            self.fail("C2.stamp", f"chu kỳ {k}: {m} stamp_us {stamp} ≠ t0 {t0}")
        for leaf in _BY_MESSAGE[m]:
            if leaf.is_bool and _byte(raw, leaf) not in (0, 1):
                self.fail("C2.enum", f"chu kỳ {k}: {leaf.path} = {_byte(raw, leaf)}")
            elif leaf.enum is not None and leaf.read(raw) not in {int(v) for v in leaf.enum}:
                self.fail("C2.enum", f"chu kỳ {k}: {leaf.path} = {leaf.read(raw)}")
            elif leaf.is_float and not math.isfinite(leaf.read(raw)):
                self.fail("C2.finite", f"chu kỳ {k}: {leaf.path} = {leaf.read(raw)}")
        if m == "trajectory":
            frame = values["trajectory.header.frame_id"].read(raw)
            if frame != int(I.FrameId.BASE_LINK):
                self.fail("C2.trajectory_format", f"chu kỳ {k}: frame_id {frame}")
            for i in range(I.TRAJECTORY_POINTS):
                t = values[f"trajectory.points[{i}].time_from_start"].read(raw)
                if not abs(t - i * I.TRAJECTORY_STEP_S) <= 1e-5:
                    self.fail("C2.trajectory_format", f"chu kỳ {k}: điểm {i} time_from_start {t:.6g} s")
                    break
            for i in range(I.TRAJECTORY_POINTS):
                rear = values[f"trajectory.points[{i}].rear_wheel_angle_rad"].read(raw)
                if rear != 0.0:
                    self.fail("C2.trajectory_format", f"chu kỳ {k}: điểm {i} rear_wheel_angle {rear:.6g}")
                    break

    def finish(self) -> None:
        if len(self._sentinels_seen) < 2:
            return
        never = [leaf.path for leaf, hits in zip(_ALL, self._sentinel_hits)
                 if hits and hits == self.cycles]
        if never:
            self.fail("C2.filled", f"{len(never)} trường không được ghi, ví dụ {', '.join(never[:4])}")


def run_sequence(lib, seq: io.Sequence, config=VP0, expect_trajectory=True, instance=None):
    """Runs one sequence on a fresh instance (or the given one); returns checker, outputs, guards."""
    inst = instance or io.Instance(lib, config)
    checker = OutputChecker(seq.name, expect_trajectory)
    outputs = []
    for k in range(seq.cycles):
        x = seq.frame(k)
        res = inst.step(x, seq.motion, io.SENTINELS[k % 2])
        checker.cycles += 1
        checker.cycle(k, x.t0_us, res)
        outputs.append(res)
    checker.finish()
    return checker, outputs, inst


# ---- child jobs ------------------------------------------------------------------------

def _result(check: str, status: str, detail: str = "") -> dict:
    return {"id": check, "status": status, "detail": detail}


def _from_checkers(ids, checkers) -> list[dict]:
    out = []
    for check in ids:
        failures = [f for c in checkers for f in c.failures.get(check, [])]
        out.append(_result(check, "fail" if failures else "pass", "; ".join(failures[:5])))
    return out


class _Guards:
    def __init__(self) -> None:
        self.bad: list[str] = []

    def check(self, name: str, inst: io.Instance) -> None:
        if not inst.guards_intact():
            self.bad.append(name)

    def result(self) -> dict:
        return _result("C3.memory", "fail" if self.bad else "pass",
                       ("byte canh bị ghi đè: " + ", ".join(self.bad[:5])) if self.bad else "")


def job_api(lib_path: str) -> list[dict]:
    lib = io.open_library(lib_path)
    results = [_result("C1.symbols", "pass" if hasattr(lib, "pp_version") else "fail",
                       "" if hasattr(lib, "pp_version") else "thiếu pp_version")]
    sizes = [int(lib.pp_state_size()) for _ in range(3)]
    results.append(_result("C1.state_size", "pass" if sizes[0] > 0 and len(set(sizes)) == 1 else "fail",
                           f"{sizes[0]} byte" if len(set(sizes)) == 1 else f"đổi giữa các lần gọi: {sizes}"))
    guards = _Guards()
    _, _, inst = run_sequence(lib, io.Sequence("căn lề", 40))
    guards.check("căn lề", inst)
    results.append(_result("C1.alignment", "pass", f"trạng thái tại địa chỉ ≡ {io.STATE_ALIGNMENT} "
                           f"(mod {2 * io.STATE_ALIGNMENT}), 40 chu kỳ"))
    return results + [guards.result()]


def job_init(lib_path: str) -> list[dict]:
    lib = io.open_library(lib_path)
    guards = _Guards()
    seq = io.Sequence("khởi tạo", 80)
    ok = io.Instance(lib, VP0).init_result == int(I.InitResult.OK)
    results = [_result("C2.init_ok", "pass" if ok else "fail", "" if ok else "pp_init không trả OK với VP-0")]

    def rejected(config) -> str | None:
        inst = io.Instance(lib, config)
        checker, _, _ = run_sequence(lib, seq, expect_trajectory=False, instance=inst)
        guards.check("khởi tạo", inst)
        problems = []
        if inst.init_result == int(I.InitResult.OK):
            problems.append("pp_init trả OK")
        if checker.trajectories_sent:
            problems.append(f"gửi Trajectory {checker.trajectories_sent}/{seq.cycles} chu kỳ")
        return ", ".join(problems) or None

    bad = rejected(None)
    results.append(_result("C2.init_missing", "fail" if bad else "pass", bad or ""))
    bad = {name: rejected(cfg) for name, cfg in _GRADED_CONFIGS.items()}
    failed = {k: v for k, v in bad.items() if v}
    results.append(_result("C2.init_out_of_limits", "fail" if failed else "pass",
                           "; ".join(f"{k}: {v}" for k, v in failed.items())))
    info = {name: rejected(cfg) for name, cfg in _INFO_CONFIGS.items()}
    accepted = [k for k, v in info.items() if v]
    results.append({"id": "info.vehicle_config", "status": "info",
                    "detail": ("Chấp nhận (chưa có giới hạn trong Software Requirements Specification): "
                               + ", ".join(accepted)) if accepted else "Từ chối mọi giá trị đã thử"})
    return results + [guards.result()]


def job_nominal(lib_path: str) -> list[dict]:
    lib = io.open_library(lib_path)
    guards = _Guards()
    checkers = []
    for seq in (io.Sequence("danh định", 300), io.Sequence("biến thiên", 300, seed=1)):
        checker, _, inst = run_sequence(lib, seq)
        guards.check(seq.name, inst)
        checkers.append(checker)
    ids = ("C2.outputs_every_cycle", "C2.filled", "C2.counter", "C2.stamp", "C2.enum",
           "C2.trajectory_format", "C2.finite")
    versions = {lib.pp_version() for _ in range(3)} if hasattr(lib, "pp_version") else set()
    words = next(iter(versions)).decode("ascii", "replace").split() if len(versions) == 1 else []
    ok = (len(words) >= 6 and words[2] == "commit" and words[4] == "calibration"
          and all(words[i] for i in (0, 1, 3, 5)))
    version = _result("C2.version", "pass" if ok else "fail",
                      " ".join(words) if ok else f"chuỗi không đúng dạng: {sorted(v.decode('ascii', 'replace') for v in versions)}")
    return _from_checkers(ids, checkers) + [version, guards.result()]


def robust_sequences(name: str) -> list[io.Sequence]:
    if name == "all":
        return [io.Sequence("mọi input chưa nhận", 40, absent=frozenset(io.INPUTS))]
    return [io.Sequence(f"{name} chưa nhận", 40, absent=frozenset({name})),
            io.Sequence(f"{name} valid = false", 40, invalid=frozenset({name})),
            io.Sequence(f"{name} đầu thấp của dải", 40, extreme=(name, "low")),
            io.Sequence(f"{name} đầu cao của dải", 40, extreme=(name, "high"))]


def job_robust(lib_path: str, name: str) -> list[dict]:
    lib = io.open_library(lib_path)
    guards = _Guards()
    failures = []
    for seq in robust_sequences(name):
        checker, _, inst = run_sequence(lib, seq)
        guards.check(seq.name, inst)
        failures += [f"[{check}] {msg}" for check, msgs in checker.failures.items() for msg in msgs[:1]]
    return [_result("C2.robust", "fail" if failures else "pass", "; ".join(failures[:6])), guards.result()]


def _fields_equal(a: io.StepResult, b: io.StepResult) -> str | None:
    if a.requests != b.requests:
        return f"EgoMotionQuery khác: {a.requests[:2]} / {b.requests[:2]}"
    for leaf in _ALL:
        if a.raw[leaf.offset:leaf.offset + leaf.size] != b.raw[leaf.offset:leaf.offset + leaf.size]:
            return f"{leaf.path}: {leaf.read(a.raw)} / {leaf.read(b.raw)}"
    return None


def job_determinism(lib_path: str) -> list[dict]:
    lib = io.open_library(lib_path)
    guards = _Guards()
    seq_a, seq_b = io.Sequence("A", 400, seed=7), io.Sequence("B", 400, seed=8)
    _, alone_a, inst = run_sequence(lib, seq_a)
    guards.check("A", inst)
    _, again_a, inst = run_sequence(lib, seq_a)
    guards.check("A lần 2", inst)
    _, alone_b, inst = run_sequence(lib, seq_b)
    guards.check("B", inst)
    diff = next(((k, d) for k, (x, y) in enumerate(zip(alone_a, again_a)) if (d := _fields_equal(x, y))), None)
    det = _result("C3.deterministic", "fail" if diff else "pass",
                  f"chu kỳ {diff[0]}: {diff[1]}" if diff else f"{seq_a.cycles} chu kỳ, hai instance")
    a, b = io.Instance(lib, VP0), io.Instance(lib, VP0)
    mixed = None
    for k in range(seq_a.cycles):
        ra = a.step(seq_a.frame(k), seq_a.motion, io.SENTINELS[k % 2])
        rb = b.step(seq_b.frame(k), seq_b.motion, io.SENTINELS[k % 2])
        for label, got, want in (("A", ra, alone_a[k]), ("B", rb, alone_b[k])):
            if mixed is None and (d := _fields_equal(got, want)):
                mixed = f"chu kỳ {k}, instance {label}: {d}"
    guards.check("xen kẽ A", a)
    guards.check("xen kẽ B", b)
    inter = _result("C3.interleaved", "fail" if mixed else "pass", mixed or f"{seq_a.cycles} chu kỳ")
    return [det, inter, guards.result()]


JOBS = {"api": (job_api, ("C1.symbols", "C1.state_size", "C1.alignment")),
        "init": (job_init, ("C2.init_ok", "C2.init_missing", "C2.init_out_of_limits")),
        "nominal": (job_nominal, ("C2.outputs_every_cycle", "C2.filled", "C2.counter", "C2.stamp",
                                  "C2.enum", "C2.trajectory_format", "C2.finite", "C2.version")),
        "determinism": (job_determinism, ("C3.deterministic", "C3.interleaved"))}
JOBS.update({f"robust:{name}": (lambda path, n=name: job_robust(path, n), ("C2.robust",))
             for name in ("all",) + io.INPUTS})


# ---- parent ----------------------------------------------------------------------------

def run_child(job: str, lib: Path) -> list[dict]:
    """One job in a child process; a crash or hang fails every check of the job."""
    produced = JOBS[job][1]
    try:
        proc = subprocess.run([sys.executable, "-m", "eval.conformance", "--child", job, str(lib)],
                              cwd=ROOT, capture_output=True, text=True, timeout=CHILD_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return [_result(c, "fail", f"{job}: planner không trả về sau {CHILD_TIMEOUT_S} s") for c in produced]
    if proc.returncode != 0:
        if proc.returncode < 0:
            why = f"{job}: planner làm tiến trình dừng (signal {-proc.returncode})"
        else:
            why = f"{job}: lỗi {proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else proc.returncode}"
        return [_result(c, "fail", why) for c in produced]
    return json.loads(proc.stdout.strip().splitlines()[-1])


def symbols(lib: Path) -> dict:
    if shutil.which("nm") is None:
        return _result("C3.symbols", "not_checked", "không có nm")
    cmd = ["nm", "-u", str(lib)] if platform.system() == "Darwin" else ["nm", "-D", "--undefined-only", str(lib)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return _result("C3.symbols", "not_checked", proc.stderr.strip()[:200])
    names = set()
    for line in proc.stdout.split():
        name = line.split("@")[0].split("$")[0]
        names.add(name[1:] if platform.system() == "Darwin" and name.startswith("_") else name)
    found = {kind: sorted(names & bad) for kind, bad in FORBIDDEN_SYMBOLS.items() if names & bad}
    return _result("C3.symbols", "fail" if found else "pass",
                   "; ".join(f"{k}: {', '.join(v)}" for k, v in found.items()))


_RANK = {"fail": 3, "not_checked": 2, "pass": 1, "info": 0}


def merge(results: list[dict]) -> list[dict]:
    """One line per check: the worst status wins; details of that status are joined."""
    by_id: dict[str, dict] = {}
    for r in sorted(results, key=lambda r: -_RANK[r["status"]]):
        old = by_id.setdefault(r["id"], {**r, "detail": ""})
        if r["status"] == old["status"] and r["detail"] and r["detail"] not in old["detail"]:
            old["detail"] = "; ".join(x for x in (old["detail"], r["detail"]) if x)[:600]
    order = list(CHECKS) + sorted(k for k in by_id if k not in CHECKS)
    return [{**by_id[k], **({"level": CHECKS[k][0], "title": CHECKS[k][1], "source": CHECKS[k][2]}
                             if k in CHECKS else {"level": "info"})} for k in order if k in by_id]


def run(lib: Path) -> dict:
    results = [_result("C1.layout", "not_checked",
                       "Không quan sát được từ file thư viện: pp_types.h không có mã phiên bản schema")]
    api = run_child("api", lib)  # loads the library in a child first
    results += api
    if any(r["id"] == "C1.symbols" and r["status"] == "fail" and "pp_version" not in r["detail"] for r in api):
        others = [c for c in CHECKS if c not in ("C1.symbols", "C1.layout", "C3.symbols")
                  and c not in JOBS["api"][1]]
        results += [_result(c, "not_checked", "không gọi được thư viện") for c in others]
    else:
        for job in JOBS:
            if job != "api":
                results += run_child(job, lib)
    results.append(symbols(lib))
    checks = merge(results)
    level = {lv: ("fail" if any(c["status"] == "fail" for c in checks if c["level"] == lv) else "pass")
             for lv in ("C1", "C2", "C3")}
    blocked = level["C1"] == "fail" or level["C2"] == "fail"
    return {"checks": checks, "levels": level, "blocked": blocked,
            "integrable": not blocked and level["C3"] == "pass"
                          and all(c["status"] == "pass" for c in checks if c["level"] == "C3"),
            "not_checked": [c["id"] for c in checks if c["status"] == "not_checked"]}


_STATUS = {"pass": "đạt", "fail": "TRƯỢT", "not_checked": "không kiểm được", "info": "thông tin"}


def text(result: dict, version: str | None) -> str:
    verdict = ("Không đạt: trượt " + ", ".join(lv for lv in ("C1", "C2") if result["levels"][lv] == "fail")
               + "; không chạy bộ khác") if result["blocked"] else (
        "Đạt C1, C2" + ("; Tích hợp được" if result["integrable"] else "; không có cờ Tích hợp được"))
    lines = [f"B0 Conformance: {verdict}", f"pp_version: {version or '—'}", ""]
    for c in result["checks"]:
        lines.append(f"{c['id']:<24} {_STATUS[c['status']]:<16} {c.get('title', '')}")
        if c["detail"] and c["status"] != "pass":
            lines.append(f"{'':<24} {c['detail']}")
    if result["not_checked"]:
        lines += ["", "Không kiểm được (không tính là đạt): " + ", ".join(result["not_checked"])]
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) == 4 and sys.argv[1] == "--child":
        print(json.dumps(JOBS[sys.argv[2]][0](sys.argv[3]), ensure_ascii=False))
        return
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    planner_choice.add_argument(parser)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--record", action="store_true",
                        help="Official run: clean working tree; copy to research/runs")
    args = parser.parse_args()
    lib = (args.planner or planner_choice.library_path())
    if not lib.is_file():
        raise SystemExit(f"planner library not found: {lib}")
    lib = lib.resolve()
    manifest = provenance.make("conformance", lib.stem)
    try:
        manifest["libraries"] = [provenance.library_info(lib, external=args.planner is not None)]
    except Exception as error:  # a library that cannot be loaded is still judged (C1)
        manifest["libraries"] = [{"path": str(lib), "sha256": provenance.sha256(lib), "pp_version": None,
                                  "build": {}, "external": args.planner is not None, "error": str(error)}]
    if args.record:
        provenance.preflight(manifest)
    result = run(lib)
    version = manifest["libraries"][0]["pp_version"]
    report = text(result, version)
    print(report)
    out = args.out or OUT_DIR / f"{lib.stem}-{manifest['libraries'][0]['sha256'][:8]}"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "conformance.json"
    path.write_text(json.dumps({"pp_version": version, **result}, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    (out / "conformance.txt").write_text(report + "\n", encoding="utf-8")
    provenance.write({**manifest, "summary": {k: result[k] for k in ("levels", "blocked", "integrable")}}, out)
    print(f"\nJSON: {path}")
    if args.record:
        dest = provenance.record(manifest, {"conformance.json": path, "conformance.txt": out / "conformance.txt"},
                                 report.splitlines()[0])
        print(f"Recorded: {dest}")
    if result["blocked"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
