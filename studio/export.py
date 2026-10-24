"""Gate a complete Stage-A bundle for public synthetic-only workflow export."""
import argparse
import json
from pathlib import Path

from .evaluate import verify_bundle


def require_synthetic(document):
    if (document.get('reference_kind') != 'synthetic_development'
            or document.get('purpose') != 'development_benchmark'):
        raise ValueError('Only a synthetic development reference may be exported')
    columns = document.get('reference_columns', {})
    if not columns or any(c.get('class') != 'synthetic' or c.get('redistribution') != 'allowed'
                          for c in columns.values()):
        raise ValueError('All reference columns require synthetic/redistribution-allowed provenance')


def verify_export(directory):
    root = Path(directory).resolve()
    inventory = verify_bundle(root)
    require_synthetic(json.loads((root / 'private/generator.json').read_text()))
    expected = {
        'protocol.json', 'environment.json', 'implementation.json', 'report.md',
        'comparison.json', 'private/generator.json', 'private/reference.csv',
        'private/truth.json', 'safe/data.csv',
    }
    for name in ('with-quarter', 'without-quarter'):
        expected.add(f'evaluation/{name}.json')
        expected.update(f'safe/{name}.{suffix}' for suffix in
                        ('manifest.json', 'result.json', 'result.predictions.csv', 'access.json'))
    if set(inventory['artifacts']) != expected:
        raise ValueError('Unexpected export membership; refusing additional files')
    for name in ('with-quarter', 'without-quarter'):
        manifest = json.loads((root / f'safe/{name}.manifest.json').read_text())
        if any(c['class'] != 'synthetic' or c['redistribution'] != 'allowed'
               for c in manifest['columns'].values()):
            raise ValueError('Estimator data must also be fully synthetic and redistributable')
    return len(expected) + 1  # Include the existing inventory, no extra hash manifest.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    count = verify_export(args.directory)
    print(f'Verified SYNTHETIC / NOT EMPIRICAL export: {count} original files')


if __name__ == '__main__':
    main()
