"""ASAM migration, portable generation, sampling coverage and input integrity."""
from itertools import combinations, product
import json
from pathlib import Path
import shutil

import pytest

from eval import generate, loader, openx, provenance, suite
from sim.faults.lane import LaneFault

FIXTURES = Path(__file__).parent / 'fixtures'
BENCHMARK = openx.ROOT / 'benchmark'


def test_all_old_scenario_values_preserved():
    for old in json.loads((FIXTURES / 'legacy_scenarios.json').read_text()).values():
        p = old['parameters']
        s = loader.load(p['scenario_id'], p['variant'])
        assert [[seg.kind, seg.length, seg.curvature_end] for seg in s.segments] == old['segments']
        for field, parameter in [('lane_width', 'lane_width_m'), ('speed_mps', 'speed_mps'),
                                 ('duration_s', 'duration_s'), ('hwa_request_s', 'hwa_request_s'),
                                 ('start_s', 'start_s_m'), ('start_offset_m', 'start_offset_m'),
                                 ('start_heading_rad', 'start_heading_rad')]:
            assert getattr(s, field) == pytest.approx(p[parameter]), (s.name, field)
        for key in ('profile', 'acc', 'hold_until_hwa'):
            assert getattr(s, key) == p[key]


def test_all_old_fault_values_preserved():
    for fid, levels in json.loads((FIXTURES / 'legacy_faults.json').read_text()).items():
        for level, spec in levels.items():
            if 'lines' in spec:
                spec['lines'] = tuple(spec['lines'])
            assert loader.load_fault(fid, level) == LaneFault(**spec)


def test_unknown_anchor_rejected():
    with pytest.raises(KeyError): loader.load('S1b', 'z')
    with pytest.raises(KeyError): loader.load_fault('F04', 'e')


def test_added_regulatory_anchor_geometry():
    s = loader.load('S1', 'f')
    assert [x.length for x in s.segments[1:7]] == [30, 57.1, 14, 26, 5.1, 39]
    assert s.segments[2].curvature_end == pytest.approx(1 / 787)
    assert s.segments[5].curvature_end == pytest.approx(-1 / 374)
    assert loader.load('S14', 'e').segments == s.segments
    assert loader.load('S1b', 'f').speed_mps ** 2 * loader.load('S1b', 'f').segments[-1].curvature_end == pytest.approx(625 / 230)


def test_all_sources_pass_official_xsd():
    for path in BENCHMARK.rglob('*'):
        if path.suffix in ('.xosc', '.xodr'):
            openx.validate(path)


def test_schema_rejects_nonstandard_xml(tmp_path):
    path = tmp_path / 'bad.xosc'
    root = openx.parse(BENCHMARK / 'scenarios/S1.xosc')
    openx.node(root, 'FakeScenario')
    openx.write(root, path)
    with pytest.raises(Exception, match='FakeScenario'):
        openx.validate(path)


def test_portable_concrete_matches_anchor_and_bakes_road(tmp_path):
    source = BENCHMARK / 'scenarios/S1.xosc'
    params = {**openx.anchors(source)['d'], 'profile': 'VP-5', 'direction': -1., 'lane_width_m': 5.5}
    destination = tmp_path / 'generated' / 'curve.xosc'
    openx.concrete(source, destination, params)
    moved = tmp_path / 'moved'
    shutil.move(str(destination.parent), moved)
    actual = openx.load_scenario(moved / destination.name)
    assert actual == openx.load_scenario(source, params)
    root = openx.parse(moved / destination.name)
    assert root.find('.//Dimensions').get('width') == '2.5'
    assert not any('$' in v for n in root.iter() for v in n.attrib.values())
    openx.validate(moved / destination.name)
    openx.validate(moved / 'curve.xodr')


def test_fault_concrete_preserves_injection(tmp_path):
    source = BENCHMARK / 'faults/F02.xosc'
    for level in ('d', 'e'):
        destination = tmp_path / f'F02{level}.xosc'
        openx.concrete(source, destination, openx.anchors(source)[level])
        s = openx.load_scenario(destination)
        assert s.lane_faults == (loader.load_fault('F02', level),)
        fault = s.lane_faults[0]
        assert not fault.active(3.999) and fault.active(4.0)
        assert fault.active(4.05) == (level == 'e')


