"""Isolated T7 proof of concept for PP-TS-024 and PP-TS-025.

Run from the repository root with one CPU worker. The original C sources and
the two formal study plans remain usable. All build products go under --out.
"""

import argparse
import ctypes as c
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.sil.sil_planner import PlannerLibraries
from eval import metrics, provenance, sweep
from sim.harness import Harness

STUDIES = ROOT / "research" / "studies"
DRIVER_HOOK = STUDIES / "PP-TS-024-driver-model-path" / "pilot_driver.inc"
QP_HOOK = STUDIES / "PP-TS-025-nn-ltv-mpc-path" / "pilot_qp.inc"
N = 30
F = 21
H = 32
VEC = c.c_double * N
CASES = (
    (["S1", "f"], 11),
    (["S1", "f"], 12),
    (["S1", "d"], 1),
    (["S1", "f", "F01", "a"], 11),
    (["S1b", "a", {"acc": "ignore_limits"}], 1),
    (["S22", "a"], 1),
    (["S1", "f", {"loop": "open"}], 11),
    (["S1b", "a", {"loop": "open", "acc": "ignore_limits"}], 1),
)


class QpProblem(c.Structure):
    _fields_ = [
        ("start", c.c_double * 4), ("d_target", c.c_double), ("v", VEC),
        ("kappa", VEC), ("d_max", VEC), ("d_min", VEC), ("d_old", VEC),
        ("has_old", c.c_bool * N), ("ay_limit", c.c_double),
        ("jerk_limit", c.c_double), ("dkappa", VEC),
    ]


def replace_once(code, old, new):
    if code.count(old) != 1:
        raise RuntimeError(f"Expected one source anchor: {old!r}")
    return code.replace(old, new, 1)


def add_driver_hook(planner):
    target = planner / "src" / "pp_lcc.c"
    code = target.read_text()
    code = replace_once(code, "double d_target,\n                         pp_trajectory_point_t",
                        "double d_target, pp_lateral_path_t *base,\n                         pp_trajectory_point_t")
    code = replace_once(code, "        done = !ok;\n        if (ok) {",
                        "        done = !ok;\n        if (ok) {\n            *base = lateral;")
    code = replace_once(code, "static bool build_path(", '#include "pilot_driver.inc"\n\nstatic bool build_path(')
    start = code.index("    (void)from_old;\n")
    end = code.index("\n#endif", start)
    branch = code[start:end]
    branch = replace_once(branch, "    const bool ok = generate_lcc(s, ref, &start, &speed, d_target,",
                          "    pp_lateral_path_t base;\n"
                          "    const bool ok = generate_lcc(s, ref, &start, &speed, d_target, &base,")
    code = code[:start] + branch + (
        "\n    if (ok) {\n"
        "        pilot_driver(s, in, ref, &speed, goal, follow, d_target, &base, out);\n"
        "    }"
    ) + code[end:]
    target.write_text(code)
    shutil.copyfile(DRIVER_HOOK, target.with_name(DRIVER_HOOK.name))


def add_qp_hook(planner):
    target = planner / "src" / "generators" / "qp.c"
    code = target.read_text()
    code = replace_once(code, "bool pp_generate_qp(", '#include "pilot_qp.inc"\n\nbool pp_generate_qp(')
    code = replace_once(code, "        bounds(ws, cal, pb, &data);",
                        "        bounds(ws, cal, pb, &data);\n#if PP_POTENTIAL_NN\n"
                        "        pilot_init_jerk(ws, pb, &data);\n#endif")
    code = replace_once(code, "        ws->warm = ok;",
                        "        if (ok) {\n            pilot_record_residual(ws);\n        }\n        ws->warm = ok;")
    target.write_text(code)
    shutil.copyfile(QP_HOOK, target.with_name(QP_HOOK.name))


def build(source, output, technique, *, iters=None, flags=""):
    output.mkdir(parents=True, exist_ok=True)
    data = yaml.safe_load((source / "calibration" / "calibration.yaml").read_text())
    if iters is not None:
        data["parameters"]["qp_iters"]["value"] = iters
    calibration = output / "calibration.yaml"
    calibration.write_text(yaml.safe_dump(data, sort_keys=False))
    commands = (
        ["cmake", "-S", str(source), "-B", str(output), "-DCMAKE_BUILD_TYPE=Release",
         "-DPP_BUILD_TESTS=OFF", "-DPP_BUILD_LAYOUT_PROBE=OFF", f"-DPP_T7={technique}",
         f"-DPP_CALIBRATION_FILE={calibration}", f"-DPython3_EXECUTABLE={sys.executable}",
         f"-DCMAKE_C_FLAGS={flags}"],
        ["cmake", "--build", str(output), "--parallel", "1", "--target", "pp_lcc", "pp_lkaelk"],
    )
    with (output / "build.log").open("w") as log:
        for command in commands:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(f"Build failed. See {output / 'build.log'}")
    return PlannerLibraries.at(output)


