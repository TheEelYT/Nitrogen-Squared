"""Host build scheduling and stage messages; never changes game compatibility."""
from __future__ import annotations
import os
import json
from pathlib import Path
import time


def available_threads():
    process_count = getattr(os, 'process_cpu_count', lambda: None)()
    if process_count:
        return max(1, process_count)
    try:
        return max(1, len(os.sched_getaffinity(0)))
    except (AttributeError, OSError):
        return max(1, os.cpu_count() or 1)


def build_jobs(environment=None, *, target=None):
    env = os.environ if environment is None else environment
    count = available_threads()
    target = target or env.get('NITROGEN_BUILD_TARGET', 'desktop')
    limit = min(2, count) if target == 'vita' else max(1, count * 4 // 5)
    # Honour a smaller explicit budget, without exceeding the target's cap.
    try:
        requested = int(env.get('CMAKE_BUILD_PARALLEL_LEVEL', limit))
    except (ValueError, TypeError):
        requested = limit
    return min(limit, requested) if requested > 0 else limit


def report_stage(title, detail):
    print(f'Stage: {title} | {detail}', flush=True)


def report_workers():
    jobs = build_jobs()
    print(f'Build workers: {jobs} of {available_threads()} logical CPUs', flush=True)
    return jobs


def normalize_build_timestamps(root: Path, progress=print):
    """Repair future archive dates on build inputs, without changing any bytes.

    ZIP dates have no timezone. An archive extracted in another timezone (or
    after a clock correction) can otherwise make Ninja regenerate indefinitely.
    Only reviewed build inputs and VERSION are eligible; no private/user files.
    """
    definition = json.loads((root / 'configs/runtime_inputs.json').read_text(encoding='utf-8'))
    paths = {root / name for name in definition['files']} | {root / 'VERSION'}
    for name in definition['trees']:
        paths.update(p for p in (root / name).rglob('*') if p.is_file())
    now = time.time_ns()
    adjusted = 0
    for path in sorted(paths):
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Build input must stay inside the source folder')
        stat = path.stat()
        if stat.st_mtime_ns > now:
            os.utime(path, ns=(stat.st_atime_ns, now - 2_000_000_000))
            adjusted += 1
    if adjusted:
        progress(f'Adjusted {adjusted} future-dated build input timestamps; file contents were preserved.')
    return adjusted
