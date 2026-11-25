"""B0 chạy trước. C1/C2 trượt sẽ dừng suite trừ khi bật chế độ chạy tiếp để lập báo cáo."""

import argparse
from dataclasses import replace
import json
from pathlib import Path
from shlex import join
import sys

from eval import aspects, conclusion, conformance, isolation, labels, loader, matrix, openx, planner_choice, provenance, report, run_artifacts

RUN_TIMEOUT_S = 1800


def verify_manifest(path):
    path = Path(path)
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('format') != 1:
        raise ValueError('unsupported concrete manifest format')
    cases = {}
    for case in manifest['cases']:
        if case['id'] in cases:
            raise ValueError('duplicate case id')
        if case.get('planner_only') not in (None, *planner_choice.FAMILIES):
            raise ValueError('invalid standalone planner family')
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


SCOPE = matrix.SCOPE


def rerun_command(path, seed, planner) -> str:
    command = ['python3', '-m', 'eval.runner', str(path), '--seed', str(seed)]
    if planner is not None:
        command += ['--planner', str(planner.location)]
        if planner.only:
            command += ['--planner-only', planner.only]
    return join(command)


def execute_case(case, directory, seed, planner, mcap_dir=None, mcap='failed'):
    from eval import case as resolved, checksum, metrics
    from sim.harness import Harness
    from sim.logging import run_log
    path = directory / case['file']
    scenario = replace(loader.load_file(path), name=case['id'])
    if case.get('planner_only'):
        planner = replace(planner, only=case['planner_only'])
    log = Harness(scenario, planner, seed).run()
    identity = {'case_hash': resolved.case_hash(scenario), 'behavior_checksum': checksum.behavior_checksum(log)}
    result = metrics.evaluate(log)
    from eval import differential
    result.criteria.extend(differential.criteria(scenario, log, planner, seed))
    family = case['family']
    scope = matrix.case_scope(case) | labels.scope_extra(labels.of(scenario))
    if log.planner_only:
        metrics.score_standalone(result, scope)
    failed = dict.fromkeys(c.id for c in result.criteria if c.applicable and not c.passed)
    case_labels = labels.of(scenario)
    record = {'case': case['id'], 'seed': seed, 'profile': scenario.profile, 'labels': case_labels,
              'aspects': aspects.members(family, case['anchor'], case.get('methods', []), case_labels),
              'failed': [i['text'] for i in result.issues if i['kind'] != metrics.ISSUE_NOT_JUDGED]
                        + [key for key in failed if key in scope],
              'failed_out_of_scope': [key for key in failed if key not in scope],
              'scope': sorted(scope), 'rerun': rerun_command(path, seed, planner),
              **identity, 'result': result.to_dict(), 'mcap': None}
    if mcap_dir is not None and mcap != 'none' and (mcap == 'all' or record['failed']):
        record['mcap'] = str(run_log.write(log, Path(mcap_dir) / f"{case['id']}_seed{seed}.mcap",
                                           {'rerun': record['rerun']}))
        from eval import presentation
        record['figure'] = str(presentation.run_figure(
            log, result, Path(mcap_dir).parent / 'figures' / 'runs' / f"{case['id']}_seed{seed}.png"))
    return record


def run_safely(case, directory, run, planner, mcap_dir=None, mcap='failed'):
    try:
        return execute_case(case, directory, run['seed'], planner, mcap_dir, mcap)
    except Exception as exc:
        return {**run, 'error': f'{type(exc).__name__}: {exc}'}


def from_isolated(run, status, value, timeout_s=RUN_TIMEOUT_S):
    """Crash và timeout của một run được ghi thành lỗi thực thi (SQTS 8.4)."""
    if status == 'ok':
        return value
    if status == 'crash':
        return {**run, 'execution': f'Lỗi thực thi: tiến trình dừng ({value}) trong lúc chạy planner'}
    if status == 'timeout':
        return {**run, 'execution': f'Lỗi thực thi: lần chạy không trả về sau {timeout_s} s'}
    return {**run, 'error': str(value).splitlines()[0]}


def results(tasks, jobs, fn=run_safely, timeout_s=RUN_TIMEOUT_S):
    for task, (status, value) in zip(tasks, isolation.map_isolated(fn, tasks, jobs, timeout_s)):
        yield from_isolated(task[2], status, value, timeout_s)


