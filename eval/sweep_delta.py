"""PP-SWR-013 đo phần PP-SWR-050 tăng so với lần chạy không có độ trễ."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_DIR = ROOT / "build" / "matrix"


def _group(run: dict, key: str) -> tuple:
    sim = {k: v for k, v in (run.get("sim") or {}).items() if k != key}
    return (tuple(run["run"]), run["acc"], run["profile"], run["seed"], tuple(sorted(sim.items())))


def deltas(runs: list[dict], key: str, base: float, target: str, default: float) -> list[dict]:
    level = lambda r: float((r.get("sim") or {}).get(key, default))  # noqa: E731
    bases = {_group(r, key): r for r in runs if level(r) == base}
    out = []
    for r in runs:
        partner = bases.get(_group(r, key))
        value = r.get("targets", {}).get(target)
        if partner is None or value is None or partner.get("targets", {}).get(target) is None:
            continue
        b = partner["targets"][target]
        out.append({"name": r["name"], "level": level(r), "value": value, "base_value": b,
                    "delta": value - b})
    return sorted(out, key=lambda d: (d["name"].split(" [")[0], d["level"]))


def table(rows: list[dict], key: str, target: str) -> list[str]:
    lines = [f"| Chạy | {key} | {target} | Ở mức gốc | Tăng thêm |", "|---|---|---|---|---|"]
    lines += [f"| {d['name']} | {d['level']:g} | {d['value']:.3f} | {d['base_value']:.3f} | {d['delta']:+.3f} |"
              for d in rows]
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Change of a target across the levels of a simulator sweep (Software Qualification "
            "Test"
        ),
    )
    parser.add_argument("suite")
    parser.add_argument("--key", required=True, help="Simulator value swept, e.g. camera_latency_ms")
    parser.add_argument("--base", type=float, required=True, help="Level the others are compared with")
    parser.add_argument("--target", default="PP-SWR-050")
    args = parser.parse_args()
    from dataclasses import fields
    from sim.scenario import Scenario
    default = next(f.default for f in fields(Scenario) if f.name == args.key)
    folder = MATRIX_DIR / args.suite
    runs = json.loads((folder / "runs.json").read_text(encoding="utf-8"))
    lines = [f"# {args.suite}: {args.target} so với {args.key} = {args.base:g}", ""]
    lines += table(deltas(runs, args.key, args.base, args.target, float(default)), args.key, args.target)
    (folder / "delta.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
