"""PP-SWR-092: no LKA or ELK line intervention toward a side whose ego-lane line is not trusted
(Software Qualification Test Specification 8.1; PP-PR-038)."""

from types import SimpleNamespace

from eval import metrics
from interfaces import ActiveFunction, CancelReason, ElkReason, FunctionRequest, LineStatus, RequestState, Side

CAL = {"conf_ego": 0.5}
SEEN = ((LineStatus.MEASURED, 0.9),) * 4 + ((LineStatus.LOST, 0.0),) * 2
LEFT_LOST = ((LineStatus.MEASURED, 0.9), (LineStatus.LOST, 0.0),
             (LineStatus.MEASURED, 0.9), (LineStatus.MEASURED, 0.9)) + ((LineStatus.LOST, 0.0),) * 2


def cycles(boundaries, n=10):
    return [SimpleNamespace(inputs_ok={"lane_model": True}, lane_boundaries=boundaries, t0_us=i * 25_000)
            for i in range(n)]


def request(reason=ElkReason.SOLID_LINE, side=Side.LEFT):
    message = FunctionRequest(RequestState.REQUEST, side, 1.0, reason, CancelReason.NONE)
    return metrics._Request(2, 8, 50_000, message)


def test_refusal_is_correct_only_when_the_line_is_unseen_for_the_whole_request():
    r = request()
    assert metrics._refused_unseen_line(cycles(LEFT_LOST), ActiveFunction.ELK, r, CAL)
    assert not metrics._refused_unseen_line(cycles(SEEN), ActiveFunction.ELK, r, CAL)
    mixed = cycles(LEFT_LOST)
    mixed[5].lane_boundaries = SEEN  # line back during the request: the planner must start
    assert not metrics._refused_unseen_line(mixed, ActiveFunction.ELK, r, CAL)


def test_road_edge_elk_is_judged_by_047_not_092():
    r = request(ElkReason.ROAD_EDGE)
    assert not metrics._refused_unseen_line(cycles(LEFT_LOST), ActiveFunction.ELK, r, CAL)


def test_starting_toward_an_unseen_line_fails():
    r = request()
    started = metrics._Intervention(ActiveFunction.ELK, 3, 8, False, r)
    requests = {ActiveFunction.LKA: [], ActiveFunction.ELK: [r]}
    bad = metrics._unseen_line_criterion(cycles(LEFT_LOST), [started], requests, CAL)
    assert bad.applicable and not bad.passed and bad.value == 1.0
    ok = metrics._unseen_line_criterion(cycles(LEFT_LOST), [], requests, CAL)
    assert ok.applicable and ok.passed
    unseen_not_tested = metrics._unseen_line_criterion(cycles(SEEN), [started], requests, CAL)
    assert not unseen_not_tested.applicable
