"""Verify a complete, synthetic-only research-task-02 data manifest and summaries."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from .run import PROTOCOL_SHA


def verify(directory):
    root=Path(directory).resolve()
    manifest=json.loads((root/'manifest.json').read_text())
    if manifest.get('scope')!='SYNTHETIC_ONLY' or manifest.get('protocol_sha256')!=PROTOCOL_SHA:
        raise ValueError('Not an approved new-stage synthetic experiment')
    n=manifest['seeds_per_cell']
    expected={'truth.csv','evaluations.csv','summary.csv','mde.csv','reference.csv','protocol.json','report.md','power.png'}
    if n>42:expected.add('legacy_flags.csv')
    if set(manifest['files'])!=expected or {p.name for p in root.iterdir()}!=expected|{'manifest.json'}:
        raise ValueError('Unexpected artifact membership')
    for name,digest in manifest['files'].items():
        path=root/name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError('Changed or unsafe experiment artifact')
    if hashlib.sha256((root/'protocol.json').read_bytes()).hexdigest()!=PROTOCOL_SHA:
        raise ValueError('Protocol bytes changed')
    with (root/'truth.csv').open() as f:truth=list(csv.DictReader(f))
    with (root/'evaluations.csv').open() as f:evaluations=list(csv.DictReader(f))
    with (root/'summary.csv').open() as f:summary=list(csv.DictReader(f))
    if len(truth)!=18*n or len(evaluations)!=36*n or len(summary)!=36:
        raise ValueError('Incomplete grid or seed accounting')
    identities={(r['cell'],r['seed']) for r in truth}
    if len(identities)!=len(truth) or any((r['cell'],r['seed']) not in identities for r in evaluations):
        raise ValueError('Truth/evaluation key mismatch')
    if len({(r['cell'],r['seed'],r['model']) for r in evaluations})!=len(evaluations):
        raise ValueError('Duplicate model/seed evaluation')
    for row in summary:
        if int(row['scheduled'])!=n or int(row['estimated'])+int(row['failed'])!=n:
            raise ValueError('Failure denominator mismatch')
    print(f'Verified synthetic experiment: {len(truth)} truth rows, {len(evaluations)} fits, 36 summaries')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path)
    verify(p.parse_args().directory)


if __name__=='__main__':main()