def case_aspects(case, directory):
    scenario = loader.load_file(directory / case['file'])
    return aspects.members(case['family'], case['anchor'], case.get('methods', []), labels.of(scenario))


def aspect_table(records, b0):
    lines = ['', '## Bộ theo khía cạnh', '', '| Bộ | Khía cạnh | Lần chạy | Kết luận | BLOCKER | MAJOR | MINOR |',
             '|---|---|---|---|---|---|---|']
    if b0 is not None:
        verdict = conclusion.BLOCKED if b0['blocked'] else 'Đạt C1, C2' + ('; Tích hợp được' if b0['integrable'] else '')
        lines.append(f'| B0 | Conformance | — | {verdict} | — | — | — |')
    for aspect, rule in aspects.definitions().items():
        subset = [r for r in records if aspect in r.get('aspects', [])]
        if not subset:
            lines.append(f"| {aspect} | {rule['title']} | 0 | không có ca | — | — | — |")
            continue
        c = conclusion.conclude(subset)
        lines.append(f"| {aspect} | {rule['title']} | {len(subset)} | {c['verdict']} | {c['counts']['BLOCKER']} | "
                     f"{c['counts']['MAJOR']} | {c['counts']['MINOR']} |")
    return lines


def write_report(out, records, b0, planner_text, extra=()):
    c = conclusion.conclude(records, b0)
    extra = aspect_table(records, b0) + list(extra)
    (out / 'conclusion.json').write_text(json.dumps(c, indent=1, ensure_ascii=False, default=report.jsonable) + '\n',
                                         encoding='utf-8')
    (out / 'report.md').write_text('\n'.join(conclusion.markdown(c, planner_text) + list(extra)) + '\n',
                                   encoding='utf-8')
    return c


