"""Campaigns: a frozen list of runs, started together, followed together, repeatable on a new build.

A campaign is a file `<store>/<id>.json` ("campaign/1") with its name and its items, one configuration each
(the same body as POST /api/runs). The runs are ordinary workbench runs: they go through the one
supervisor, so no more than N_max run at a time and the rest wait in QUEUED; each has its own bundle.
The campaign only remembers which runs are its own. The state of a campaign is read from the runs, never
stored. Its runs are pinned, so retention does not remove them while the campaign exists.

Coverage, from the designed list down to what could be judged:
  designed    items in the frozen list
  scheduled   items handed to the supervisor
  ran         runs that ended COMPLETED (the others failed, timed out or were cancelled)
  judged      completed runs with at least one applicable criterion and no case not-judged issue
The fifth level of the plan, the condition really happening (a fault really injected), is not in the
evaluation of a run yet; the answer says so and does not guess it.

Imports no SUT package. A scenario, fault or vehicle that does not exist makes its run fail with a reason
(the worker resolves the case), which the campaign shows; the server checks only the shape.
"""

import itertools
import json
import re
import time
from pathlib import Path

from execution import bundle as B
from workbench import evidence

MAX_RUNS = 40               # below N_keep (50): the pinned runs of a campaign are never pruned
MAX_NAME = 80
ID = re.compile(r"^[0-9]{8}-[0-9]{6}-[0-9a-f]{6}$")
SID = re.compile(r"^S\d+[a-z]?$")
VARIANT = re.compile(r"^[a-z][a-z0-9-]*$")
FAULT = re.compile(r"^F\d{2}$")
LEVEL = re.compile(r"^[a-z]$")
VEHICLE = re.compile(r"^VP-\d+$")
ACTIVE = ("QUEUED", "RUNNING", "PAUSED")
SCHEMA = "campaign/1"


class CampaignError(ValueError):
    """The request cannot make a campaign (HTTP 400)."""


def _list(value, what: str) -> list:
    if not isinstance(value, list) or not value:
        raise CampaignError(f"{what} phải là danh sách không rỗng")
    return value


def expand(spec: dict) -> list[dict]:
    """The configurations of a campaign: `items` as given, or the product of a `matrix`."""
    if "items" in spec:
        items = _list(spec["items"], "items")
        if not all(isinstance(c, dict) for c in items):
            raise CampaignError("mỗi mục của items phải là một cấu hình")
        configs = [{**c, "rate": 0} for c in items]
    elif "matrix" in spec:
        m = spec["matrix"]
        if not isinstance(m, dict):
            raise CampaignError("matrix phải là một đối tượng")
        scenarios = _list(m.get("scenarios"), "scenarios")
        for s in scenarios:
            if not (isinstance(s, dict) and SID.match(str(s.get("sid", ""))) and VARIANT.match(str(s.get("v", "")))):
                raise CampaignError("kịch bản không hợp lệ (cần sid như S1 và biến thể như a)")
        fault_sets = m.get("fault_sets") or [[]]
        for fs in fault_sets:
            if not (isinstance(fs, list) and all(isinstance(f, list) and len(f) == 2 and FAULT.match(str(f[0]))
                                                 and LEVEL.match(str(f[1])) for f in fs)):
                raise CampaignError("tập lỗi không hợp lệ (cần dạng [[\"F04\", \"a\"]])")
        vehicles = m.get("vehicles") or ["VP-0"]
        if not all(VEHICLE.match(str(v)) for v in vehicles):
            raise CampaignError("mẫu xe không hợp lệ")
        seeds = m.get("seeds") or [1]
        if not all(isinstance(s, int) and not isinstance(s, bool) and 0 <= s <= 9999 for s in seeds):
            raise CampaignError("seed phải là số nguyên từ 0 đến 9999")
        if len(scenarios) * len(fault_sets) * len(vehicles) * len(seeds) > MAX_RUNS:
            raise CampaignError(f"campaign có quá {MAX_RUNS} run; chia nhỏ ra")
        configs = [{"scenario": {"sid": s["sid"], "v": s["v"]}, "faults": faults, "trigger": m.get("trigger"),
                    "vehicle": vehicle, "seed": seed, "sim": m.get("sim") or {}, "acc": m.get("acc"), "rate": 0}
                   for s, faults, vehicle, seed in itertools.product(scenarios, fault_sets, vehicles, seeds)]
    else:
        raise CampaignError("cần matrix hoặc items")
    if len(configs) > MAX_RUNS:
        raise CampaignError(f"campaign có quá {MAX_RUNS} run; chia nhỏ ra")
    unique = {json.dumps({k: v for k, v in c.items() if k != "rate"}, sort_keys=True) for c in configs}
    if len(unique) != len(configs):
        raise CampaignError("có hai run trùng cấu hình trong campaign")
    return configs


def _label(config: dict) -> str:
    sc = config.get("scenario") or {}
    faults = " ".join("".join(f) for f in config.get("faults") or [])
    return " ".join(x for x in (f"{sc.get('sid', '')} {sc.get('v', '')}".strip(), faults,
                               config.get("vehicle") or "", f"seed {config.get('seed', 1)}") if x)


def _path(store: Path, cid: str) -> Path:
    if not ID.match(cid):
        raise KeyError(cid)
    return Path(store) / f"{cid}.json"


def read(store: Path, cid: str) -> dict:
    path = _path(store, cid)
    if not path.is_file():
        raise KeyError(cid)
    return json.loads(path.read_text(encoding="utf-8"))


