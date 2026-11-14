"""eval/ plugs in any planner library built against interfaces/c/pp_planner.h
(Software Qualification Test Specification 11), not only build/planner."""

import pickle
import sys

import pytest

import interfaces as I
from eval import planner_choice, provenance

VP0 = I.VehicleConfig(2.9, 1.45, 1.9, 15.0, 0.61, 6.0, 0.05)  # Software Qualification Test Specification 4.4
SUFFIX = ".dylib" if sys.platform == "darwin" else ".so"


@pytest.fixture(scope="module")
def stub(build_stub):
    return build_stub()


def no_motion(_request):
    return I.EgoMotionResponse(True, 0.0, 0.0, 0.0)


def test_any_library_runs_through_the_planner_contract(stub):
    factory = planner_choice.resolve(stub)
    assert factory.version().startswith("stub_planner ")
    planner = factory(VP0)
    assert planner.init_result is I.InitResult.OK
    counters = [planner.step(I.PlannerInputs(t0_us=k * I.PLANNER_PERIOD_US), no_motion)
                .path_status.header.counter for k in range(1, 4)]
    assert counters == [0, 1, 2]
    assert factory(None).init_result is I.InitResult.BAD_VEHICLE_CONFIG


def test_factory_is_picklable_for_worker_processes(stub):
    factory = planner_choice.resolve(stub)
    assert pickle.loads(pickle.dumps(factory)) == factory


def test_missing_library_stops_with_its_path(tmp_path):
    with pytest.raises(SystemExit, match="not found"):
        planner_choice.resolve(tmp_path / f"libnone{SUFFIX}")


def test_library_without_required_call_is_refused(build_stub):
    lib = build_stub("STUB_NO_STEP")
    with pytest.raises(SystemExit, match="missing pp_step"):
        planner_choice.resolve(lib)


def test_file_that_is_not_a_library_is_refused(tmp_path):
    bad = tmp_path / f"libbad{SUFFIX}"
    bad.write_bytes(b"not a library")
    with pytest.raises(SystemExit, match="cannot load"):
        planner_choice.resolve(bad)


def _manifest(lib: dict) -> dict:
    return {"git": {"commit": "f" * 40, "short": "fffffff", "dirty": False}, "libraries": [lib]}


def test_external_library_is_identified_by_hash_not_by_this_repository(stub):
    external = provenance.library_info(stub, external=True)
    assert external["sha256"] and external["pp_version"].startswith("stub_planner ")
    assert provenance.official_problems(_manifest(external)) == []
    # The same library as the default in-repo build must come from HEAD.
    in_repo = provenance.library_info(stub)
    assert provenance.official_problems(_manifest(in_repo))
