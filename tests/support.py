"""Hand-authored shape fixtures; never fitted models or simulation evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def template(name='manifest'):
    return json.loads((ROOT / f'contracts/examples/{name}.json').read_text())


def artifact(root, name):
    return {'path': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}


def store(root, name, document):
    (root / name).write_text(json.dumps(document, indent=2) + '\n')
    return artifact(root, name)


def interval(estimate, standard_error=.1):
    return {'estimate': estimate, 'standard_error': standard_error,
            'lower': estimate-1.96*standard_error, 'upper': estimate+1.96*standard_error,
            'confidence_level': .95}


def graph(root):
    """A complete synthetic file graph for validation, without executing the DGP."""
    periods = [f'{2019+i//12:04d}-{i%12+1:02d}' for i in range(60)]
    (root / 'data.csv').write_text('period,synthetic_media,semi_synthetic_outcome\n' +
                                 ''.join(f'{p},{2*(i%2)},{10+i%4+.5}\n' for i,p in enumerate(periods)))
    (root / 'reference.csv').write_text('period,observed_registrations\n' +
                                      ''.join(f'{p},{10+i%4}\n' for i,p in enumerate(periods)))
    manifest = template()
    manifest['data'] = artifact(root, 'data.csv')
    manifest['split'] = {'train_start': '2019-01', 'train_end': '2022-12',
                         'test_start': '2023-01', 'test_end': '2023-12'}
    manifest['estimation']['specified_on'] = '2018-12-31'
    generator = template('generator')
    generator['reference'] = artifact(root, 'reference.csv')
    generator['coverage'] = {'start': periods[0], 'end': periods[-1]}
    generator['split'] = manifest['split']
    generator['outputs'] = {'estimator_data': 'data.csv', 'truth': 'truth.json'}
    generator_ref = store(root, 'generator.json', generator)
    for run in ['left', 'right']:
        manifest['run_id'] = run
        manifest['outputs']['result'] = run + '.json'
        manifest_ref = store(root, run + '-manifest.json', manifest)
        result = {
            'schema_version': '0.2.0', 'purpose': 'contract_fixture', 'run_id': run, 'stage': 'A',
            'manifest': manifest_ref, 'data_sha256': manifest['data']['sha256'], 'status': 'success',
            'target': 'semi_synthetic_outcome', 'split': manifest['split'],
            'coefficients': {k: interval(1 if k=='media' else 0) for k in
                             ['intercept','trend','annual_sin_1','annual_cos_1','media','quarter_end']},
            'break_coefficients': [], 'parameters': manifest['estimation']['parameters'],
            'uncertainty': manifest['estimation']['uncertainty'],
            'metrics': {'train': {'n':48,'mae':1,'rmse':1}, 'test': {'n':12,'mae':1,'rmse':1}},
            'diagnostics': {'rank':6, 'design_columns':6, 'scaled_condition_number':10,
                            'condition_number_limit':1e8, 'flags':[]},
            'contribution': {'start':'2023-01','end':'2023-12','unit':'count_equivalent',
                             'monthly_estimate':[.5]*12,'total':interval(6)},
            'training_spend_range': {'min':0,'max':2}, 'response_grid':manifest['response_grid'],
            'response_curve': {'estimate':[0,.5,1], 'lower':[-.1,.4,.9], 'upper':[.1,.6,1.1],
                               'interval_kind':'pointwise_not_simultaneous'},
            'software': {'python':'shape-only','numpy':'shape-only','hypoforge_commit':'0'*40},
            'claim': manifest['claim']}
        store(root, run+'.json', result)
    truth = {'schema_version':'0.2.0','purpose':'contract_fixture','dataset_id':'shape-only-dataset','estimator_access':False,
             'data':manifest['data'],'reference':generator['reference'],'generator':generator_ref,
             'parameters':manifest['estimation']['parameters'],'media_coefficient':.9,'noise_sd':1,
             'training_reference_mean':11.5,
             'equation':'outcome = reference + media_coefficient * hill(adstock(media)) + noise',
             'true_contribution_monthly':[.4]*60, 'true_response_grid':manifest['response_grid'],
             'true_response':[0,.4,.8], 'claim':manifest['claim']}
    truth_ref = store(root, 'truth.json', truth)
    comparison = {'schema_version':'0.2.0','purpose':'contract_fixture','comparison_id':'shape-only',
                  'left':{'run_id':'left','result':artifact(root,'left.json')},
                  'right':{'run_id':'right','result':artifact(root,'right.json')},
                  'same_data_and_holdout':True,'response_grid':manifest['response_grid'],
                  'test_rmse_delta_right_minus_left':0,'media_coefficient_delta_right_minus_left':0,
                  'contribution_delta_right_minus_left':0,'response_curve_delta_right_minus_left':[0,0,0],
                  'response_curve_rmse':0,'relative_curve_change':0,
                  'stability_rule':{'relative_curve_change_limit':.25,'scale_floor_count_equivalent':1},
                  'flags':[],'uncertainty_interpretation':'per_run_pointwise_intervals_no_unjustified_delta_interval',
                  'detection_limit_status':'not_calibrated','effect_below_detection_limit':None,
                  'claim':manifest['claim']}
    evaluation = {'schema_version':'0.2.0','purpose':'contract_fixture','run_id':'left',
                  'result':artifact(root,'left.json'),'truth':truth_ref,'media_coefficient_error':.1,
                  'holdout_contribution_error':1.2,'response_curve_rmse':((.1**2+.2**2)/3)**.5,
                  'media_interval_covers_truth':True,'positive_detection':True,'two_sided_rejection':True,
                  'detection_limit_status':'not_calibrated','effect_below_detection_limit':None,
                  'claim':manifest['claim']}
    return {'manifest':template(), 'generator':generator, 'truth':truth,
            'result':result, 'comparison':comparison,'evaluation':evaluation}