def main():
    parser = argparse.ArgumentParser(
        description="Run a generated ASAM suite, one SIL log per worker at a time (8 GB machines).",
    )
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--max-runs', type=int, help='Exploratory prefix only; reported as partial, never official')
    parser.add_argument('--record', action='store_true')
    parser.add_argument('--artifact-dir', type=Path, help='Shared directory for official suite artifacts')
    parser.add_argument('--jobs', type=int, default=1, help='Worker processes (each holds one SIL log)')
    parser.add_argument('--mcap', choices=('failed', 'all', 'none'), default='failed',
                        help='MCAP log for runs with an in-scope failure (default), for every run, or none')
    parser.add_argument('--continue-after-b0', action='store_true',
                        help='Run every case even when B0 C1 or C2 fails; the conclusion stays as 8.4 says')
    parser.add_argument('--skip-b0', action='store_true', help='Exploratory only: do not run B0 first')
    parser.add_argument('--aspect', action='append', help='Run only the cases of aspect suites B1..B8 (repeatable)')
    planner_choice.add_argument(parser)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be at least 1')
    if args.record and args.skip_b0:
        parser.error('--record needs B0')
    if args.max_runs is not None and (args.max_runs <= 0 or args.record):
        parser.error('--max-runs must be positive and cannot be combined with --record')
    if args.record and not args.artifact_dir:
        parser.error('--record requires --artifact-dir')
    source, cases = verify_manifest(args.manifest)
    planner = planner_choice.from_args(args)
    manifest = provenance.make('suite', source['suite'], {'jobs': args.jobs, 'start_method': isolation.START_METHOD})
    manifest['libraries'] = provenance.library_infos(planner, external=args.planner is not None)
    manifest['generation'] = {'manifest': str(args.manifest.resolve()), 'sha256': provenance.sha256(args.manifest),
                              'inputs': source['inputs'], 'definition': source['definition']}
    if args.record:
        provenance.preflight(manifest)
        if source['inputs'] != manifest['inputs']:
            raise SystemExit('Benchmark inputs changed since generation; regenerate before an official run')
        try:
            run_artifacts.prepare_store(args.artifact_dir)
        except (OSError, ValueError) as exc:
            parser.error(f'cannot use --artifact-dir: {exc}')
    runs = source['runs']
    if args.aspect:
        unknown = set(args.aspect) - set(aspects.definitions())
        if unknown:
            parser.error(f'unknown aspect: {sorted(unknown)}')
        chosen = {cid for cid, case in cases.items() if set(args.aspect) & set(case_aspects(case, args.manifest.parent))}
        runs = [r for r in runs if r['case'] in chosen]
        manifest['aspects'] = args.aspect
    selected = len(runs)  # Suite theo nhóm aspect hoàn tất khi chạy hết tập con đã chọn.
    runs = runs[:args.max_runs] if args.max_runs else runs
    out = args.out or openx.ROOT / 'build' / 'suites' / source['suite']
    out.mkdir(parents=True, exist_ok=False)
    planner_text = ' / '.join(f"{lib['pp_version']} ({lib['sha256'][:12]})" for lib in manifest['libraries'])
    b0 = None
    if not args.skip_b0:
        b0 = conformance.run(planner)
        (out / 'conformance.json').write_text(json.dumps(b0, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
        if b0['blocked'] and args.continue_after_b0:
            print('B0: không đạt C1 hoặc C2; vẫn chạy mọi ca (--continue-after-b0)', flush=True)
        elif b0['blocked']:
            c = write_report(out, [], b0, planner_text)
            provenance.write({**manifest, 'summary': {'b0_blocked': True, 'verdict': c['verdict']}}, out)
            print('\n'.join(conclusion.markdown(c, planner_text)))
            raise SystemExit(1)
    counts = {'planned': selected, 'executed': 0, 'failed': 0, 'failed_out_of_scope': 0, 'errors': 0,
              'execution_faults': 0, 'not_judged': 0}
    result_path = out / 'results.jsonl'
    records = []
    with result_path.open('w', encoding='utf-8') as stream:
        tasks = [(cases[run['case']], args.manifest.parent, run, planner, out / 'mcap', args.mcap) for run in runs]
        for run, result in zip(runs, results(tasks, args.jobs)):
            if 'execution' in result:
                counts['execution_faults'] += 1
                counts['failed'] += 1
            elif 'error' in result:
                counts['errors'] += 1
            else:
                counts['failed'] += bool(result['failed'])
                counts['failed_out_of_scope'] += bool(result['failed_out_of_scope'])
                counts['not_judged'] += any(issue['kind'] == 'not_judged' for issue in result['result']['issues'])
            stream.write(json.dumps(result, ensure_ascii=False, default=report.jsonable) + '\n')
            stream.flush()
            records.append({k: v for k, v in result.items()})
            counts['executed'] += 1
            print(f'{counts["executed"]}/{len(runs)} {run["case"]} seed={run["seed"]}', flush=True)
    counts['partial'] = counts['executed'] != counts['planned']
    if args.aspect:
        counts['aspects'] = args.aspect
    from eval import presentation
    c = write_report(out, records, b0, planner_text,
                     ['', '## Số lần chạy', '', '```json', json.dumps(counts, indent=1), '```']
                     + presentation.suite_sections(records, cases, out))
    counts['verdict'] = c['verdict']
    summary = out / 'summary.json'
    summary.write_text(json.dumps(counts, indent=2, ensure_ascii=False) + '\n')
    manifest = {**manifest, 'summary': counts, 'finished': provenance.now()}
    provenance.write(manifest, out)
    # Lưu định nghĩa sinh ca đã dùng để có thể đối chiếu với kết quả chi tiết.
    generation_path = out / 'generation.json'
    generation_path.write_text(json.dumps(source, indent=2, ensure_ascii=False) + '\n')
    if args.record:
        try:
            artifact = run_artifacts.pack(args.artifact_dir, manifest, out, args.manifest)
            official = {**manifest, 'artifact': artifact}
            provenance.record(official, {'summary.json': summary, 'report.md': out / 'report.md',
                                         'conclusion.json': out / 'conclusion.json'},
                              f"{c['verdict']}; {json.dumps({k: counts[k] for k in ('executed', 'failed', 'errors')})}")
            provenance.write(official, out)
        except (OSError, ValueError) as exc:
            print(f'Cannot record official suite: {exc}', file=sys.stderr)
            raise SystemExit(2) from exc
    print('\n'.join(conclusion.markdown(c, planner_text)[:6]))
    print(json.dumps(counts, ensure_ascii=False))
    if counts['errors'] or counts['failed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
