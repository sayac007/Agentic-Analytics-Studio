"""File-contract checks only: no generator, fitting or transform implementation."""
import argparse
import csv
from datetime import datetime
from decimal import Decimal
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['period', 'synthetic_media', 'semi_synthetic_outcome']
REFERENCE_COLUMNS = ['period', 'observed_registrations']
MONTH = re.compile(r'[0-9]{4}-(0[1-9]|1[0-2])')
NUMBER = re.compile(r'[+-]?(?:[0-9]+(?:[.][0-9]*)?|[.][0-9]+)(?:[eE][+-]?[0-9]+)?')
SCHEMAS = {p.stem.removesuffix('.schema'): json.loads(p.read_text())
           for p in (ROOT / 'contracts').glob('*.schema.json')}
REGISTRY = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in SCHEMAS.values())


def require_finite_numbers(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('Nonfinite JSON numbers are rejected')
    if isinstance(value, dict):
        for item in value.values():
            require_finite_numbers(item)
    elif isinstance(value, list):
        for item in value:
            require_finite_numbers(item)


def validate_document(kind, document):
    require_finite_numbers(document)
    Draft202012Validator(SCHEMAS[kind], registry=REGISTRY,
                        format_checker=FormatChecker()).validate(document)


def contained(path, root):
    resolved = (root.resolve() / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError('Paths must stay inside the project root')
    return resolved


def artifact_bytes(artifact, root):
    raw = contained(artifact['path'], root).read_bytes()
    if hashlib.sha256(raw).hexdigest() != artifact['sha256']:
        raise ValueError('Artifact checksum mismatch')
    return raw


def artifact_json(artifact, root):
    return json.loads(artifact_bytes(artifact, root))


def csv_rows(artifact, columns, root):
    raw = artifact_bytes(artifact, root)
    try:
        records = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    except csv.Error as error:
        raise ValueError('Malformed CSV') from error
    if not records or records[0] != columns:
        raise ValueError('CSV header must exactly match the allowed interface columns')
    if len(records) == 1:
        raise ValueError('Empty input')
    rows, months = [], []
    for fields in records[1:]:
        if len(fields) != len(columns) or any(not value.strip() for value in fields):
            raise ValueError('Malformed or empty CSV field/record')
        row = dict(zip(columns, fields))
        if MONTH.fullmatch(row['period']) is None:
            raise ValueError('Month must use ASCII YYYY-MM')
        period = datetime.strptime(row['period'], '%Y-%m')
        months.append(period.year * 12 + period.month)
        for key in columns[1:]:
            text = row[key]
            if NUMBER.fullmatch(text) is None:
                raise ValueError('CSV numbers must use decimal notation without whitespace')
            if not math.isfinite(float(text)):
                raise ValueError('Nonfinite CSV values are rejected')
            value = Decimal(text)
            if key != 'semi_synthetic_outcome' and value < 0:
                raise ValueError('Reference and exposure must be nonnegative')
            if key == 'observed_registrations' and value != value.to_integral_value():
                raise ValueError('Registration reference must contain integer counts')
        rows.append(row)
    if any(right != left + 1 for left, right in zip(months, months[1:])):
        raise ValueError('Months must be sorted, unique and consecutive')
    return rows


def split_counts(split, periods):
    if not (split['train_start'] <= split['train_end'] < split['test_start'] <= split['test_end']):
        raise ValueError('Invalid chronological split')
    if periods[0] != split['train_start'] or periods[-1] != split['test_end']:
        raise ValueError('Split must cover the complete input')
    if any(endpoint not in periods for endpoint in split.values()):
        raise ValueError('Split endpoint not in data')
    ntrain = periods.index(split['train_end']) + 1
    if periods.index(split['test_start']) != ntrain:
        raise ValueError('Train and holdout must be adjacent')
    return ntrain, len(periods) - ntrain


def admission(purpose, ntrain, ntest, columns=6, require_benchmark=False):
    if require_benchmark and purpose != 'development_benchmark':
        raise ValueError('Contract fixtures cannot be used as benchmark runs')
    if purpose == 'development_benchmark' and (ntrain < 48 or ntest < 12 or ntrain - columns < 20):
        raise ValueError('Benchmark requires >=48 training and >=12 holdout months, >=20 residual df')


def check_grid(grid, low, high):
    points = grid['spend']
    if any(b <= a for a, b in zip(points, points[1:])) or points[0] < low or points[-1] > high:
        raise ValueError('Spend grid must increase strictly inside training support')


def validate_manifest(manifest, root=ROOT, require_benchmark=False):
    validate_document('manifest', manifest)
    data_path = contained(manifest['data']['path'], root)
    output_path = contained(manifest['outputs']['result'], root)
    if data_path == output_path:
        raise ValueError('Output must not overwrite estimator input')
    rows = csv_rows(manifest['data'], COLUMNS, root)
    ntrain, ntest = split_counts(manifest['split'], [r['period'] for r in rows])
    spec = manifest['estimation']
    breaks = spec['controls']['structural_breaks']
    if len({b['id'] for b in breaks}) != len(breaks):
        raise ValueError('Duplicate structural-break id')
    for change in breaks:
        if not (manifest['split']['train_start'] < change['start'] <= manifest['split']['train_end']):
            raise ValueError('Structural break must be estimable within training')
        if (change['published_on'] > spec['specified_on'] or
                change['published_on'][:7] > manifest['split']['train_end']):
            raise ValueError('Structural-break evidence must precede specification and holdout')
        url = urlsplit(change['evidence_url'])
        if url.scheme != 'https' or not url.hostname:
            raise ValueError('Structural breaks require documented HTTPS evidence')
    columns = 5 + int(spec['controls']['include_quarter_end']) + len(breaks)
    admission(manifest['purpose'], ntrain, ntest, columns, require_benchmark)
    if spec['uncertainty']['max_lags'] >= ntrain:
        raise ValueError('HAC max_lags must be smaller than training length')
    spends = [float(r['synthetic_media']) for r in rows[:ntrain]]
    check_grid(manifest['response_grid'], min(spends), max(spends))
    return len(rows)


def validate_release(record, root=None, as_of=None):
    """Provenance gate only; evidence meaning still requires source review."""
    validate_document('release', record)
    if 'published_on' in record:
        publication = {'precision': 'day', 'value': record['published_on']}
    else:
        publication = record['publication_date']
    retrieved = record.get('retrieved_at')
    if (retrieved and publication['precision'] != 'unknown' and
            publication['value'] > retrieved[:len(publication['value'])]):
        raise ValueError('Publication cannot postdate retrieval')
    available = record.get('available_as_of')
    if available is not None:
        if available['source_sha256'] != record['sha256']:
            raise ValueError('Availability evidence binds a different source vintage')
        url = urlsplit(available['evidence_url'])
        if url.scheme != 'https' or not url.hostname:
            raise ValueError('Availability evidence needs an HTTPS source')
        if root is None:
            raise ValueError('Availability evidence bytes must be checked')
        artifact_bytes(available['evidence'], root)
        stamp = datetime.fromisoformat(available['timestamp'].upper().replace('Z', '+00:00'))
        if (publication['precision'] != 'unknown' and
                stamp.date().isoformat()[:len(publication['value'])] < publication['value']):
            raise ValueError('Availability evidence predates documented publication')
        retrieved = record.get('retrieved_at')
        if retrieved and ((len(retrieved) == 10 and stamp.date().isoformat() > retrieved) or
                          (len(retrieved) > 10 and stamp > datetime.fromisoformat(retrieved.upper().replace('Z', '+00:00')))):
            raise ValueError('Availability evidence postdates retrieval')
    if as_of is not None:
        if publication['precision'] != 'day':
            raise ValueError('Historical point-in-time requires day-precision publication evidence')
        cutoff = datetime.fromisoformat(as_of.upper().replace('Z', '+00:00'))
        if available is None:
            raise ValueError('Historical point-in-time requires exact-vintage availability evidence')
        if stamp > cutoff:
            raise ValueError('Exact vintage was not evidenced as available by cutoff')
    return publication


def validate_generator(generator, root=ROOT, require_benchmark=False):
    validate_document('generator', generator)
    reference = contained(generator['reference']['path'], root)
    outputs = [contained(v, root) for v in generator['outputs'].values()]
    if len(set([reference] + outputs)) != 3:
        raise ValueError('Generator outputs must be distinct from reference and each other')
    rows = csv_rows(generator['reference'], REFERENCE_COLUMNS, root)
    periods = [r['period'] for r in rows]
    if generator['coverage'] != {'start': periods[0], 'end': periods[-1]}:
        raise ValueError('Declared reference coverage does not match its bytes')
    ntrain, ntest = split_counts(generator['split'], periods)
    admission(generator['purpose'], ntrain, ntest, require_benchmark=require_benchmark)
    releases = generator['release_records']
    if generator['reference_kind'] == 'observed_kba':
        if sorted(r['period'] for r in releases) != periods:
            raise ValueError('Observed reference needs one verified release record per month')
        for release in releases:
            cutoff = (generator.get('as_of') if generator.get('admission_regime') ==
                      'historical_point_in_time' else None)
            validate_release(release, root, cutoff)
        if generator['reference_columns']['observed_registrations']['redistribution'] != 'allowed':
            raise ValueError('Observed reference redistribution rights must be verified')
    settings = generator['generation']
    if settings['confounding'] == 'independent' and settings['confounding_strength'] != 0:
        raise ValueError('Independent media requires zero confounding strength')
    if settings['confounding'] != 'independent' and settings['confounding_strength'] <= 0:
        raise ValueError('Confounded media requires positive strength')
    return len(rows)


def intervals_and_curves(document):
    if isinstance(document, dict):
        if {'estimate', 'standard_error', 'lower', 'upper'} <= document.keys():
            if not document['lower'] <= document['estimate'] <= document['upper']:
                raise ValueError('Interval must contain its estimate')
        if {'estimate', 'lower', 'upper', 'interval_kind'} <= document.keys():
            if len({len(document[k]) for k in ['estimate', 'lower', 'upper']}) != 1:
                raise ValueError('Curve arrays must have equal lengths')
            if any(not a <= b <= c for a, b, c in zip(document['lower'], document['estimate'], document['upper'])):
                raise ValueError('Curve bounds must contain point estimates')
        for value in document.values():
            intervals_and_curves(value)
    elif isinstance(document, list):
        for value in document:
            intervals_and_curves(value)


def close(actual, expected):
    if not math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-10):
        raise ValueError('Stored numerical summary does not match its inputs')


def validate_result(result, root=ROOT):
    validate_document('result', result)
    intervals_and_curves(result)
    manifest = artifact_json(result['manifest'], root)
    validate_manifest(manifest, root)
    for key in ['purpose', 'run_id', 'stage', 'split', 'response_grid']:
        if result[key] != manifest[key]:
            raise ValueError('Result/manifest identity or evaluation support mismatch')
    spec = manifest['estimation']
    if result['parameters'] != spec['parameters'] or result['uncertainty'] != spec['uncertainty']:
        raise ValueError('Result differs from predeclared estimation settings')
    if result['data_sha256'] != manifest['data']['sha256']:
        raise ValueError('Result data hash mismatch')
    rows = csv_rows(manifest['data'], COLUMNS, root)
    ntrain, ntest = split_counts(result['split'], [r['period'] for r in rows])
    if result['metrics']['train']['n'] != ntrain or result['metrics']['test']['n'] != ntest:
        raise ValueError('Metric sample counts mismatch')
    changes = spec['controls']['structural_breaks']
    if sorted(b['id'] for b in result['break_coefficients']) != sorted(b['id'] for b in changes):
        raise ValueError('Break coefficient identities mismatch')
    if (result['coefficients']['quarter_end'] is not None) != spec['controls']['include_quarter_end']:
        raise ValueError('Quarter-end coefficient does not match declared controls')
    p = 5 + int(spec['controls']['include_quarter_end']) + len(changes)
    d = result['diagnostics']
    if d['rank'] != p or d['design_columns'] != p or ntrain <= p:
        raise ValueError('Success requires full rank and positive residual degrees of freedom')
    if d['condition_number_limit'] != spec['condition_number_limit'] or d['scaled_condition_number'] < 1:
        raise ValueError('Invalid predeclared condition-number diagnostic')
    flags = ['weak_identification'] if d['scaled_condition_number'] >= d['condition_number_limit'] else []
    if d['flags'] != flags:
        raise ValueError('Identification flags do not match diagnostics')
    contribution = result['contribution']
    if (contribution['start'], contribution['end']) != (result['split']['test_start'], result['split']['test_end']):
        raise ValueError('Contribution must cover the exact holdout')
    if len(contribution['monthly_estimate']) != ntest:
        raise ValueError('Monthly contribution length mismatch')
    close(contribution['total']['estimate'], sum(contribution['monthly_estimate']))
    spends = [float(r['synthetic_media']) for r in rows[:ntrain]]
    if result['training_spend_range'] != {'min': min(spends), 'max': max(spends)}:
        raise ValueError('Training spend support mismatch')
    check_grid(result['response_grid'], min(spends), max(spends))
    if len(result['response_curve']['estimate']) != len(result['response_grid']['spend']):
        raise ValueError('Curve/grid length mismatch')
    return result


def validate_comparison(comparison, root=ROOT):
    validate_document('comparison', comparison)
    sides = []
    for key in ['left', 'right']:
        side = comparison[key]
        result = artifact_json(side['result'], root)
        validate_result(result, root)
        if side['run_id'] != result['run_id'] or result['purpose'] != comparison['purpose']:
            raise ValueError('Comparison/result identity mismatch')
        sides.append(result)
    left, right = sides
    if left['run_id'] == right['run_id']:
        raise ValueError('Comparison requires distinct runs')
    for key in ['data_sha256', 'split', 'target', 'response_grid']:
        if left[key] != right[key]:
            raise ValueError('Comparison support mismatch')
    if comparison['response_grid'] != left['response_grid']:
        raise ValueError('Comparison grid differs from result grids')
    for field, a, b in [
        ('test_rmse_delta_right_minus_left', left['metrics']['test']['rmse'], right['metrics']['test']['rmse']),
        ('media_coefficient_delta_right_minus_left', left['coefficients']['media']['estimate'], right['coefficients']['media']['estimate']),
        ('contribution_delta_right_minus_left', left['contribution']['total']['estimate'], right['contribution']['total']['estimate'])]:
        close(comparison[field], b - a)
    lcurve, rcurve = left['response_curve']['estimate'], right['response_curve']['estimate']
    deltas = [b - a for a, b in zip(lcurve, rcurve)]
    if len(comparison['response_curve_delta_right_minus_left']) != len(deltas):
        raise ValueError('Comparison delta/grid length mismatch')
    for actual, expected in zip(comparison['response_curve_delta_right_minus_left'], deltas):
        close(actual, expected)
    close(comparison['response_curve_rmse'], math.sqrt(sum(x*x for x in deltas)/len(deltas)))
    scale = max(comparison['stability_rule']['scale_floor_count_equivalent'], *(abs(x) for x in lcurve + rcurve))
    relative = max(abs(x) for x in deltas)/scale
    close(comparison['relative_curve_change'], relative)
    flags = set()
    if any(r['diagnostics']['flags'] for r in sides):
        flags.add('weak_identification')
    if relative >= comparison['stability_rule']['relative_curve_change_limit']:
        flags.add('unstable_results')
    if set(comparison['flags']) != flags:
        raise ValueError('Stability flags do not match the declared rule')
    return comparison


def validate_truth(truth, root=ROOT):
    validate_document('truth', truth)
    generator = artifact_json(truth['generator'], root)
    validate_generator(generator, root)
    if truth['purpose'] != generator['purpose'] or truth['reference'] != generator['reference']:
        raise ValueError('Truth/generator reference mismatch')
    if truth['parameters'] != generator['generation']['parameters']:
        raise ValueError('Truth/generator transform mismatch')
    if contained(truth['data']['path'], root) != contained(generator['outputs']['estimator_data'], root):
        raise ValueError('Truth data differs from generator output')
    rows = csv_rows(truth['data'], COLUMNS, root)
    reference = csv_rows(truth['reference'], REFERENCE_COLUMNS, root)
    if [r['period'] for r in rows] != [r['period'] for r in reference]:
        raise ValueError('Generated/reference month alignment mismatch')
    if len(truth['true_contribution_monthly']) != len(rows):
        raise ValueError('Truth contribution length mismatch')
    if len(truth['true_response']) != len(truth['true_response_grid']['spend']):
        raise ValueError('Truth response/grid length mismatch')
    spends = [float(r['synthetic_media']) for r in rows[:split_counts(generator['split'], [r['period'] for r in rows])[0]]]
    check_grid(truth['true_response_grid'], min(spends), max(spends))
    return truth


def validate_evaluation(evaluation, root=ROOT):
    validate_document('evaluation', evaluation)
    result = artifact_json(evaluation['result'], root)
    truth = artifact_json(evaluation['truth'], root)
    validate_result(result, root)
    validate_truth(truth, root)
    if evaluation['run_id'] != result['run_id']:
        raise ValueError('Evaluation run identity mismatch')
    if not (evaluation['purpose'] == result['purpose'] == truth['purpose']):
        raise ValueError('Evaluation purpose mismatch')
    generator = artifact_json(truth['generator'], root)
    if generator['split'] != result['split']:
        raise ValueError('Evaluation generator/estimator split mismatch')
    if result['data_sha256'] != truth['data']['sha256'] or result['parameters'] != truth['parameters']:
        raise ValueError('Oracle evaluation data/transform mismatch')
    if result['response_grid'] != truth['true_response_grid']:
        raise ValueError('Recovery requires identical response grids')
    coef = result['coefficients']['media']
    close(evaluation['media_coefficient_error'], coef['estimate'] - truth['media_coefficient'])
    start = result['metrics']['train']['n']
    close(evaluation['holdout_contribution_error'], result['contribution']['total']['estimate'] - sum(truth['true_contribution_monthly'][start:]))
    delta = [a-b for a, b in zip(result['response_curve']['estimate'], truth['true_response'])]
    close(evaluation['response_curve_rmse'], math.sqrt(sum(x*x for x in delta)/len(delta)))
    outcomes = {'media_interval_covers_truth': coef['lower'] <= truth['media_coefficient'] <= coef['upper'],
                'positive_detection': coef['lower'] > 0,
                'two_sided_rejection': coef['lower'] > 0 or coef['upper'] < 0}
    if any(evaluation[k] != value for k, value in outcomes.items()):
        raise ValueError('Coverage/detection summary does not match interval and truth')
    return evaluation


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='?', type=Path, default=ROOT/'contracts/examples/manifest.json')
    parser.add_argument('--kind', choices=['manifest', 'generator', 'result', 'comparison', 'truth', 'evaluation'], default='manifest')
    parser.add_argument('--require-benchmark', action='store_true')
    args = parser.parse_args()
    document = json.loads(args.file.read_text())
    validator = globals()['validate_' + args.kind]
    kwargs = {'require_benchmark': True} if args.require_benchmark and args.kind in ['manifest', 'generator'] else {}
    if args.require_benchmark and document.get('purpose') != 'development_benchmark':
        raise ValueError('Contract fixtures cannot be used as benchmark runs')
    outcome = validator(document, **kwargs)
    print(f'Valid {args.kind}' + (f' and CSV: {outcome} rows' if isinstance(outcome, int) else ''))
