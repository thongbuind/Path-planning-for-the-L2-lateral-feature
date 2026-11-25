"""Mốc tiêm lỗi tính từ chu kỳ planner đầu tiên xuất hiện sự kiện tương ứng (SQTS 6)."""

from interfaces import InterventionPhase, LccMode
from sim.stand_ins.arbitrator import SystemStatus

EVENTS = ("lka_active", "elk_active", "intervention_active",
          "lka_completed", "elk_completed", "intervention_completed", "lcc_follow")
NEVER_S = 1e9  # Giá trị mốc khi sự kiện kích hoạt lỗi chưa xảy ra.


def check(trigger: str | None) -> None:
    if trigger is not None and trigger not in EVENTS:
        raise ValueError(f"unknown fault trigger {trigger!r}")


def happened(event: str, status: SystemStatus) -> bool:
    if not status.path_valid:
        return False
    if event == "lcc_follow":
        return status.lcc_mode == LccMode.FOLLOW
    name, _, state = event.rpartition("_")
    phase = InterventionPhase.ACTIVE if state == "active" else InterventionPhase.COMPLETED
    lka = status.lka_phase == phase
    elk = status.elk_phase == phase
    return {"lka": lka, "elk": elk, "intervention": lka or elk}[name]


class EventCounter:
    def __init__(self) -> None:
        self.times: dict[str, list[int]] = {e: [] for e in EVENTS}
        self._held = {e: False for e in EVENTS}

    def update(self, status: SystemStatus, t_us: int) -> list[str]:
        started = []
        for event in EVENTS:
            now = happened(event, status)
            if now and not self._held[event]:
                self.times[event].append(t_us)
                started.append(event)
            self._held[event] = now
        return started
