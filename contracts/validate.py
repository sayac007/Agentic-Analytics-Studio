"""Task 00 contract validation only; no data acquisition or model execution."""
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['period', 'observed_registrations', 'synthetic_media', 'semi_synthetic_outcome']
MONTH = re.compile(r'[0-9]{4}-(0[1-9]|1[0-2])')
NUMBER = re.compile(r'[+-]?(?:[0-9]+(?:[.][0-9]*)?|[.][0-9]+)(?:[eE][+-]?[0-9]+)?')


def require_finite_numbers(value):
    """JSON Schema alone does not exclude Python's NaN/Infinity extensions."""
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Nonfinite JSON numbers are rejected')
    if isinstance(value, dict):
        for item in value.values():
            require_finite_numbers(item)
    elif isinstance(value, list):
        for item in value:
            require_finite_numbers(item)


def validate_manifest(manifest, root=ROOT):
    require_finite_numbers(manifest)
    schema = json.loads((ROOT / 'contracts/manifest.schema.json').read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    root = root.resolve()
    data_path = (root / manifest['data']['path']).resolve()
    output_path = (root / manifest['outputs']['result']).resolve()
    if not all(path.is_relative_to(root) for path in [data_path, output_path]):
        raise ValueError('Input and output must stay inside the project root')
    raw = data_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest['data']['sha256']:
        raise ValueError('Data checksum mismatch')
    # Parse precisely the bytes whose checksum was checked; do not reopen the file.
    try:
        records = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    except csv.Error as error:
        raise ValueError('Malformed CSV') from error
    if not records or records[0] != COLUMNS:
        raise ValueError('CSV header must exactly match ordered manifest columns')
    if len(records) == 1:
        raise ValueError('Empty input')
    months, periods = [], []
    for fields in records[1:]:
        if len(fields) != len(COLUMNS) or any(not value.strip() for value in fields):
            raise ValueError('Malformed or empty CSV field/record')
        row = dict(zip(COLUMNS, fields))
        if MONTH.fullmatch(row['period']) is None:
            raise ValueError('Month must use ASCII YYYY-MM')
        period = datetime.strptime(row['period'], '%Y-%m')
        periods.append(row['period'])
        months.append(period.year * 12 + period.month)
        for key in COLUMNS[1:]:
            text = row[key]
            if NUMBER.fullmatch(text) is None:
                raise ValueError('CSV numbers must use decimal notation without whitespace')
            if not math.isfinite(float(text)):
                raise ValueError('Nonfinite values are rejected')
            value = Decimal(text)
            if key != 'semi_synthetic_outcome' and value < 0:
                raise ValueError('Reference and exposure must be nonnegative')
            if key == 'observed_registrations' and value != value.to_integral_value():
                raise ValueError('Registration reference must contain integer counts')
    if any(right != left + 1 for left, right in zip(months, months[1:])):
        raise ValueError('Months must be sorted, unique and consecutive')
    split = manifest['split']
    if not (split['train_start'] <= split['train_end'] < split['test_start'] <= split['test_end']):
        raise ValueError('Invalid chronological split')
    if periods[0] != split['train_start'] or periods[-1] != split['test_end']:
        raise ValueError('Split must cover the complete input')
    for endpoint in split.values():
        if endpoint not in periods:
            raise ValueError('Split endpoint not in data')
    if periods.index(split['test_start']) != periods.index(split['train_end']) + 1:
        raise ValueError('Train and holdout must be adjacent')
    return len(periods)


if __name__ == '__main__':
    file = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'contracts/examples/manifest.json'
    print(f'Valid manifest and CSV: {validate_manifest(json.loads(file.read_text()))} rows')