def synthetic_problem(rng):
    t = np.arange(1, N + 1) * 0.1
    v = rng.uniform(13.5, 35.0) + rng.uniform(-1, 1) * t
    ay = rng.uniform(-1.8, 1.8) + rng.uniform(-1.6, 1.6) * np.sin(t * rng.uniform(0.5, 2.0) + rng.uniform(-3, 3))
    kappa = ay / v**2
    dkappa = np.gradient(kappa, np.cumsum(v) * 0.1)
    d = float(rng.uniform(-0.5, 0.5))
    dv = float(rng.uniform(-0.22, 0.22))
    da = float(rng.uniform(-0.5, 0.5))
    target = float(rng.uniform(-0.25, 0.25)) if rng.random() < 0.2 else 0.0
    half = float(rng.uniform(0.13, 0.70))
    old_count = int(rng.choice([0, 10, 20, 25, N, N, N]))
    old = target + (d - target) * np.exp(-t / rng.uniform(0.65, 2.5)) + (t * dv * np.exp(-t))
    return QpProblem((c.c_double * 4)(d, dv, da, 0), target, VEC(*v), VEC(*kappa),
                     VEC(*[half] * N), VEC(*[-half] * N), VEC(*old),
                     (c.c_bool * N)(*(i < old_count for i in range(N))), 2.5, 4.5, VEC(*dkappa))


def dataset(lib, seed, count):
    rng = np.random.default_rng(seed)
    features = lib.pp_potential_features
    features.argtypes = [c.POINTER(QpProblem), c.POINTER(c.c_double)]
    features.restype = None
    teacher = lib.pp_potential_teacher
    teacher.argtypes = [c.POINTER(QpProblem), *[c.POINTER(c.c_double)] * 3]
    teacher.restype = c.c_bool
    x, y = [], []
    for _ in range(count):
        problem = synthetic_problem(rng)
        feature, jerk = (c.c_double * F)(), VEC()
        residual, violation = c.c_double(), c.c_double()
        if teacher(c.byref(problem), jerk, c.byref(residual), c.byref(violation)):
            if residual.value < 0.035 and violation.value < 0.025:
                features(c.byref(problem), feature)
                x.append(list(feature))
                y.append(list(jerk))
    return np.array(x), np.array(y)


def train(library, destination):
    x, y = dataset(library.load()[0], 107, 900)
    validation_x, validation_y = dataset(library.load()[0], 211, 220)
    if len(x) < 500 or len(validation_x) < 100:
        raise RuntimeError(f"Too few usable teacher labels: {len(x)} / {len(validation_x)}")
    rng = np.random.default_rng(311)
    mean, inv = x.mean(axis=0), 1 / np.maximum(x.std(axis=0), 1e-5)
    scale = max(float(y.std()), 0.01)
    x, y = (x - mean) * inv, y / scale
    parameters = [rng.normal(0, 0.15, (F, H)), np.zeros(H),
                  rng.normal(0, 0.08, (H, N)), np.zeros(N)]
    moment = [np.zeros_like(p) for p in parameters]
    variance = [np.zeros_like(p) for p in parameters]
    step = 0
    for _ in range(60):
        for batch in np.array_split(rng.permutation(len(x)), 12):
            a, b, w, bias = parameters
            hidden = np.tanh(x[batch] @ a + b)
            dy = (hidden @ w + bias - y[batch]) / (len(batch) * N)
            dz = (dy @ w.T) * (1 - hidden**2)
            gradient = [x[batch].T @ dz, dz.sum(axis=0), hidden.T @ dy, dy.sum(axis=0)]
            step += 1
            for p, m, v, g in zip(parameters, moment, variance, gradient):
                m *= 0.9
                m += 0.1 * g
                v *= 0.999
                v += 0.001 * g**2
                p -= (0.003 / (1 - 0.9**step)) * m / (np.sqrt(v / (1 - 0.999**step)) + 1e-8)
    a, b, w, bias = parameters

    def array(name, values):
        def initializer(v):
            return "{" + ", ".join(format(float(x), ".12g") if np.ndim(x) == 0 else initializer(x) for x in v) + "}"
        dims = "".join(f"[{size}]" for size in values.shape)
        return f"static const double {name}{dims} = {initializer(values)};"

    entries = {"input_mean": mean, "input_inv_std": inv, "input_weights": a.T,
               "hidden_bias": b, "output_weights": w.T * scale, "output_bias": bias * scale}
    destination.write_text("\n".join(array(f"pilot_{key}", value) for key, value in entries.items()) + "\n")
    prediction = (np.tanh(((validation_x - mean) * inv) @ a + b) @ w + bias) * scale
    return {"train_labels": len(x), "validation_labels": len(validation_x), "iterations_teacher": 600,
            "validation_jerk_rmse": float(np.sqrt(np.mean((prediction - validation_y)**2))),
            "zero_jerk_rmse": float(np.sqrt(np.mean(validation_y**2))),
            "sha256": provenance.sha256(destination)}


