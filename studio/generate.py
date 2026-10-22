"""The approved, explicitly synthetic 72-month Stage-A development DGP."""
import numpy as np
from contracts import validate as v
from .files import artifact, csv_bytes, store, write_once
from .runtime import versions
from .transforms import media_feature, steady_response_feature, finite

CLAIM = 'benchmark_recovery_not_real_causal_marketing_roi'
SPLIT = {'train_start': '2018-01', 'train_end': '2022-12',
         'test_start': '2023-01', 'test_end': '2023-12'}
PARAMETERS = {'alpha': .5, 'l_max': 3, 'normalize': False, 'k': 100, 'n': 1.5}


def lineage(unit, method, date):
    return {'class': 'synthetic', 'publisher': 'Agentic Analytics Studio',
            'source_or_generator': 'synthetic_development_reference_v1', 'access_date': date,
            'geography': 'Fictional monthly development series; not Tesla or observed Germany data',
            'time_grain': 'month', 'unit': unit,
            'rights': 'Project-generated synthetic development data; no external source data',
            'redistribution': 'allowed', 'transformations': method,
            'limitations': 'Single synthetic benchmark; not real marketing ROI, power or MDE evidence'}


def baseline():
    t = np.arange(72)
    months = t % 12 + 1
    quarter_end = np.isin(months, [3, 6, 9, 12]).astype(float)
    reference = np.rint(2000 + 15*t + 250*np.sin(2*np.pi*t/12) +
                        300*quarter_end + 600*(t >= 36) + 900*(t == 50)).astype(int)
    periods = [f'{2018+i//12:04d}-{i%12+1:02d}' for i in t]
    return periods, reference, quarter_end


