"""Simulator identity and the validation state of its models (SIM-REQ-121).

Every report that concludes on a planner names the simulator version and says, for each model
the run used, whether the model was validated against real data. The models and their text
are the ones of the Simulation Handbook (docs/vi/simulation-handbook.md, section 9 and 15);
tests/eval/test_credibility.py checks that both lists agree, so a model added here without a
handbook entry fails the test.

No real vehicle data exists in this project, so no model is validated yet. A model counts as
validated only when its `validated` flag is set together with the evidence in the handbook.
"""

from dataclasses import dataclass

from eval import checksum
from execution import bundle

HANDBOOK = "docs/vi/simulation-handbook.md"
NOT_VALIDATED = "Chưa validation: không có dữ liệu xe thật"
NOT_VALIDATED_STAND_IN = "Chưa validation: stand-in theo đặc tả, không có khối thật để đối chiếu"


@dataclass(frozen=True)
class Model:
    id: str          # also the handbook anchor: hb-model-<id>
    name: str
    validation: str
    validated: bool = False

    @property
    def anchor(self) -> str:
        return f"hb-model-{self.id}"


MODELS = (
    Model("vehicle", "Mô hình xe (bicycle, lốp tuyến tính, sáu vehicle profile)", NOT_VALIDATED),
    Model("controller", "Lateral Controller và EPS chạy thử", NOT_VALIDATED_STAND_IN),
    Model("acc", "ACC chạy thử", NOT_VALIDATED_STAND_IN),
    Model("adas", "Tài xế và Chức năng ADAS chạy thử", NOT_VALIDATED_STAND_IN),
    Model("arbitrator", "Arbitrator chạy thử (PP-ASM-022)", NOT_VALIDATED_STAND_IN),
    Model("camera", "Camera và lane model", NOT_VALIDATED),
    Model("objects", "Cảm biến đối tượng và traffic", NOT_VALIDATED),
    Model("timing", "Đồng hồ ECU, kênh truyền, lỗi timing", NOT_VALIDATED),
    Model("faults", "Fault injector", "Không áp dụng: không phải mô hình vật lý; kiểm bằng fault_hits và NEVER_S"),
)


def simulator_info(git: dict | None = None) -> dict:
    """What a manifest records about the simulator that made the run (eval.provenance.make)."""
    git = git or {}
    return {"commit": git.get("commit"), "dirty": git.get("dirty"),
            "checksum_version": checksum.VERSION, "bundle_schema": bundle.SCHEMA, "handbook": HANDBOOK,
            "models": [{"id": m.id, "name": m.name, "validation": m.validation, "validated": m.validated}
                       for m in MODELS]}


def simulator_text(info: dict | None = None) -> str:
    """One line for a report: version of simulator and evaluator, and the validation state."""
    if info is None:
        from eval import provenance  # not at import: provenance imports this module
        info = simulator_info(provenance.git_state())
    commit = (info.get("commit") or "")[:7]
    version = (commit + ("-dirty" if info.get("dirty") else "")) if commit else "không có git"
    models = info.get("models") or []
    validated = [m["name"] for m in models if m.get("validated")]
    state = (f"{len(validated)}/{len(models)} model đã validation" if validated
             else f"chưa model nào trong {len(models)} model được validation với dữ liệu thật")
    return (f"commit {version} (simulator và bên chấm), {info.get('checksum_version')}, {info.get('bundle_schema')}; "
            f"{state} (Simulation Handbook mục 9, 15)")
