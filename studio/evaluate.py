"""Post-fit truth evaluation, same-support comparison and immutable bundle checks."""
import csv
import json
import math
from pathlib import Path
from contracts import validate as v
from .files import artifact, store


def evaluate(root, result_relative):
    result = json.loads((root/result_relative).read_text())
    truth = json.loads((root/'private/truth.json').read_text())
    v.validate_result(result, root)
    v.validate_truth(truth, root)
    coefficient = result['coefficients']['media']
    ntrain = result['metrics']['train']['n']
    delta = [a-b for a,b in zip(result['response_curve']['estimate'], truth['true_response'])]
    evaluation = {'schema_version': '0.2.0', 'purpose': result['purpose'], 'run_id': result['run_id'],
                  'result': artifact(root, result_relative), 'truth': artifact(root, 'private/truth.json'),
                  'media_coefficient_error': coefficient['estimate']-truth['media_coefficient'],
                  'holdout_contribution_error': result['contribution']['total']['estimate']-
                                                 sum(truth['true_contribution_monthly'][ntrain:]),
                  'response_curve_rmse': math.sqrt(sum(x*x for x in delta)/len(delta)),
                  'media_interval_covers_truth': coefficient['lower'] <= truth['media_coefficient'] <= coefficient['upper'],
                  'positive_detection': coefficient['lower'] > 0,
                  'two_sided_rejection': coefficient['lower'] > 0 or coefficient['upper'] < 0,
                  'detection_limit_status': 'not_calibrated', 'effect_below_detection_limit': None,
                  'claim': result['claim']}
    v.validate_evaluation(evaluation, root)
    name = Path(result_relative).name.removesuffix('.result.json')
    store(root/'evaluation'/f'{name}.json', evaluation)
    return evaluation


def compare(root, rule):
    left = json.loads((root/'safe/with-quarter.result.json').read_text())
    right = json.loads((root/'safe/without-quarter.result.json').read_text())
    lcurve, rcurve = left['response_curve']['estimate'], right['response_curve']['estimate']
    differences = [b-a for a,b in zip(lcurve,rcurve)]
    scale = max(rule['scale_floor_count_equivalent'], *(abs(x) for x in lcurve+rcurve))
    relative = max(abs(x) for x in differences)/scale
    flags = []
    if any(r['diagnostics']['flags'] for r in [left,right]):
        flags.append('weak_identification')
    if relative >= rule['relative_curve_change_limit']:
        flags.append('unstable_results')
    comparison = {'schema_version': '0.2.0', 'purpose': left['purpose'], 'comparison_id': 'quarter-end-sensitivity-v1',
                  'left': {'run_id': left['run_id'], 'result': artifact(root,'safe/with-quarter.result.json')},
                  'right': {'run_id': right['run_id'], 'result': artifact(root,'safe/without-quarter.result.json')},
                  'same_data_and_holdout': True, 'response_grid': left['response_grid'],
                  'test_rmse_delta_right_minus_left': right['metrics']['test']['rmse']-left['metrics']['test']['rmse'],
                  'media_coefficient_delta_right_minus_left': right['coefficients']['media']['estimate']-left['coefficients']['media']['estimate'],
                  'contribution_delta_right_minus_left': right['contribution']['total']['estimate']-left['contribution']['total']['estimate'],
                  'response_curve_delta_right_minus_left': differences,
                  'response_curve_rmse': math.sqrt(sum(x*x for x in differences)/len(differences)),
                  'relative_curve_change': relative, 'stability_rule': rule, 'flags': flags,
                  'uncertainty_interpretation': 'per_run_pointwise_intervals_no_unjustified_delta_interval',
                  'detection_limit_status': 'not_calibrated', 'effect_below_detection_limit': None,
                  'claim': left['claim']}
    v.validate_comparison(comparison,root)
    store(root/'comparison.json',comparison)
    return comparison


def validate_predictions(root, name):
    result = json.loads((root/f'safe/{name}.result.json').read_text())
    manifest = v.artifact_json(result['manifest'],root)
    data = v.csv_rows(manifest['data'],v.COLUMNS,root)[result['metrics']['train']['n']:]
    with (root/f'safe/{name}.result.predictions.csv').open(newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['period','semi_synthetic_outcome','prediction','residual']:
            raise ValueError('Invalid prediction sidecar header')
        predictions = list(reader)
    if len(predictions) != len(data):
        raise ValueError('Prediction count mismatch')
    residuals = []
    for expected, prediction in zip(data,predictions):
        if prediction['period'] != expected['period']:
            raise ValueError('Prediction month mismatch')
        actual, fitted, residual = [float(prediction[k]) for k in ['semi_synthetic_outcome','prediction','residual']]
        if not all(math.isfinite(x) for x in [actual,fitted,residual]):
            raise ValueError('Nonfinite prediction')
        v.close(actual,float(expected['semi_synthetic_outcome']))
        v.close(residual,actual-fitted)
        residuals.append(residual)
    v.close(result['metrics']['test']['rmse'],math.sqrt(sum(x*x for x in residuals)/len(residuals)))
    v.close(result['metrics']['test']['mae'],sum(abs(x) for x in residuals)/len(residuals))


def verify_bundle(root):
    inventory = json.loads((root/'inventory.json').read_text())
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p != root/'inventory.json')
    if files != sorted(inventory['artifacts']):
        raise ValueError('Bundle file membership mismatch')
    for name, digest in inventory['artifacts'].items():
        v.artifact_bytes({'path':name,'sha256':digest},root)
    v.validate_generator(json.loads((root/'private/generator.json').read_text()),root,require_benchmark=True)
    v.validate_truth(json.loads((root/'private/truth.json').read_text()),root)
    for name in ['with-quarter','without-quarter']:
        result = json.loads((root/f'safe/{name}.result.json').read_text())
        v.validate_result(result,root)
        v.validate_evaluation(json.loads((root/f'evaluation/{name}.json').read_text()),root)
        validate_predictions(root,name)
    v.validate_comparison(json.loads((root/'comparison.json').read_text()),root)
    return inventory