def test_concrete_preserves_double_mark_barrier_and_oncoming_orientation(tmp_path):
    import math
    from interfaces import LineType, RoadEdgeType
    from sim.world.road import Segment

    source = tmp_path / 'road-edge.xosc'
    root = openx.parse(BENCHMARK / 'scenarios' / 'S3.xosc')
    root.find(".//ParameterDeclaration[@name='road_file']").set('value', 'road-edge.xodr')
    root.find(".//ParameterDeclaration[@name='truck_t_m']").set('value', '3.5')
    root.find(".//Private[@entityRef='Truck']//Orientation").set('h', str(math.pi))
    openx.write(root, source)

    road = openx.road_xml((Segment('straight', 1200.0),), 3.5)
    right = road.find('.//right')
    right.remove(right.find("lane[@id='-3']"))
    right.find("lane[@id='-1']/roadMark").set('type', 'solid broken')
    ego = right.find("lane[@id='-2']")
    ego.remove(ego.find('roadMark'))
    objects = openx.node(road.find('road'), 'objects')
    barrier = openx.node(objects, 'object', id='1', type='barrier', s=0, t=-1.85, zOffset=0)
    openx.node(barrier, 'repeat', s=0, length=1200, distance=0, tStart=-1.85, tEnd=-1.85,
               widthStart=0.2, widthEnd=0.2, heightStart=0.8, heightEnd=0.8, zOffsetStart=0, zOffsetEnd=0)
    openx.write(road, source.with_suffix('.xodr'))

    destination = tmp_path / 'generated' / source.name
    overrides = {'lane_width_m': 4.0}
    openx.concrete(source, destination, overrides)
    openx.validate(destination)
    openx.validate(destination.with_suffix('.xodr'))
    scenario = openx.load_scenario(destination)
    assert scenario == openx.load_scenario(source, overrides)
    assert scenario.traffic[0].direction == -1
    mark = scenario.road_layout.markings[1]
    assert mark.type == LineType.DOUBLE and mark.crossable and mark.offset_m == pytest.approx(1.925)
    assert scenario.road_layout.markings[2] is None
    edge = scenario.road_layout.edges[1]
    assert edge.type == RoadEdgeType.BARRIER and edge.offset_m == pytest.approx(-2.0)


def test_unsupported_dynamic_content_and_bad_parameters_rejected(tmp_path):
    source = BENCHMARK / 'scenarios/S1.xosc'
    with pytest.raises(ValueError, match='undeclared'): openx.load_scenario(source, {'typo': 1})
    with pytest.raises(ValueError, match='non-finite'): openx.load_scenario(source, {'speed_mps': float('nan')})
    with pytest.raises(ValueError, match='ODD'): openx.load_scenario(source, {'lane_width_m': 2})
    root = openx.parse(source)
    openx.node(root.find('Storyboard'), 'Story', name='unsupported')
    path = tmp_path / 'unsupported.xosc'
    openx.write(root, path)
    with pytest.raises(ValueError, match='unsupported'): openx.load_scenario(path)


def test_discontinuous_geometry_rejected(tmp_path):
    root = openx.parse(BENCHMARK / 'roads/S1a.xodr')
    root.findall('.//geometry')[1].set('x', '0')
    path = tmp_path / 'road.xodr'
    openx.write(root, path)
    with pytest.raises(ValueError, match='discontinuous'): openx.read_road(path)


def test_pairwise_covers_every_pair():
    space = {'a': generate.Domain(1, bounds=(0, 2)), 'b': generate.Domain(10, bounds=(5, 20)),
             'c': generate.Domain('on', values=('on', 'off')), 'd': generate.Domain(3, bounds=(2, 4))}
    rows = list(generate.pairwise_samples(space))
    for a, b in combinations(space, 2):
        assert set(product(space[a].levels(), space[b].levels())) <= {(r[a], r[b]) for r in rows}


def test_lhs_stratified_and_reproducible():
    space = {'x': generate.Domain(3., bounds=(1., 5.)), 'y': generate.Domain(0., bounds=(-10., 10.))}
    a = generate.latin_hypercube(space, 24, 19)
    assert a == generate.latin_hypercube(space, 24, 19)
    assert a != generate.latin_hypercube(space, 24, 20)
    for key, domain in space.items():
        lo, hi = domain.bounds
        bins = [int((r[key] - lo) / (hi - lo) * 24) for r in a]
        assert sorted(bins) == list(range(24))


def test_suites_have_required_profiles_seeds_anchors_and_methods():
    plans = {name: generate.plan(name) for name in ('smoke', 'regression', 'full')}
    assert plans['full'] == generate.plan('full')
    for name, p in plans.items():
        assert len({c['id'] for c in p['cases']}) == len(p['cases'])
        case_by_id = {c['id']: c for c in p['cases']}
        profiles = {c['parameters']['profile'] for c in p['cases']}
        assert profiles == ({'VP-0'} if name == 'smoke' else {f'VP-{i}' for i in range(6)})
        for c in p['cases']:
            seeds = {r['seed'] for r in p['runs'] if r['case'] == c['id']}
            expected = {1} if name == 'smoke' else {1, 2} if name == 'regression' else set(range(1, 11)) if c['family'] == 'F01' else {1}
            assert seeds == expected
        for folder in ('scenarios', 'faults'):
            for sid in p['definition'][folder]:
                anchors = openx.anchors(BENCHMARK / folder / f'{sid}.xosc')
                assert {c['anchor'] for c in p['cases'] if c['family'] == sid and c['anchor']} == set(anchors)
        assert all(r['case'] in case_by_id for r in p['runs'])
    assert {'anchor', 'boundary', 'pairwise', 'lhs', 'protocol'} == {m for c in plans['full']['cases'] for m in c['methods']}
    for p in plans.values():
        for anchor in ('a', 'e'):
            assert {c['parameters']['acc'] for c in p['cases'] if c['family'] == 'S14' and c['anchor'] == anchor} == {'on', 'ignore_limits'}


