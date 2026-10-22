"""Verify the runtime lock and the audited transformation package's Git provenance."""
import importlib.metadata as metadata
import json
from pathlib import Path
import platform

HYPOFORGE_COMMIT = 'c47f636d24a39a820574a13133d6af693134a180'
LOCK = Path(__file__).resolve().parents[1] / 'requirements.lock'


def versions():
    expected = {}
    for line in LOCK.read_text().splitlines():
        if '==' in line:
            name, version = line.split('==')
            expected[name] = version
    expected['hypoforge'] = '0.4.0'
    actual = {name: metadata.version(name) for name in expected}
    for name, version in expected.items():
        if actual[name] != version:
            raise RuntimeError(f'{name} must be {version}, found {actual[name]}')
    direct = json.loads(metadata.distribution('hypoforge').read_text('direct_url.json') or '{}')
    if direct.get('vcs_info', {}).get('commit_id') != HYPOFORGE_COMMIT:
        raise RuntimeError('HypoForge must be installed from the audited Git commit')
    return {'python': platform.python_version(), 'packages': actual,
            'hypoforge_commit': HYPOFORGE_COMMIT}
