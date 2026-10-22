"""Task 00 contract validation only; no data acquisition or model execution."""
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def validate_manifest(manifest, root=ROOT):
    schema = json.loads((ROOT / 'contracts/manifest.schema.json').read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    data_path = (root / manifest['data']['path']).resolve()
    if not data_path.is_relative_to(root.resolve()):
        raise ValueError('Input must stay inside the project root')
    raw = data_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest['data']['sha256']:
        raise ValueError('Data checksum mismatch')
    with data_path.open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['period', 'observed_registrations', 'synthetic_media', 'semi_synthetic_outcome']:
            raise ValueError('CSV header must exactly match ordered manifest columns')
        rows = list(reader)
    if not rows:
        raise ValueError('Empty input')
    months = []
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError('Malformed CSV row')
        period = datetime.strptime(row['period'], '%Y-%m')
        if period.strftime('%Y-%m') != row['period']:
            raise ValueError('Month must use YYYY-MM')
        months.append(period.year * 12 + period.month)
        for key in ('observed_registrations', 'synthetic_media', 'semi_synthetic_outcome'):
            value = float(row[key])
            if not math.isfinite(value):
                raise ValueError('Missing/nonfinite values are rejected')
            if key != 'semi_synthetic_outcome' and value < 0:
                raise ValueError('Reference and exposure must be nonnegative')
            if key == 'observed_registrations' and value != int(value):
                raise ValueError('Registration reference must contain integer counts')
    if any(right != left + 1 for left, right in zip(months, months[1:])):
        raise ValueError('Months must be sorted, unique and consecutive')
    split = manifest['split']
    if not (split['train_start'] <= split['train_end'] < split['test_start'] <= split['test_end']):
        raise ValueError('Invalid chronological split')
    periods = [row['period'] for row in rows]
    if periods[0] != split['train_start'] or periods[-1] != split['test_end']:
        raise ValueError('Split must cover the complete input')
    for endpoint in split.values():
        if endpoint not in periods:
            raise ValueError('Split endpoint not in data')
    if periods.index(split['test_start']) != periods.index(split['train_end']) + 1:
        raise ValueError('Train and holdout must be adjacent')
    return len(rows)


if __name__ == '__main__':
    file = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'contracts/examples/manifest.json'
    print(f'Valid manifest and CSV: {validate_manifest(json.loads(file.read_text()))} rows')
