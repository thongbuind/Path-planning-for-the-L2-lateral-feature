"""Tạo các tệp dành cho SUT trong bundle. Trace MCAP làm tròn float để xem lại; bên chấm dùng
RunLog.
"""

from pathlib import Path

from eval import case, checksum, provenance
from execution import bundle

EVALUATION_SCHEMA = "evaluation/1"

# Mốc tuyệt đối theo đồng hồ sim, trừ trường khai báo trong exceptions. Khoảng thời gian không có
# clock domain (SIM-REQ-028).
TIME_DOMAINS = {
    "schema": "time_domains/1",
    "domains": ["sim", "camera", "adas"],
    "default": "sim",
    "exceptions": {
        "trace.mcap /planner/trajectory stamp_us": "adas",
        "trace.mcap /planner/function_requests rx_us": "adas",
        "trace.mcap /planner/cycle lane_capture_us": "camera",
    },
    "not_instants": [
        "resolved-case.json case.start_s: vị trí dọc đường [m]",
        "mọi giá trị *_s còn lại của resolved-case.json là thời gian của kịch bản, miền sim",
    ],
}


def write(folder: Path, *, run_id: str, parent: str | None, kind: str, doc: dict, planner, seed: int,
          log, result, command: str | None = None) -> dict:
    folder = Path(folder)
    libraries = provenance.library_infos(planner, external=True)
    lib = libraries[0]
    manifest = provenance.make(kind, doc["annotations"]["name"], {"seed": seed, "planner_only": planner.only})
    manifest["provenance_run_id"] = manifest["run_id"]
    manifest["run_id"] = run_id
    manifest["libraries"] = libraries
    behaviour = checksum.behavior_checksum(log)
    manifest["bundle"] = {"schema": bundle.SCHEMA, "parent_run_id": parent, "case_hash": doc["case_hash"],
                          "behavior_checksum": behaviour, "checksum_version": checksum.VERSION,
                          "resolved_case_schema": case.SCHEMA, "evaluation_schema": EVALUATION_SCHEMA,
                          "time_domains": TIME_DOMAINS, "recipe": doc["recipe"]}
    bundle.write_json(folder / "resolved-case.json", doc)
    bundle.write_json(folder / "evaluation.json", {"schema": EVALUATION_SCHEMA,
                                                   "evaluator_commit": manifest["git"]["commit"],
                                                   **result.to_dict()})
    from sim.logging import run_log
    run_log.write(log, folder / "trace.mcap", {"pp_version": str(lib["pp_version"]), "library_sha256": lib["sha256"],
                                               "commit": str(manifest["git"]["commit"]), "run_id": run_id,
                                               "rerun": command or ""})
    provenance.write(manifest, folder)
    return manifest