def create(store: Path, supervisor, spec: dict, parent: str | None = None, label_of=None) -> dict:
    """Freeze the list, write the file, hand every run to the supervisor, pin them."""
    name = str(spec.get("name") or "").strip()[:MAX_NAME]
    if not name:
        raise CampaignError("campaign cần một tên")
    configs = expand(spec)
    store = Path(store)
    store.mkdir(parents=True, exist_ok=True)
    cid = B.new_run_id()
    items = [{"config": c, "label": (label_of or _label)(c), "run_id": None} for c in configs]
    doc = {"schema": SCHEMA, "id": cid, "name": name, "created": time.time(), "parent_campaign": parent,
           "items": items}
    B.write_json(_path(store, cid), doc)                 # frozen before any run starts
    try:
        for i, item in enumerate(items):
            item["run_id"] = supervisor.submit({"config": item["config"]}, label=item["label"])
            supervisor.pin(item["run_id"], True)
    finally:
        B.write_json(_path(store, cid), doc)             # the run ids, also after a failure half way
    return doc


# ---- state -------------------------------------------------------------------------------

def _item_state(supervisor, item: dict) -> dict:
    out = {"index": None, "label": item["label"], "run_id": item.get("run_id"), "state": "NOT_STARTED",
           "failure": None, "verdict": None, "applicable": None, "passed": None, "first_fail": None}
    rid = item.get("run_id")
    if not rid:
        return out
    try:
        status = supervisor.status(rid)
    except KeyError:
        out["state"] = "MISSING"
        return out
    state = status.get("state") or (status.get("execution") or {}).get("state")
    out["state"] = state
    out["failure"] = status.get("failure") or (status.get("execution") or {}).get("failure")
    if state in ("COMPLETED", "FAILED", "TIMED_OUT", "CANCELLED"):
        folder = supervisor.s.root / rid
        if (folder / "execution.json").is_file():
            summary = evidence.run_summary(folder)
            out.update({k: summary.get(k) for k in ("verdict", "applicable", "passed", "first_fail")})
    return out


def status(store: Path, supervisor, cid: str) -> dict:
    doc = read(store, cid)
    items = []
    for i, item in enumerate(doc["items"]):
        st = _item_state(supervisor, item)
        st["index"] = i
        items.append(st)
    n = len(items)

    def count(*states):
        return sum(1 for s in items if s["state"] in states)

    completed = [s for s in items if s["state"] == "COMPLETED"]
    judged = [s for s in completed if s["verdict"] in ("pass", "fail")]
    coverage = {"designed": n, "scheduled": sum(1 for s in items if s["run_id"]), "ran": len(completed),
                "judged": len(judged), "not_judged": sum(1 for s in completed if s["verdict"] == "not_judged"),
                "condition_observed": None}
    counts = {"queued": count("QUEUED"), "running": count("RUNNING", "PAUSED"), "completed": len(completed),
              "failed": count("FAILED", "TIMED_OUT"), "cancelled": count("CANCELLED"), "missing": count("MISSING"),
              "pass": sum(1 for s in judged if s["verdict"] == "pass"),
              "fail": sum(1 for s in judged if s["verdict"] == "fail")}
    active = counts["queued"] + counts["running"]
    return {"id": doc["id"], "name": doc["name"], "created": doc["created"], "parent_campaign": doc.get("parent_campaign"),
            "state": "running" if active else "done", "counts": counts, "coverage": coverage, "items": items,
            "frozen": True}


def listing(store: Path, supervisor) -> list[dict]:
    out = []
    store = Path(store)
    for path in sorted(store.glob("*.json"), reverse=True) if store.is_dir() else []:
        if not ID.match(path.stem):
            continue
        try:
            s = status(store, supervisor, path.stem)
        except (KeyError, ValueError):
            continue
        out.append({k: s[k] for k in ("id", "name", "created", "state", "counts", "coverage", "parent_campaign")})
    return sorted(out, key=lambda c: c["created"], reverse=True)


def cancel(store: Path, supervisor, cid: str) -> dict:
    """Cancel the runs of this campaign that have not ended; no other run is touched."""
    doc = read(store, cid)
    cancelled = 0
    for item in doc["items"]:
        rid = item.get("run_id")
        if not rid:
            continue
        try:
            if supervisor.status(rid).get("state") in ACTIVE:
                supervisor.cancel(rid)
                cancelled += 1
        except KeyError:
            continue
    return {"cancelled": cancelled}


def repeat(store: Path, supervisor, cid: str, label_of=None) -> dict:
    """The same frozen list again (a new build, a new calibration): a new campaign with new runs."""
    doc = read(store, cid)
    spec = {"name": f"{doc['name']} (lặp lại)"[:MAX_NAME], "items": [i["config"] for i in doc["items"]]}
    return create(store, supervisor, spec, parent=cid, label_of=label_of)


def delete(store: Path, supervisor, cid: str) -> None:
    """Remove the campaign and unpin its runs (retention may then remove them). Not while a run is active."""
    doc = read(store, cid)
    if any(_item_state(supervisor, i)["state"] in ACTIVE for i in doc["items"]):
        raise CampaignError("campaign còn run đang chạy hoặc đang chờ: hủy trước")
    for item in doc["items"]:
        if item.get("run_id"):
            supervisor.pin(item["run_id"], False)
    _path(store, cid).unlink()
