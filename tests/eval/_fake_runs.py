"""Stand-ins for eval.suite.run_safely, importable by the child processes of eval.isolation."""

import ctypes
import time


def fake(case, directory, run, planner, *rest):
    if case['id'] == 'crash':
        ctypes.string_at(0)  # segmentation fault, as a crashing planner library would cause
    if case['id'] == 'hang':
        time.sleep(60)
    if case['id'] == 'bad':
        raise RuntimeError('boom')
    return {'case': case['id'], 'seed': run['seed'], 'failed': [], 'failed_out_of_scope': []}
