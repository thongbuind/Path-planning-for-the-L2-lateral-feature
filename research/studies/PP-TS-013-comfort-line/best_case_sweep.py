#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prototype as P  # noqa: E402

V = 25.0
R = V**2 / 2.0
LC_MAX = 60.0
VIEW = float(sys.argv[1]) if len(sys.argv) > 1 else P.VIEW_M


def curve(deg: float, sign: float) -> list:
    """Dùng clothoid–cung–clothoid. Góc quá nhỏ thì dùng cặp clothoid không có cung."""
    k = sign / R
    need = np.radians(deg) * R
    lc = min(LC_MAX, need)
    arc = need - lc
    segs = [(lc, 0.0, k)]
    if arc > 1e-6:
        segs.append((arc, k, k))
    segs.append((lc, k, 0.0))
    return segs


def make(kind: str, deg: float) -> P.Road:
    segs = [(150.0, 0.0, 0.0)] + curve(deg, 1.0)
    if kind == "S":
        segs += curve(deg, -1.0)
    segs.append((250.0, 0.0, 0.0))
    end = sum(s[0] for s in segs[:-1])
    return P.Road(f"{kind}{deg:.0f}", "", V, segs, (100.0, end + 120.0)).build()


def main():
    rows = []
    for kind in ("đơn", "S"):
        for deg in (6, 10, 15, 20, 30, 45, 90):
            road = make("S" if kind == "S" else "C", deg)
            st = {}
            d = P.plan_receding(road, P.CORRIDOR, view=VIEW, cont_stats=st)
            b = P.path_metrics(road, np.zeros_like(road.kn))
            m = P.path_metrics(road, d)
            curve_len = sum(s[0] for s in road.segs[1:-1])
            row = {
                "kind": kind, "deg": deg, "curve_len": curve_len,
                "ay_b": b["ay_peak"], "ay_n": m["ay_peak"],
                "ay_pc": 100 * (m["ay_peak"] - b["ay_peak"]) / b["ay_peak"],
                "jrms_pc": 100 * (m["jerk_rms"] - b["jerk_rms"]) / b["jerk_rms"],
                "cont": st.get("max", 0.0),
            }
            rows.append(row)
            print(f"{kind:3s} {deg:3d}°  dài {curve_len:5.0f} m  a_y {row['ay_b']:.2f}→{row['ay_n']:.2f} "
                  f"({row['ay_pc']:+5.1f} %)  jerk rms {row['jrms_pc']:+5.1f} %  path đổi {row['cont'] * 1000:5.1f} mm",
                  flush=True)
    (HERE / f"best_case_sweep_view{VIEW:.0f}.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
