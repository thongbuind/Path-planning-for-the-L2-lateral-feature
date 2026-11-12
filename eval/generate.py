"""Generate portable concrete ASAM scenarios and smoke/regression/full manifests.

    python3 -m eval.generate smoke
    python3 -m eval.generate full --plan-only
"""
import argparse
from dataclasses import dataclass
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

import numpy as np
import yaml

from eval import labels, openx, provenance

BENCHMARK = openx.ROOT / 'benchmark'
# Road and run of a fault's host anchor replace those of the fault file (lane faults are
# injected on several host roads, Software Qualification Test Specification 6.2).
_SCOPE = yaml.safe_load((BENCHMARK / 'suites' / 'scope.yaml').read_text(encoding='utf-8'))
ACC_BOTH = set(_SCOPE['acc_both_modes'])
OWN_PROFILE = set(_SCOPE.get('own_profile', []))
HOST_KEYS = ('road_file', 'duration_s', 'speed_mps', 'lane_width_m', 'start_s_m', 'hwa_request_s')


@dataclass(frozen=True)
class Domain:
    nominal: object
    values: tuple = ()
    bounds: tuple | None = None

    def levels(self):
        if self.bounds:
            return tuple(dict.fromkeys((self.bounds[0], self.nominal, self.bounds[1])))
        return tuple(dict.fromkeys((*self.values, self.nominal)))

    def sample(self, fraction):
        if self.bounds:
            lo, hi = self.bounds
            return lo + (hi - lo) * float(fraction)
        return self.values[min(int(fraction * len(self.values)), len(self.values) - 1)]


def domains(path):
    nominal = openx.declarations(openx.parse(path))
    root = openx.parse(Path(path).with_suffix('.ranges.xosc'))
    if root.find('./ParameterValueDistribution/ScenarioFile').get('filepath') != Path(path).name:
        raise ValueError('range distribution references the wrong scenario')
    result = {}
    for single in root.findall('.//DeterministicSingleParameterDistribution'):
        name = single.attrib['parameterName']
        if name not in nominal or name in result:
            raise ValueError(f'unknown or duplicate distribution parameter {name}')
        default = nominal[name]
        r = single.find('DistributionRange/Range')
        if r is not None:
            lo, hi = openx.number(r.attrib['lowerLimit']), openx.number(r.attrib['upperLimit'])
            step = openx.number(single.find('DistributionRange').attrib['stepWidth'])
            if not lo <= default <= hi or step <= 0:
                raise ValueError(f'invalid range for {name}')
            result[name] = Domain(default, bounds=(lo, hi))
        else:
            values = tuple(e.attrib['value'] for e in single.findall('DistributionSet/Element'))
            if isinstance(default, float):
                values = tuple(openx.number(v) for v in values)
            if not values or default not in values:
                raise ValueError(f'empty distribution or missing nominal for {name}')
            result[name] = Domain(default, values=values)
    return result


def boundary_samples(space):
    base = {k: d.nominal for k, d in space.items()}
    for key, domain in space.items():
        values = domain.bounds if domain.bounds else domain.values
        for value in values:
            yield {**base, key: value}


def pairwise_samples(space):
    """All pairs of min/nominal/max (all categorical levels), others nominal.

    No exponential Cartesian product; an explicit covering array, not a minimal one.
    """
    base = {k: d.nominal for k, d in space.items()}
    if len(space) < 2:
        yield from boundary_samples(space)
    for a, b in combinations(space, 2):
        for av, bv in product(space[a].levels(), space[b].levels()):
            yield {**base, a: av, b: bv}


def latin_hypercube(space, count, seed):
    if count <= 0:
        raise ValueError('Latin hypercube count must be positive')
    rng = np.random.default_rng(seed)
    columns = {key: (rng.permutation(count) + rng.random(count)) / count for key in space}
    return [{k: d.sample(columns[k][i]) for k, d in space.items()} for i in range(count)]


def load_suite(name):
    path = BENCHMARK / 'suites' / f'{name}.json'
    suite = json.loads(path.read_text())
    if suite['id'] != name:
        raise ValueError('suite id mismatch')
    return suite


def fault_hosts(suite):
    """[(name, parameters)] of the host anchors lane faults run on; default S1a."""
    hosts = []
    for sid, variant in suite.get('fault_hosts', [['S1', 'a']]):
        path = BENCHMARK / 'scenarios' / f'{sid}.xosc'
        params = openx.resolve(openx.parse(path), openx.anchors(path)[variant])[1]
        hosts.append((f'{sid}{variant}', {k: params[k] for k in HOST_KEYS}
                      | ({'host_expected_outcome': params['expected_outcome']} if 'expected_outcome' in params else {})))
    return hosts


