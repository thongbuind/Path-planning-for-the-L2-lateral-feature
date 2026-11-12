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
| lka_completed, elk_completed, intervention_completed | as above with phase COMPLETED |

A trigger that never happens leaves its fault uninjected; the run log says so. The scripted
driver and FunctionRequests use the same events (sim.stand_ins.driver repeats,
sim.stand_ins.scripted RequestEvent): a driver repeat waits for the next occurrence, so
repeated interventions (S16) are counted by EventCounter.
"""

from interfaces import InterventionPhase, PathStatus

EVENTS = ("lka_active", "elk_active", "intervention_active",
          "lka_completed", "elk_completed", "intervention_completed")
NEVER_S = 1e9  # start of a fault whose event has not happened yet


def check(trigger: str | None) -> None:
    if trigger is not None and trigger not in EVENTS:
        raise ValueError(f"unknown fault trigger {trigger!r}")


def happened(event: str, status: PathStatus) -> bool:
    if not status.path_valid:
        return False
    name, _, state = event.rpartition("_")
    phase = InterventionPhase.ACTIVE if state == "active" else InterventionPhase.COMPLETED
    lka = status.lka_phase == phase
    elk = status.elk_phase == phase
    return {"lka": lka, "elk": elk, "intervention": lka or elk}[name]


class EventCounter:
    """Occurrences of each event: the planner t0 of every cycle where it starts to hold."""

    def __init__(self) -> None:
        self.times: dict[str, list[int]] = {e: [] for e in EVENTS}
        self._held = {e: False for e in EVENTS}

    def update(self, status: PathStatus, t_us: int) -> list[str]:
        """Events that started at this cycle."""
        started = []
        for event in EVENTS:
            now = happened(event, status)
            if now and not self._held[event]:
                self.times[event].append(t_us)
                started.append(event)
            self._held[event] = now
        return started
