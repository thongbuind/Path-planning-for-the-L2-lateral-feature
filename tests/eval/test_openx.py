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
    with pytest.raises(KeyError): loader.load('S1b', 'd')
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
    assert {'anchor', 'boundary', 'pairwise', 'lhs'} == {m for c in plans['full']['cases'] for m in c['methods']}
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
    def fake(case, directory, seed):
        if case['id'] == 'bad':
            raise RuntimeError('boom')
        return {'case': case['id'], 'seed': seed, 'failed': [], 'failed_out_of_scope': []}
    monkeypatch.setattr(suite, 'execute_case', fake)
    tasks = [({'id': i}, Path('.'), {'case': i, 'seed': 1}) for i in ('a', 'bad', 'c')]
    out = list(suite.results(tasks, 1))
    assert [r['case'] for r in out] == ['a', 'bad', 'c']
    assert 'boom' in out[1]['error'] and 'error' not in out[0]