def _identity(params):
    return json.dumps(params, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def plan(name):
    suite = load_suite(name)
    cases, runs = [], []
    for folder in ('scenarios', 'faults'):
        for sid in suite[folder]:
            path = BENCHMARK / folder / f'{sid}.xosc'
            raw = openx.parse(path)
            nominal = openx.declarations(raw)
            space = {k: d for k, d in domains(path).items() if k != 'profile'}
            selections = [('anchor', dict(openx.resolve(raw, values)[1]))
                          for values in openx.anchors(path).values()]
            for method in suite['methods']:
                if method == 'anchor':
                    continue
                if method == 'protocol':
                    if path.with_suffix('.protocol.xosc').is_file():
                        selections.extend((method, openx.resolve(raw, values)[1])
                                          for values in openx.parameter_sets(path, '.protocol.xosc').values())
                    continue
                samples = (boundary_samples(space) if method == 'boundary' else pairwise_samples(space)
                           if method == 'pairwise' else latin_hypercube(space, suite['lhs_count'], suite['sampling_seed']))
                for sample in samples:
                    params = {**nominal, **sample}
                    # Keep the nominal travelled distance when sampling speed; anchors remain exact.
                    if 'speed_mps' in sample:
                        params['duration_s'] = nominal['duration_s'] * nominal['speed_mps'] / params['speed_mps']
                    selections.append((method, params))
            if folder == 'faults':
                def on_host(params, host_params):
                    # Host geometry; expected outcome the stricter of fault and host (5.3).
                    merged = {**params, **{k: v for k, v in host_params.items() if k != 'host_expected_outcome'}}
                    if 'expected_outcome' in merged:
                        merged['expected_outcome'] = labels.stricter(merged['expected_outcome'],
                                                                     host_params.get('host_expected_outcome'))
                    return merged
                selections = [(method, on_host(params, host_params), host)
                              for host, host_params in fault_hosts(suite) for method, params in selections]
                for _, params, host in selections:
                    if not params['fault_start_s'] < params['duration_s']:
                        raise ValueError(f'{sid}: fault starts after the end of host {host}')
            else:
                selections = [(method, params, None) for method, params in selections]
            seen = {}
            for method, params, host in selections:
                # Both sides of the longitudinal constraint exchange (benchmark/suites/scope.yaml).
                acc_modes = ('on', 'ignore_limits') if sid in ACC_BOTH else (params['acc'],)
                profiles = [params['profile']] if sid in OWN_PROFILE else suite['profiles']
                for profile, acc in product(profiles, acc_modes):
                    concrete_params = {**params, 'profile': profile, 'acc': acc}
                    # IDs for anchors retain a,b,...; samples use a content hash in filenames.
                    key = _identity(concrete_params)
                    if key in seen:
                        case = seen[key]
                        if method not in case['methods']:
                            case['methods'].append(method)
                        continue
                    digest = hashlib.sha256(key.encode()).hexdigest()[:12]
                    label = f'{params["variant"]}-{host}' if host else params['variant']
                    case_id = f'{sid}-{label}-{profile}-{digest}'
                    case = {'id': case_id, 'family': sid, 'host': host,
                            'anchor': params['variant'] if method == 'anchor' else None,
                            'methods': [method], 'source': str(path.relative_to(openx.ROOT)),
                            'parameters': concrete_params, 'file': f'cases/{case_id}.xosc'}
                    seen[key] = case
                    cases.append(case)
                    noisy = params.get('fault_kind') == 'noise' and (params.get('fault_sigma_c0', 0) > 0 or params.get('fault_sigma_c1', 0) > 0)
                    seeds = suite['noise_seeds'] if noisy else suite['seeds']
                    for seed in seeds:
                        runs.append({'case': case_id, 'seed': seed})
    _injected_cases(suite, cases, runs)
    return {'format': 1, 'suite': name, 'definition': suite, 'inputs': provenance.input_files(),
            'cases': cases, 'runs': runs}


def anchor_params(folder, sid, variant):
    path = BENCHMARK / folder / f'{sid}.xosc'
    return path, openx.resolve(openx.parse(path), openx.anchors(path)[variant])[1]


def load_combination(cid):
    """Combined-fault case of Software Qualification Test Specification 6.2."""
    data = yaml.safe_load((BENCHMARK / 'combinations' / f'{cid}.yaml').read_text(encoding='utf-8'))
    if data.get('id') != cid or set(data) - {'id', 'title', 'hosts', 'faults', 'sim'}:
        raise ValueError(f'{cid}: invalid combination definition')
    if len(data['faults']) < 2:
        raise ValueError(f'{cid}: a combination needs at least two faults (6.2)')
    return data


def _injected_cases(suite, cases, runs):
    """Fault definitions added to whole host scenarios: at a planner-output event of LKA or ELK
    hosts (`event_hosts`, `event_faults`, `event_offsets_s`; section 6), and the combined faults
    of 6.2 (`combinations`). Anchors only; profiles and seeds as the rest of the suite."""
    jobs = []
    for host_sid, host_variant, event in suite.get('event_hosts', []):
        for fsid in suite.get('event_faults', []):
            for fvariant in openx.anchors(BENCHMARK / 'faults' / f'{fsid}.xosc'):
                for offset in suite.get('event_offsets_s', [0.0]):
                    jobs.append((fsid, fvariant, (host_sid, host_variant), [(fsid, fvariant)],
                                 event, float(offset), {}, f'{host_sid}{host_variant}@{event}+{float(offset):g}'))
    for cid in suite.get('combinations', []):
        combo = load_combination(cid)
        for host_sid, host_variant in combo['hosts']:
            jobs.append((cid, None, (host_sid, host_variant), [tuple(f) for f in combo['faults']],
                         None, 0.0, combo.get('sim', {}), f'{host_sid}{host_variant}'))
    for family, anchor, (host_sid, host_variant), faults, event, offset, sim, host in jobs:
        host_path, host_params = anchor_params('scenarios', host_sid, host_variant)
        inject = {'faults': [{'source': str((BENCHMARK / 'faults' / f'{f}.xosc').relative_to(openx.ROOT)),
                              'level': v, 'name': f'{f}{v}' + (f'@{event}+{offset:g}' if event else '')}
                             for f, v in faults],
                  'trigger': event, 'offset_s': offset, 'sim': sim}
        noisy = False
        for f, v in faults:
            fparams = anchor_params('faults', f, v)[1]
            noisy |= fparams.get('fault_kind') == 'noise'
        for profile in suite['profiles']:
            params = {**host_params, 'profile': profile}
            key = _identity({'host': params, 'inject': inject})
            digest = hashlib.sha256(key.encode()).hexdigest()[:12]
            label = f'{anchor}-{host}' if anchor else host
            case_id = f'{family}-{label}-{profile}-{digest}'.replace('@', '_at_').replace('+', 'p')
            scope_keys = [[host_sid, host_variant]] + [[host_sid, host_variant, f, v] for f, v in faults]
            cases.append({'id': case_id, 'family': family, 'host': host, 'anchor': anchor, 'methods': ['anchor'],
                          'source': str(host_path.relative_to(openx.ROOT)), 'parameters': params,
                          'inject': inject, 'scope_keys': scope_keys, 'file': f'cases/{case_id}.xosc'})
            for seed in suite['noise_seeds'] if noisy else suite['seeds']:
                runs.append({'case': case_id, 'seed': seed})


def materialize(manifest, out):
    out = Path(out)
    # Refuse accidental reuse: old files must not be confused with the new manifest.
    out.mkdir(parents=True, exist_ok=False)
    for case in manifest['cases']:
        destination = out / case['file']
        openx.concrete(openx.ROOT / case['source'], destination, case['parameters'])
        if 'inject' in case:
            inject = case['inject']
            faults = [(openx.ROOT / f['source'], openx.anchors(openx.ROOT / f['source'])[f['level']], f['name'])
                      for f in inject['faults']]
            openx.inject(destination, faults, inject['trigger'], inject['offset_s'], inject['sim'])
        openx.validate(destination)
        openx.validate(destination.with_suffix('.xodr'))
        # A fresh load catches unresolved references and checks the simulator subset.
        openx.load_scenario(destination)
        case['sha256'] = provenance.sha256(destination)
        case['road_sha256'] = provenance.sha256(destination.with_suffix('.xodr'))
    path = out / 'manifest.json'
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('suite', choices=('smoke', 'regression', 'full'))
    parser.add_argument('--out', type=Path)
    parser.add_argument('--plan-only', action='store_true', help='Count cases and runs without generating files or running SIL')
    args = parser.parse_args()
    manifest = plan(args.suite)
    print(f'{args.suite}: {len(manifest["cases"])} concrete cases, {len(manifest["runs"])} runs')
    if not args.plan_only:
        out = args.out or openx.ROOT / 'build' / 'concrete' / args.suite
        print(materialize(manifest, out))


if __name__ == '__main__':
    main()
