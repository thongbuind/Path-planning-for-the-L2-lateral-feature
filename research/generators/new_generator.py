"""Tạo generator lab mới từ templates/generator và đánh dấu developing trong registry.yaml."""

import argparse
import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "templates" / "generator"
REGISTRY = HERE / "registry.yaml"
NAME = re.compile(r"[a-z][a-z0-9_]*")


def prefix_of(name: str) -> str:
    return "".join(word[0] for word in name.split("_") if word)


def render(text: str, name: str, prefix: str) -> str:
    return text.replace("__NAME__", name).replace("__UPPER__", name.upper()).replace("__PREFIX__", prefix)


def create(name: str, prefix: str, base: str, root: Path = HERE) -> Path:
    if not NAME.fullmatch(name):
        raise SystemExit(f"{name}: lower-case letters, digits and _ only")
    if not re.fullmatch(r"[a-z][a-z0-9]*", prefix):
        raise SystemExit(f"{prefix}: calibration prefix must be lower-case letters and digits")
    target = root / name
    if target.exists():
        raise SystemExit(f"{target} already exists")
    for source in sorted(p for p in TEMPLATE.rglob("*") if p.is_file()):
        dest = target / render(str(source.relative_to(TEMPLATE)), name, prefix)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(source.read_text(encoding="utf-8"), name, prefix), encoding="utf-8")
    yaml_path = target / "generator.yaml"
    yaml_path.write_text(yaml_path.read_text(encoding="utf-8").replace("base: quintic_duration", f"base: {base}"),
                         encoding="utf-8")
    return target


def mark_developing(name: str, registry: Path = REGISTRY) -> None:
    """Chỉ đổi dòng status của mục đã có, để giữ chú thích của registry."""
    lines = registry.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(f"  {name}:")
    except ValueError:
        raise SystemExit(f"{name} is not in {registry.name}: add it there first (contract session)") from None
    for i in range(start + 1, len(lines)):
        if not lines[i].startswith("    "):
            break
        if lines[i].strip().startswith("status:"):
            lines[i] = "    status: developing"
            registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise SystemExit(f"{name} has no status in {registry.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a lab T7 generator from the template")
    parser.add_argument("name", help="Algorithm name, e.g. quintic_tangent_point (must be in registry.yaml)")
    parser.add_argument("--prefix", help="Calibration prefix; default: initials of the name")
    args = parser.parse_args()
    entry = (yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["generators"]).get(args.name)
    if entry is None or entry.get("kind") != "lab":
        raise SystemExit(f"{args.name}: not a lab generator in {REGISTRY.name}")
    target = create(args.name, args.prefix or prefix_of(args.name), entry.get("base", "quintic_duration"))
    mark_developing(args.name)
    print(f"Created {target.relative_to(HERE.parents[1])}")


if __name__ == "__main__":
    main()