def test_manifest_tamper_detected(tmp_path):
    manifest = generate.plan('smoke')
    manifest['cases'] = manifest['cases'][:1]
    manifest['runs'] = manifest['runs'][:1]
    path = generate.materialize(manifest, tmp_path / 'suite')
    suite.verify_manifest(path)
    road = path.parent / manifest['cases'][0]['file'].replace('.xosc', '.xodr')
    road.write_text(road.read_text() + '\n')
    with pytest.raises(ValueError, match='changed'): suite.verify_manifest(path)


def test_lka_and_elk_protocol_sets_are_explicit_and_separate_from_coverage():
    counts = {"S4": 20, "S5": 14, "S6": 10, "S7": 5, "S8": 16}
    cases = generate.plan("regression")["cases"]
    for sid, count in counts.items():
        rows = [c["parameters"] for c in cases if c["family"] == sid and c["methods"] == ["protocol"]
                and c["parameters"]["profile"] == "VP-0"]
        assert len(rows) == count
        assert {r["speed_mps"] for r in rows} == {20.0}
        assert {r["departure_v_lat_mps"] for r in rows if r["protocol"] == "Euro NCAP LSS"
                and not r["indicated"]} == {.2, .3, .4, .5, .6}
        if sid in ("S4", "S5"):
            assert {r["departure_side"] for r in rows} == {"left", "right"}
        if sid == "S5":
            eu = [r for r in rows if r["protocol"] == "EU 2021/646"]
            assert {(r["departure_side"], r["departure_v_lat_mps"]) for r in eu} == set(
                product(("left", "right"), (.2, .5)))
            assert all(r["departure_radius_m"] >= 1200 and not r["passive_hands_on"] for r in eu)
        if sid == "S8":
            intent = [r for r in rows if r["indicated"]]
            assert {r["departure_v_lat_mps"] for r in intent} == {.5, .6, .7}
            assert {r["departure_radius_m"] for r in intent} == {800}


def test_anchors_override_the_default_drift_direction_and_target_speed():
    assert loader.load("S4b", "b").driver.drift_curvature < 0
    assert loader.load("S4b", "c").driver.drift_curvature > 0
    same_speed = loader.load("S8", "b")
    assert same_speed.speed_mps == same_speed.traffic[0].speed == 20.0


@pytest.mark.parametrize("sid, variant", [("S4", "d"), ("S6", "d"), ("S7", "a"), ("S8", "late")])
def test_intervention_round_trip_includes_driver_and_traffic(tmp_path, sid, variant):
    source = BENCHMARK / "scenarios" / f"{sid}.xosc"
    out = tmp_path / source.name
    anchor = openx.anchors(source)[variant]
    openx.concrete(source, out, anchor)
    openx.validate(out)
    openx.validate(out.with_suffix(".xodr"))
    expected = loader.load(sid, variant)
    assert openx.load_scenario(out) == expected
    assert expected.hwa_request_s is None and expected.driver is not None
    if variant == "late":
        assert expected.adas_mode == "scripted" and len(expected.request_events) == 1


def test_provenance_includes_xml_ranges_suites_and_schemas():
    files = provenance.input_files()
    for p in ('scenarios/S1.xosc', 'scenarios/S1.ranges.xosc', 'scenarios/S1.anchors.xosc',
              'roads/S1a.xodr', 'suites/smoke.json', 'schema/openscenario-1.3.1/OpenSCENARIO.xsd'):
        assert 'benchmark/' + p in files


def test_all_planned_parameter_combinations_are_loadable():
    for name in ('smoke', 'regression', 'full'):
        for case in generate.plan(name)['cases']:
            openx.load_scenario(openx.ROOT / case['source'], case['parameters'])


def test_lane_faults_run_on_every_host_anchor():
    for name in ('smoke', 'regression', 'full'):
        p = generate.plan(name)
        hosts = {f'{sid}{v}' for sid, v in p['definition']['fault_hosts']}
        assert hosts == {'S1a', 'S1c'}
        for fid in p['definition']['faults']:
            anchors = set(openx.anchors(BENCHMARK / 'faults' / f'{fid}.xosc'))
            for host in hosts:
                cases = [c for c in p['cases'] if c['family'] == fid and c['host'] == host]
                assert {c['anchor'] for c in cases if c['anchor']} == anchors
                assert all(c['parameters']['fault_start_s'] < c['parameters']['duration_s'] for c in cases)
                assert all(f'-{host}-' in c['id'] for c in cases)


def test_suite_runs_keep_order_and_isolate_errors(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parent))  # child processes inherit sys.path
    import _fake_runs
    tasks = [({'id': i}, Path('.'), {'case': i, 'seed': 1}, None) for i in ('a', 'bad', 'crash', 'hang', 'c')]
    out = list(suite.results(tasks, 2, fn=_fake_runs.fake, timeout_s=5))
    assert [r['case'] for r in out] == ['a', 'bad', 'crash', 'hang', 'c']
    assert 'boom' in out[1]['error'] and 'error' not in out[0]
    assert 'tiến trình dừng' in out[2]['execution'] and 'không trả về' in out[3]['execution']
    assert 'execution' not in out[4]
