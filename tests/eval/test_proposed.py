"""Criteria of proposed requirement texts (eval/proposed.py), on hand-made results."""

import math

import pytest

from eval import proposed
from eval.metrics import Criterion, Result


def result(ay_path, applicable=True, vehicle=None):
    criteria = [Criterion("PP-SWR-001", "a_y lớn nhất của path, HWA [m/s²]", ay_path, "<= 2.5",
                          ay_path <= 2.5, applicable=applicable)]
    info = {"ay_vehicle_r79_limits": [2.8, 3.3, 2.0]}
    if vehicle is not None:
        info.update({"ay_vehicle_r79_max": vehicle[0], "ay_vehicle_r79_within_limits": vehicle[1]})
    return Result("x", 1, criteria, [], info)


def test_path_ceiling_is_aysmax_plus_r79_margin():
    ok, over = (proposed.criteria(result(a), [proposed.PATH_AY_PROPOSED])[0] for a in (2.75, 2.85))
    assert ok.passed and ok.value == 2.75 and ok.limit == "<= 2.8"
    assert not over.passed
    # The current PP-SWR-001 stays as it was; the proposed one is a separate criterion.
    r = result(2.75)
    r.criteria.extend(proposed.criteria(r, [proposed.PATH_AY_PROPOSED]))
    assert [c.passed for c in r.criteria] == [False, True]


def test_path_ceiling_not_applicable_without_hwa():
    c = proposed.criteria(result(0.0, applicable=False), [proposed.PATH_AY_PROPOSED])[0]
    assert not c.applicable


def test_vehicle_criterion_follows_r79_measure():
    ok = proposed.criteria(result(2.5, vehicle=(2.9, True)), [proposed.VEHICLE_AY_R79])[0]
    bad = proposed.criteria(result(2.5, vehicle=(3.4, False)), [proposed.VEHICLE_AY_R79])[0]
    none = proposed.criteria(result(2.5), [proposed.VEHICLE_AY_R79])[0]
    assert ok.applicable and ok.passed and ok.value == 2.9
    assert bad.applicable and not bad.passed
    assert not none.applicable and math.isnan(none.value)


def test_unknown_proposed_criterion_is_an_error():
    with pytest.raises(ValueError):
        proposed.criteria(result(2.5), ["PP-SWR-999"])
