"""PP-SWR-129, 130 by a reference twin of the same seed (Software Qualification Test
Specification 6: F15, F16, F17), on a short run with the stub planner library."""

from adapters.sil.sil_planner import PlannerLibrary
from eval import differential
from sim.faults.channel import ChannelFault
from sim.harness import Harness
from sim.scenario import Scenario
from sim.world.road import Segment


def test_twin_drops_exactly_the_messages_hit_and_outputs_are_compared(build_stub):
    planner = PlannerLibrary(build_stub())
    faults = (ChannelFault("counter_repeat", "lane_model", start_s=0.5, duration_s=0.5, every=2, value=10.0),
              ChannelFault("counter_stuck", "speed", start_s=0.5, duration_s=0.2))
    scenario = Scenario(name="short", segments=(Segment("straight", 200.0),), lane_width=3.5, speed_mps=20.0,
                        duration_s=1.5, channel_faults=faults)
    log = Harness(scenario, planner, seed=1).run()
    assert log.fault_hits[0] == [] and len(log.fault_hits[1]) == 10  # 0.2 s of 20 ms speed frames
    twin, requirements = differential.twin_of(scenario, log)
    assert requirements == {"PP-SWR-129", "PP-SWR-130"}
    assert [f.kind for f in twin.channel_faults] == ["drop_listed"]
    assert twin.channel_faults[0].indices == tuple(log.fault_hits[1])
    criteria = {c.id: c for c in differential.criteria(scenario, log, planner, 1)}
    assert set(criteria) == {"PP-SWR-129", "PP-SWR-130"} and all(c.applicable for c in criteria.values())
