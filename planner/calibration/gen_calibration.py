#!/usr/bin/env python3
"""Sinh calibration theo đơn vị SI và kiểm giới hạn để biên dịch vào thư viện (PP-ADR-013)."""

import argparse
import math
import re
from pathlib import Path

import yaml

UNITS = {"deg": ("rad", math.pi / 180.0), "ms": ("s", 1e-3)}
BANNER = "Sinh từ planner/calibration/gen_calibration.py."


def _si(value: float, unit: str) -> tuple[float, str]:
    si_unit, factor = UNITS.get(unit, (unit, 1.0))
    return float(value) * factor, si_unit


def _f(value: float) -> str:
    return f"{value!r}F"


def generate(params: dict) -> tuple[str, str]:
    header = [f"/* {BANNER} */", "", "#ifndef PP_CALIBRATION_H", "#define PP_CALIBRATION_H", "",
              "#include <stdbool.h>", "", "typedef struct {"]
    values, checks = [], []
    for name, spec in params.items():
        value, unit = _si(spec["value"], spec.get("unit", "-"))
        header.append(f"    float {name}; /* [{unit}] {spec.get('source', '')} */")
        values.append(f"    .{name} = {_f(value)},")
        conditions = [f"isfinite(cal->{name})"]
        for key, op in (("min", ">="), ("max", "<="), ("gt", ">"), ("lt", "<")):
            if key in spec:
                limit, _ = _si(spec[key], spec.get("unit", "-"))
                conditions.append(f"(cal->{name} {op} {_f(limit)})")
        if "gt_param" in spec:
            other = spec["gt_param"]
            if other not in params:
                raise SystemExit(f"{name}: gt_param {other} is not a parameter")
            conditions.append(f"(cal->{name} > cal->{other})")
        checks.append("    ok = ok && " + " && ".join(conditions) + ";")
    header += ["} pp_calibration_t;", "",
               "extern const pp_calibration_t pp_calibration;", "",
               "bool pp_calibration_check(const pp_calibration_t *cal);", "",
               "#endif", ""]
    source = [f"/* {BANNER} */", "", "#include <math.h>", "", '#include "pp_calibration.h"', "",
              "const pp_calibration_t pp_calibration = {"] + values + ["};", "",
              "bool pp_calibration_check(const pp_calibration_t *cal)", "{",
              "    bool ok = (cal != NULL);",
              "    if (ok) {"] + ["    " + c for c in checks] + ["    }", "    return ok;", "}", ""]
    source.insert(3, "#include <stddef.h>")
    return "\n".join(header), "\n".join(source)


def merge_extra(params: dict, extra: dict, origin: str) -> dict:
    """Thêm tham số riêng của generator lab (khóa calibration trong generator.yaml).

    Mọi tên phải bắt đầu bằng calibration_prefix + "_". Tiền tố không được trùng từ đầu của một tham
    số chung, và tên không được trùng tham số đã có.
    """
    own = extra.get("calibration") or {}
    if not own:
        return params
    prefix = extra.get("calibration_prefix")
    if not isinstance(prefix, str) or not re.fullmatch(r"[a-z][a-z0-9]*", prefix):
        raise SystemExit(f"{origin}: calibration needs calibration_prefix (lower-case letters and digits)")
    base_words = {name.split("_")[0].lower() for name in params}
    if prefix in base_words:
        raise SystemExit(f"{origin}: calibration_prefix {prefix!r} is already used by the shared calibration")
    merged = dict(params)
    for name, spec in own.items():
        if not name.startswith(prefix + "_"):
            raise SystemExit(f"{origin}: {name} must start with {prefix}_")
        if name in merged:
            raise SystemExit(f"{origin}: {name} is already a calibration parameter")
        merged[name] = spec
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the calibration struct of the planner from calibration.yaml (build time).",
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--extra", type=Path, action="append", default=[],
                        help="generator.yaml of a lab T7 generator: its calibration is appended")
    args = parser.parse_args()
    params = yaml.safe_load(args.input.read_text(encoding="utf-8"))["parameters"]
    for path in args.extra:
        params = merge_extra(params, yaml.safe_load(path.read_text(encoding="utf-8")) or {}, str(path))
    header, source = generate(params)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "pp_calibration.h").write_text(header, encoding="utf-8")
    (args.out_dir / "pp_calibration.c").write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