def run_case(library, scenario, seed, scope, hook):
    lib = library.load()[0]
    if hook:
        lib.pp_potential_reset.argtypes = []
        lib.pp_potential_reset.restype = None
        lib.pp_potential_count.argtypes = [c.c_uint]
        lib.pp_potential_count.restype = c.c_uint64
        lib.pp_potential_reset()
    log = Harness(scenario, library, seed).run()
    result = metrics.evaluate(log)
    row = sweep._paired_evidence(log, result, scope)
    row["failed"] = sorted({item.id for item in result.criteria
                            if item.id in scope and item.applicable and not item.passed})
    if hook == "driver":
        row["generator"] = {name: lib.pp_potential_count(i)
                            for i, name in enumerate(("calls", "eligible", "applied"))}
    elif hook == "qp":
        lib.pp_potential_residual.argtypes = [c.c_uint]
        lib.pp_potential_residual.restype = c.c_double
        row["generator"] = {"calls": lib.pp_potential_count(0), "applied": lib.pp_potential_count(1),
                             "primal_residual_mean": lib.pp_potential_residual(0),
                             "primal_residual_max": lib.pp_potential_residual(1)}
    if not result.scored or log.init_result != 0:
        raise RuntimeError(f"Unscored SIL run: {scenario.name}, seed {seed}")
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = out / "source"
    planner = source / "planner"
    shutil.copytree(ROOT / "planner", planner)
    shutil.copytree(ROOT / "interfaces" / "c", source / "interfaces" / "c")
    snapshots = {str(p.relative_to(source)): provenance.sha256(p)
                 for p in sorted(source.rglob("*")) if p.is_file()}
    print("Build Quintic and QP 150", flush=True)
    libraries = {"Quintic": (build(planner, out / "Quintic", "quintic"), None),
                 "QP150": (build(planner, out / "QP150", "qp", iters=150), None)}
    lcc_source = planner / "src" / "pp_lcc.c"
    original_lcc = lcc_source.read_bytes()
    add_driver_hook(planner)
    for driver in (1, 2):
        name = f"Driver{driver}"
        print(f"Build {name}", flush=True)
        libraries[name] = (build(planner, out / name, "quintic",
                                 flags=f"-DPP_POTENTIAL_DRIVER={driver}"), "driver")
    lcc_source.write_bytes(original_lcc)
    add_qp_hook(planner)
    print("Build teacher and train the small MLP from synthetic QPs", flush=True)
    teacher = build(planner, out / "teacher", "qp", iters=600,
                    flags="-DPP_POTENTIAL_TEACHER=1 -DPP_POTENTIAL_NN=0")
    training = train(teacher, planner / "src" / "generators" / "pilot_weights.inc")
    print("Training:", training, flush=True)
    libraries["QP25"] = (build(planner, out / "QP25", "qp", iters=25,
                               flags="-DPP_POTENTIAL_TEACHER=0 -DPP_POTENTIAL_NN=0"), "qp")
    libraries["NN25"] = (build(planner, out / "NN25", "qp", iters=25,
                               flags="-DPP_POTENTIAL_TEACHER=0 -DPP_POTENTIAL_NN=1"), "qp")
    manifest = {
        "kind": "exploratory SIL", "source": snapshots, "git": provenance.git_state(),
        "suite": "PP-T7", "cases": CASES, "training": training,
        "hooks": {p.name: provenance.sha256(p) for p in (DRIVER_HOOK, QP_HOOK, Path(__file__))},
        "libraries": {name: provenance.library_infos(lib) for name, (lib, _) in libraries.items()},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    suite = sweep.load_suite("PP-T7")
    names = list(libraries)
    with (out / "runs.jsonl").open("w") as records:
        for index, (spec, seed) in enumerate(CASES):
            scenario = sweep.load_run(spec, object_list_on_empty_road=True)
            scope = sweep.scope_of(suite, spec)
            for name in names[index % len(names):] + names[:index % len(names)]:
                library, hook = libraries[name]
                row = {"variant": name, "case": scenario.name, "spec": spec, "seed": seed}
                row.update(run_case(library, scenario, seed, scope, hook))
                records.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                records.flush()
                print(f"{scenario.name} seed={seed} {name} failed={row['failed']} "
                      f"ay={row['vehicle']['ay_vehicle_r79_max']} {row.get('generator', '')}", flush=True)
    print(out / "runs.jsonl", flush=True)


if __name__ == "__main__":
    main()
