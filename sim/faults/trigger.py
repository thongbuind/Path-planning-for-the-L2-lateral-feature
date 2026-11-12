"""Faults started by an event in the planner output (Software Qualification Test
Specification 6: at LKA or ELK activation, and during the intervention).

A fault with `trigger` set starts `start_s` seconds after the first planner cycle whose
PathStatus shows the event; before that it is inactive. `duration_s` keeps its meaning.
The event is read from the planner output only, as the evaluator sees it.

| trigger | Event |
|---|---|
| lka_active | first PathStatus with path_valid and lka_phase ACTIVE |
| elk_active | first PathStatus with path_valid and elk_phase ACTIVE |
| intervention_active | first PathStatus with path_valid and lka_phase or elk_phase ACTIVE |

A trigger that never happens leaves its fault uninjected; the run log says so.
"""

from interfaces import InterventionPhase, PathStatus

EVENTS = ("lka_active", "elk_active", "intervention_active")
NEVER_S = 1e9  # start of a fault whose event has not happened yet


def check(trigger: str | None) -> None:
    if trigger is not None and trigger not in EVENTS:
        raise ValueError(f"unknown fault trigger {trigger!r}")


def happened(event: str, status: PathStatus) -> bool:
    if not status.path_valid:
        return False
    lka = status.lka_phase == InterventionPhase.ACTIVE
    elk = status.elk_phase == InterventionPhase.ACTIVE
    return {"lka_active": lka, "elk_active": elk, "intervention_active": lka or elk}[event]
