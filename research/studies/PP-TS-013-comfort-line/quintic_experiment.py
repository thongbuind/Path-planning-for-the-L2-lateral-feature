"""Compare the C quintic planner with a waypoint variant in paired SIL runs."""

import ctypes
from dataclasses import replace
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from adapters.sil.sil_planner import PlannerLibrary  # noqa: E402
from eval import loader, metrics, provenance  # noqa: E402
from sim.harness import Harness  # noqa: E402
from sim.runtime.seeds import random_phase_us  # noqa: E402
from sim.sensors import object_sensor  # noqa: E402

CASES = (
    ("S1", "f", ("F01", "a"), "off", 1, False),
    ("S1", "f", None, "off", 1, True),
    ("S1", "f", ("F01", "a"), "off", 1, True),
    ("S1", "f", ("F01", "a"), "off", 2, True),
    ("S1", "f", ("F01", "c"), "off", 1, True),
    ("S1", "a", ("F01", "a"), "off", 1, True),
    ("S14", "e", None, "on", 1, True),
    ("S3", "a", None, "off", 1, False),
)
CHECKS = {
    "PP-SWR-001", "PP-SWR-003", "PP-SWR-005", "PP-SWR-006", "PP-SWR-007",
    "PP-SWR-010", "PP-SWR-018", "PP-SWR-051", "PP-SWR-055", "PP-SWR-056", "PP-SWR-058",
    "PP-SWR-100", "PP-SWR-101", "PP-SWR-102", "PP-SWR-116", "PP-SWR-117",
}


class ObjectListHarness(Harness):
    """Publish the standard ObjectList sensor even on roads with no traffic actors."""

    def _build_scheduler(self):
        scheduler = super()._build_scheduler()
        if not self.scenario.traffic and self._adas_modes is None:
            period = object_sensor.PERIOD_US
            phase = random_phase_us(self.rngs["phases"], period, scheduler.step_us)
            scheduler.add_sensor("object_sensor", period, self._objects, phase)
        return scheduler


def add_research_hook(planner):
    source = planner / "src" / "pp_planner.c"
    shutil.copy2(HERE / "quintic_comfort.inc", source.with_name("quintic_comfort.inc"))
    code = source.read_text(encoding="utf-8")
    insertions = (
        ("                         double d_target,\n"
         "                         pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],",
         "                         double d_target, pp_lateral_path_t *base,\n"
         "                         pp_trajectory_point_t points[PP_TRAJECTORY_POINTS],"),
        ("            pp_output_points(ref, &lateral, speed, wheelbase, points, samples);",
         "            *base = lateral;\n"
         "            pp_output_points(ref, &lateral, speed, wheelbase, points, samples);"),
        ("static void plan_path(", '#include "quintic_comfort.inc"\n\nstatic void plan_path('),
        ("            (void)from_old;\n"
         "            out->path_valid = generate_hwa(s, &out->ref, &start, &speed, offset, out->points,",
         "            (void)from_old;\n"
         "            pp_lateral_path_t base;\n"
         "            out->path_valid = generate_hwa(s, &out->ref, &start, &speed, offset, &base, out->points,"),
        ("                /* T10 steps 3, 4 on the larger of camera and fused curvature (safe side). */",
         "                research_try_quintic(s, in, &lane, &camera_ref, &speed, &old, offset, &base, out);\n"
         "                /* T10 steps 3, 4 on the larger of camera and fused curvature (safe side). */"),
    )
    for before, after in insertions:
        if code.count(before) != 1:
            raise RuntimeError(f"Expected a unique quintic source anchor: {before}")
        code = code.replace(before, after, 1)
    source.write_text(code, encoding="utf-8")


def build(source, output):
    commands = (
        ["cmake", "-S", str(source), "-B", str(output), "-DCMAKE_BUILD_TYPE=Release",
         "-DPP_T7=quintic", "-DPP_BUILD_TESTS=OFF", "-DPP_BUILD_LAYOUT_PROBE=OFF",
         f"-DPython3_EXECUTABLE={sys.executable}"],
        ["cmake", "--build", str(output), "--parallel", "1"],
    )
    for command in commands:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout)
    suffix = ".dylib" if sys.platform == "darwin" else ".so"
    return PlannerLibrary(output / f"libpp_planner{suffix}")


