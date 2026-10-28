import argparse
from pathlib import Path
from .service import build
from .restore import restore

p = argparse.ArgumentParser(description='Private observed-data Studio; no synthetic fallback')
p.add_argument('command', choices=('restore', 'build'))
p.add_argument('--source-archive', type=Path, required=True)
p.add_argument('--output', type=Path)
a = p.parse_args()
if a.command == 'restore':
    import json
    print(json.dumps(restore(a.source_archive), indent=2))
else:
    if a.output is None: p.error('--output is required for build')
    result = build(a.source_archive, a.output)
    print('Verified private observed-data result:', result['snapshot_sha256'])
