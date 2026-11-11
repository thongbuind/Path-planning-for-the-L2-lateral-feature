"""Run a generated ASAM suite, one SIL log per worker at a time (8 GB machines).

    python3 -m eval.suite build/concrete/smoke/manifest.json [--jobs 2]

Results are written in manifest order, one line per run, whatever the number of workers.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
from pathlib import Path

from eval import loader, matrix, openx, provenance


def verify_manifest(path):
    path = Path(path)
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('format') != 1:
        raise ValueError('unsupported concrete manifest format')
    cases = {}
    for case in manifest['cases']:
        if case['id'] in cases:
            raise ValueError('duplicate case id')
        source = (path.parent / case['file']).resolve()
        if not source.is_relative_to(path.parent.resolve()):
            raise ValueError('case path outside suite directory')
        for file, key in ((source, 'sha256'), (source.with_suffix('.xodr'), 'road_sha256')):
            if provenance.sha256(file) != case[key]:
                raise ValueError(f'concrete input changed: {file}')
        root, _ = openx.resolve(openx.parse(source))
        road = (source.parent / root.find('./RoadNetwork/LogicFile').attrib['filepath']).resolve()
        if road != source.with_suffix('.xodr'):
            raise ValueError('scenario road does not match hashed road')
        cases[case['id']] = case
    run_keys = set()
    for run in manifest['runs']:
        key = (run['case'], run['seed'])
        if run['case'] not in cases or type(run['seed']) is not int or run['seed'] < 0 or key in run_keys:
            raise ValueError('invalid or duplicate run')
        run_keys.add(key)
    return manifest, cases


def execute_case(case, directory, seed):
    from adapters.sil.sil_planner import SilPlanner
    from eval import metrics
    from sim.harness import Harness
    scenario = replace(loader.load_file(directory / case['file']), name=case['id'])
    result = metrics.evaluate(Harness(scenario, SilPlanner, seed).run())
    family = case['family']
    anchor = case['anchor'] or 'a'
    spec = ['S1', 'a', family, anchor] if family.startswith('F') else [family, anchor]
    scope = matrix.scope({'scope_from': 'P1', 'extra_scope': {'S14': ['PP-SWR-009', 'PP-SWR-150', 'PP-SWR-051']}}, spec)
    return {'case': case['id'], 'seed': seed,
            'failed': [c.id for c in result.criteria if c.applicable and not c.passed and c.id in scope],
            'failed_out_of_scope': [c.id for c in result.criteria if c.applicable and not c.passed and c.id not in scope],
            'result': result.to_dict()}


def run_safely(task):
    """One run in a worker; an execution error is reported, never lost or fatal to the suite."""
    case, directory, run = task
    try:
        return execute_case(case, directory, run['seed'])
    except Exception as exc:
        return {**run, 'error': f'{type(exc).__name__}: {exc}'}


def results(tasks, jobs):
    if jobs == 1:
        yield from map(run_safely, tasks)
        return
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        # map keeps manifest order; chunksize 1 keeps one log per worker in memory.
        yield from pool.map(run_safely, tasks, chunksize=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--max-runs', type=int, help='Exploratory prefix only; reported as partial, never official')
    parser.add_argument('--record', action='store_true')
    parser.add_argument('--jobs', type=int, default=1, help='Worker processes (each holds one SIL log)')
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be at least 1')
    if args.max_runs is not None and (args.max_runs <= 0 or args.record):
        parser.error('--max-runs must be positive and cannot be combined with --record')
    source, cases = verify_manifest(args.manifest)
    from adapters.sil.sil_planner import library_path
    manifest = provenance.make('suite', source['suite'], {'jobs': args.jobs})
    manifest['libraries'] = [provenance.library_info(library_path())]
    manifest['generation'] = {'manifest': str(args.manifest.resolve()), 'sha256': provenance.sha256(args.manifest),
                              'inputs': source['inputs'], 'definition': source['definition']}
    if args.record:
        provenance.preflight(manifest)
        if source['inputs'] != manifest['inputs']:
            raise SystemExit('Benchmark inputs changed since generation; regenerate before an official run')
    runs = source['runs'][:args.max_runs] if args.max_runs else source['runs']
    out = args.out or openx.ROOT / 'build' / 'suites' / source['suite']
    out.mkdir(parents=True, exist_ok=False)
    counts = {'planned': len(source['runs']), 'executed': 0, 'failed': 0, 'failed_out_of_scope': 0, 'errors': 0}
    result_path = out / 'results.jsonl'
    with result_path.open('w', encoding='utf-8') as stream:
        tasks = [(cases[run['case']], args.manifest.parent, run) for run in runs]
        for run, result in zip(runs, results(tasks, args.jobs)):
            if 'error' in result:
                counts['errors'] += 1
            else:
                counts['failed'] += bool(result['failed'])
                counts['failed_out_of_scope'] += bool(result['failed_out_of_scope'])
            stream.write(json.dumps(result, ensure_ascii=False) + '\n')
            stream.flush()
            counts['executed'] += 1
            print(f'{counts["executed"]}/{len(runs)} {run["case"]} seed={run["seed"]}', flush=True)
    counts['partial'] = counts['executed'] != counts['planned']
    summary = out / 'summary.json'
    summary.write_text(json.dumps(counts, indent=2) + '\n')
    provenance.write({**manifest, 'summary': counts}, out)
    # Freeze the exact generation definition with the results.
    generation_path = out / 'generation.json'
    generation_path.write_text(json.dumps(source, indent=2, ensure_ascii=False) + '\n')
    if args.record:
        provenance.record(manifest, {'results.jsonl': result_path, 'summary.json': summary,
                                     'generation.json': generation_path}, json.dumps(counts))
    print(json.dumps(counts))
    if counts['errors'] or counts['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