def generate(root, protocol):
    versions()  # fail before writing artifacts when required dependencies differ
    if (protocol['start'], protocol['months'], protocol['train_months'], protocol['seed'],
        protocol['effect_fraction'], protocol['noise_fraction'], protocol['confounding'],
        protocol['parameters'], protocol['hac_max_lags'], protocol['grid_points']) != (
            '2018-01', 72, 60, 42, .08, .05, 'independent', PARAMETERS, 3, 21):
        raise ValueError('Only the predeclared Task 01a protocol is implemented')
    periods, reference, quarter_end = baseline()
    write_once(root/'private/reference.csv', csv_bytes(v.REFERENCE_COLUMNS,
               zip(periods, reference.tolist())))
    reference_artifact = artifact(root, 'private/reference.csv')
    generator = {
        'schema_version': '0.2.0', 'purpose': 'development_benchmark',
        'generator_id': 'synthetic_development_reference_v1', 'reference_kind': 'synthetic_development',
        'reference': reference_artifact, 'reference_columns': {
            'period': lineage('calendar_month', 'Monthly calendar index', protocol['specified_on']),
            'observed_registrations': lineage('fictional_count',
                'round(2000+15*t+250*sin(2*pi*t/12)+300*quarter_end+600*(t>=36)+900*(t==50)); ties to even',
                protocol['specified_on'])},
        'vintage': 'synthetic_v1; protocol_sha256=' + artifact(root, 'protocol.json')['sha256'],
        'coverage': {'start': periods[0], 'end': periods[-1]}, 'release_records': [],
        'split': SPLIT, 'estimator_access': False,
        'generation': {'implementation_id': 'studio.generate.v1', 'seed': 42, 'rng': 'PCG64',
                       'effect_fraction': .08, 'noise_fraction': .05, 'confounding': 'independent',
                       'confounding_strength': 0, 'parameters': PARAMETERS,
                       'calibration': 'training_reference_mean_only'},
        'outputs': {'estimator_data': 'safe/data.csv', 'truth': 'private/truth.json'}}
    v.validate_generator(generator, root, require_benchmark=True)
    store(root/'private/generator.json', generator)
    # Reference bytes, provenance and configuration are frozen BEFORE media injection.
    frozen = v.csv_rows(reference_artifact, v.REFERENCE_COLUMNS, root)
    B = np.array([float(row['observed_registrations']) for row in frozen])
    media_seed, noise_seed = np.random.SeedSequence(42).spawn(2)
    media_rng = np.random.Generator(np.random.PCG64(media_seed))
    noise_rng = np.random.Generator(np.random.PCG64(noise_seed))
    spend = 100*np.exp(.3*media_rng.standard_normal(72))  # lambda=0, independent scenario
    h = media_feature(spend, PARAMETERS)
    training_mean = float(B[:60].mean())
    response_mean = float(h[:60].mean())
    if response_mean <= 0:
        raise ValueError('Positive training response required for effect scaling')
    beta = .08*training_mean/response_mean
    noise_sd = .05*training_mean
    contribution = beta*h
    outcome = finite(B + contribution + noise_rng.normal(0, noise_sd, 72))
    write_once(root/'safe/data.csv', csv_bytes(v.COLUMNS,
               [(p, format(x, '.17g'), format(y, '.17g')) for p, x, y in zip(periods, spend, outcome)]))
    grid = {'spend': np.linspace(spend[:60].min(), spend[:60].max(), 21).tolist(),
            'unit': 'synthetic_currency_per_month', 'history': 'constant_spend_for_full_finite_kernel',
            'support': 'common_training_spend_range'}
    truth = {'schema_version': '0.2.0', 'purpose': 'development_benchmark',
             'dataset_id': 'synthetic-72-seed42-v1', 'estimator_access': False,
             'data': artifact(root, 'safe/data.csv'), 'reference': reference_artifact,
             'generator': artifact(root, 'private/generator.json'), 'parameters': PARAMETERS,
             'media_coefficient': float(beta), 'noise_sd': noise_sd,
             'training_reference_mean': training_mean,
             'equation': 'outcome = reference + media_coefficient * hill(adstock(media)) + noise',
             'true_contribution_monthly': contribution.tolist(), 'true_response_grid': grid,
             'true_response': (beta*steady_response_feature(grid['spend'], PARAMETERS)).tolist(),
             'claim': CLAIM}
    v.validate_truth(truth, root)
    store(root/'private/truth.json', truth)
    for include, name in [(True, 'with-quarter'), (False, 'without-quarter')]:
        manifest = {'schema_version': '0.2.0', 'purpose': 'development_benchmark', 'run_id': name,
                    'stage': 'A', 'claim': CLAIM, 'data': truth['data'], 'columns': {
                        'period': lineage('calendar_month', 'Monthly calendar index', protocol['specified_on']),
                        'synthetic_media': lineage('synthetic_currency_per_month', 'Independent seeded lognormal media', protocol['specified_on']),
                        'semi_synthetic_outcome': lineage('count_equivalent', 'Separate injected outcome; generator ID only, no reference values', protocol['specified_on'])},
                    'split': SPLIT, 'missing_policy': 'reject', 'estimation': {
                        'runtime': 'python', 'method': 'ols', 'target': 'semi_synthetic_outcome',
                        'controls': {'trend': 'month_index_from_train_start', 'annual_fourier_order': 1,
                                     'include_quarter_end': include, 'structural_breaks': []},
                        'transform_order': ['geometric_adstock', 'hill'], 'parameters': PARAMETERS,
                        'parameter_policy': 'predeclared_oracle_transforms_without_baseline_or_truth_access',
                        'specified_on': protocol['specified_on'], 'uncertainty': {
                            'method': 'newey_west_bartlett', 'max_lags': 3,
                            'finite_sample_correction': 'n_over_n_minus_p', 'reference_distribution': 'normal',
                            'confidence_level': .95, 'conditioning': 'fixed_predeclared_transforms_and_controls'},
                        'condition_number_limit': protocol['condition_number_limit']},
                    'response_grid': grid, 'outputs': {'result': f'safe/{name}.result.json'}}
        v.validate_manifest(manifest, root, require_benchmark=True)
        store(root/f'safe/{name}.manifest.json', manifest)
    if artifact(root, 'private/reference.csv') != reference_artifact:
        raise ValueError('Reference changed during generation')
    return truth
