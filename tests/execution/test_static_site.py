import re
from pathlib import Path

WEB = Path(__file__).resolve().parents[2] / "web"
INTERNAL = re.compile(r"\b(?:WP-\d|GAP-\d|SIM-REQ-\d|D-\d{2}\b)")


def test_static_build_copies_only_the_placeholder():
    script = (WEB / "build-static.cjs").read_text(encoding="utf-8")
    assert 'path.join(site, "simulation-static")' in script
    assert 'path.join(site, "simulation")' not in script


def test_placeholder_has_no_internal_codes():
    files = [p for p in (WEB / "simulation-static").rglob("*") if p.is_file()]
    assert files
    for path in files:
        assert not INTERNAL.search(path.read_text(encoding="utf-8")), path


def test_workbench_screens_do_not_show_internal_codes():
    for path in (WEB / "simulation").rglob("*"):
        if path.suffix in (".js", ".html", ".css"):
            assert not INTERNAL.search(path.read_text(encoding="utf-8")), path
