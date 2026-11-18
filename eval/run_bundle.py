"""Files of a run bundle written by the path planner package (execution.bundle defines the folder).

    resolved-case.json   eval.case.document
    evaluation.json      metrics.evaluate plus the differential criteria; evaluator commit
    trace.mcap           sim.logging.run_log, for viewing (floats rounded; never re-scored)
    manifest.json        provenance.make plus the bundle identity: run_id, parent_run_id,
                         case_hash, behavior_checksum and the schema versions

Used by eval.runner (the CLI finalizes its own bundle) and eval.live (the supervisor finalizes).
"""

from pathlib import Path

from eval import case, checksum, provenance
from execution import bundle

EVALUATION_SCHEMA = "evaluation/1"


def write(folder: Path, *, run_id: str, parent: str | None, kind: str, doc: dict, planner, seed: int,
          log, result, command: str | None = None) -> dict:
    """Writes the four files into `folder`; returns the manifest."""
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
                          "recipe": doc["recipe"]}
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
