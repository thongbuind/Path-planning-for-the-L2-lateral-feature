import ctypes
import time


def fake(case, directory, run, planner, *rest):
    if case['id'] == 'crash':
        ctypes.string_at(0)  # Tạo lỗi segmentation fault như khi thư viện planner bị crash.
    if case['id'] == 'hang':
        time.sleep(60)
    if case['id'] == 'bad':
        raise RuntimeError('boom')
    return {'case': case['id'], 'seed': run['seed'], 'failed': [], 'failed_out_of_scope': []}
