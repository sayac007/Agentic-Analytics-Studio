"""Immutable private observed-data snapshots for the Studio and its fixed models."""
import json
import importlib.metadata
import os
from pathlib import Path
import platform
import shutil
import tempfile
from uuid import uuid4

from .data import ROOT, load, sha, json_bytes
from .model import analyze

PROTOCOL = ROOT / 'workorders/03c-empirical-live.md'


def storage_root():
    workspace = Path(os.environ.get('AAS_WORKSPACE_DIR', '.aas-workspace')).resolve()
    # Preserve the legacy SQLite location, but never place observed source files in Git.
    return ROOT.parent/'.aas-private' if workspace.is_relative_to(ROOT) else workspace


def source_directory():
    return Path(os.environ.get('AAS_EMPIRICAL_SOURCE_DIR', str(storage_root()/'observed-sources')))


def destination():
    signature = sha(PROTOCOL.read_bytes() + b''.join((ROOT/'empirical'/n).read_bytes() for n in ('data.py', 'model.py', 'features.py', 'diagnostics.py')) + (ROOT/'data/verified_sources/manifest.json').read_bytes())[:16]
    return Path(os.environ.get('AAS_EMPIRICAL_DIR', str(storage_root() / 'empirical' / signature)))


def build(archive, output):
    out = Path(output).resolve()
    if out.exists() or out.is_relative_to(ROOT) or any(p.is_symlink() for p in (Path(output), *Path(output).parents)):
        raise ValueError('New private output directory outside Git required')
    data = load(archive)
    results = analyze(data)
    provenance = {'classification': 'OBSERVED_PRIVATE', 'protocol_sha256': sha(PROTOCOL.read_bytes()),
                  'input_hashes': {k: v['sha256'] for k, v in data['sources'].items()},
                  'python': platform.python_version(),
                  'packages': {p: importlib.metadata.version(p) for p in ('numpy', 'pandas', 'scipy', 'statsmodels', 'openpyxl', 'xlrd')}, 'public_redistribution_allowed': False,
                  'historical_point_in_time': False, 'synthetic_inputs': False,
                  'policy_review': 'historical review records retained; no claim of fresh policy retrieval',
                  'implementation': {name: sha((ROOT/name).read_bytes()) for name in ('empirical/data.py', 'empirical/model.py', 'empirical/features.py', 'empirical/diagnostics.py', 'fuel_oil/scoped_study.py')},
                  'feature_library': results['feature_library'],
                  'source_archive_manifest_sha256': sha((Path(archive)/'manifest.json').read_bytes()),
                  'source_review_manifest_sha256': sha((ROOT/'data/verified_sources/manifest.json').read_bytes())}
    out.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix='.empirical-', dir=out.parent))
    try:
        for name, value in [('data.json', data), ('results.json', results), ('provenance.json', provenance)]:
            (stage/name).write_bytes(json_bytes(value)); (stage/name).chmod(0o600)
        manifest = {'version': 'observed-studio-v1', 'classification': 'OBSERVED_PRIVATE',
                    'files': {p.name: sha(p.read_bytes()) for p in stage.iterdir()}}
        (stage/'manifest.json').write_bytes(json_bytes(manifest))
        (stage/'manifest.json').chmod(0o600)
        stage.rename(out)
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return read(out)


def read(directory=None):
    root = Path(directory) if directory is not None else destination()
    if root.is_symlink(): raise ValueError('Unsafe empirical directory')
    if (root/'manifest.json').is_symlink(): raise ValueError('Unsafe empirical manifest')
    if not (root/'manifest.json').is_file():
        raise FileNotFoundError('Empirical observations have not been installed')
    raw = (root/'manifest.json').read_bytes(); m = json.loads(raw)
    if m.get('version') != 'observed-studio-v1' or m.get('classification') != 'OBSERVED_PRIVATE' or set(m.get('files', {})) != {'data.json', 'results.json', 'provenance.json'}:
        raise ValueError('Unapproved empirical manifest')
    values = {}
    for name, expected in m['files'].items():
        p = root/name
        if p.is_symlink() or p.stat().st_size > 2_000_000: raise ValueError('Unsafe empirical artifact')
        b = p.read_bytes()
        if sha(b) != expected: raise ValueError('Changed empirical result')
        values[name[:-5]] = json.loads(b)
    if values['provenance'].get('protocol_sha256') != sha(PROTOCOL.read_bytes()):
        raise ValueError('Empirical protocol identity changed')
    if values['provenance'].get('synthetic_inputs') is not False or values['data'].get('classification') != 'OBSERVED_PRIVATE' or values['results'].get('classification') != 'OBSERVED_PRIVATE':
        raise ValueError('Empirical/synthetic scope mismatch')
    values['snapshot_sha256'] = sha(raw)
    return values