def build_pair(work):
    snapshot = work / "source"
    planner = snapshot / "planner"
    shutil.copytree(ROOT / "planner", planner)
    shutil.copytree(ROOT / "interfaces" / "c", snapshot / "interfaces" / "c")
    baseline = build(planner, work / "baseline")
    add_research_hook(planner)
    return baseline, build(planner, work / "waypoint")


def run_case(scenario, seed, library, candidate, publish_object_list):
    counts = None
    if candidate:
        lib = library.load()
        lib.pp_research_reset.argtypes = []
        lib.pp_research_reset.restype = None
        lib.pp_research_count.argtypes = [ctypes.c_uint]
        lib.pp_research_count.restype = ctypes.c_uint64
        lib.pp_research_reset()
    harness = ObjectListHarness if publish_object_list else Harness
    log = harness(scenario, library, seed).run()
    result = metrics.evaluate(log)
    if candidate:
        counts = dict(zip(("hwa", "eligible", "applied"), (lib.pp_research_count(i) for i in range(3))))
        assert counts["applied"] <= counts["eligible"] <= counts["hwa"]
    if not result.scored or log.init_result != 0 or result.info["first_hwa_s"] is None:
        raise RuntimeError(f"{scenario.name} did not produce a scored HWA run")
    criteria = {
        c.id: {"value": c.value if math.isfinite(c.value) else None,
               "limit": c.limit, "passed": c.passed, "first_fail_s": c.first_fail_s}
        for c in result.criteria if c.id in CHECKS and c.applicable
    }
    return {
        "criteria": criteria,
        "failed": sorted(k for k, v in criteria.items() if not v["passed"]),
        "vehicle_peak_ay_mps2": result.info["ay_vehicle_r79_max"],
        "vehicle_peak_jerk_mps3": result.info["jerk_vehicle_r79_max"],
        "vehicle_max_offset_m": result.info["vehicle_offset_max_m"],
        "speed_min_mps": result.info["speed_min_mps"],
        "object_list_usable_cycles": sum(bool(c.inputs_ok and c.inputs_ok.get("object_list"))
                                         for c in log.cycles),
        "p99_step_ms": next(t.value for t in result.targets if t.id == "PP-SWR-016" and "p99" in t.metric),
        "selection_cycles": counts,
    }


def main():
    with TemporaryDirectory(prefix=".quintic-", dir=HERE) as work:
        baseline, waypoint = build_pair(Path(work))
        libraries = {
            label: {"pp_version": lib.version(), "sha256": provenance.sha256(lib.path)}
            for label, lib in (("quintic", baseline), ("waypoint", waypoint))
        }
        print("Built baseline and waypoint libraries", flush=True)
        runs = []
        for name, variant, fault, acc, seed, publish_object_list in CASES:
            scenario = replace(loader.load(name, variant), acc=acc, camera_latency_ms=100.0, camera_view_m=80.0)
            if fault is not None:
                scenario = loader.with_fault(scenario, *fault)
            pair = {"case": scenario.name, "profile": scenario.profile, "seed": seed, "acc": acc,
                    "publish_object_list_on_empty_road": publish_object_list}
            pair["quintic"] = run_case(scenario, seed, baseline, False, publish_object_list)
            pair["waypoint"] = run_case(scenario, seed, waypoint, True, publish_object_list)
            runs.append(pair)
            base, changed = pair["quintic"], pair["waypoint"]
            print(f"{pair['case']:12s} seed {seed}  object sensor {publish_object_list!s:5s}  "
                  f"a_y {base['vehicle_peak_ay_mps2']:.3f} → {changed['vehicle_peak_ay_mps2']:.3f}  "
                  f"jerk {base['vehicle_peak_jerk_mps3']:.3f} → {changed['vehicle_peak_jerk_mps3']:.3f}  "
                  f"cycles {changed['selection_cycles']}  "
                  f"fail {base['failed']} → {changed['failed']}", flush=True)
    output = {
        "study": "PP-TS-013",
        "kind": "research-only paired SIL",
        "git": provenance.git_state(),
        "camera_latency_ms": 100.0,
        "camera_view_m": 80.0,
        "libraries": libraries,
        "hook_sha256": provenance.sha256(HERE / "quintic_comfort.inc"),
        "runs": runs,
    }
    (HERE / "quintic_results.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n",
                                               encoding="utf-8")


if __name__ == "__main__":
    main()
