"""Estimator entry point: safe manifest/CSV only; no generator/evaluator imports."""
import argparse
import json
from pathlib import Path
import numpy as np
from contracts import validate as v
from .files import artifact, csv_bytes, store, write_once
from .runtime import versions, HYPOFORGE_COMMIT
from .statistics import design, ols_hac, interval, metrics
from .transforms import finite, steady_response_feature


def estimate(root, relative):
    environment = versions()
    manifest = json.loads(v.contained(relative, root).read_text())
    v.validate_manifest(manifest, root, require_benchmark=True)
    output = v.contained(manifest['outputs']['result'], root)
    if output.exists() or output.is_symlink():
        raise FileExistsError('Refusing to replace an existing result')
    rows = v.csv_rows(manifest['data'], v.COLUMNS, root)
    periods = [r['period'] for r in rows]
    ntrain, _ = v.split_counts(manifest['split'], periods)
    spend = np.array([float(r['synthetic_media']) for r in rows])
    y = np.array([float(r['semi_synthetic_outcome']) for r in rows])
    spec = manifest['estimation']
    # Causal full-series transform retains train history. No y_holdout enters fitting.
    X, names = design(periods, spend, spec)
    coefficients, covariance, rank, condition = ols_hac(X[:ntrain], y[:ntrain], spec['uncertainty']['max_lags'])
    predictions = finite(X @ coefficients)
    se = np.sqrt(np.diag(covariance))
    estimated = {name: interval(b, s) for name, b, s in zip(names, coefficients, se)}
    media_index = names.index('media')
    h_test = X[ntrain:, media_index]
    beta = coefficients[media_index]
    beta_se = se[media_index]
    monthly = finite(beta*h_test)
    response_feature = steady_response_feature(manifest['response_grid']['spend'], spec['parameters'])
    response = finite(beta*response_feature)
    response_se = np.abs(response_feature)*beta_se
    result = {'schema_version': '0.2.0', 'purpose': manifest['purpose'], 'run_id': manifest['run_id'],
              'stage': 'A', 'manifest': artifact(root, relative), 'data_sha256': manifest['data']['sha256'],
              'status': 'success', 'target': 'semi_synthetic_outcome', 'split': manifest['split'],
              'coefficients': {name: estimated.get(name) for name in
                               ['intercept','trend','annual_sin_1','annual_cos_1','media','quarter_end']},
              'break_coefficients': [{'id': change['id'], 'interval': estimated['break:'+change['id']]}
                                     for change in spec['controls']['structural_breaks']],
              'parameters': spec['parameters'], 'uncertainty': spec['uncertainty'],
              'metrics': {'train': metrics(y[:ntrain], predictions[:ntrain]),
                          'test': metrics(y[ntrain:], predictions[ntrain:])},
              'diagnostics': {'rank': rank, 'design_columns': X.shape[1], 'scaled_condition_number': condition,
                              'condition_number_limit': spec['condition_number_limit'],
                              'flags': ['weak_identification'] if condition >= spec['condition_number_limit'] else []},
              'contribution': {'start': manifest['split']['test_start'], 'end': manifest['split']['test_end'],
                               'unit': 'count_equivalent', 'monthly_estimate': monthly.tolist(),
                               'total': interval(float(monthly.sum()), abs(float(h_test.sum()))*beta_se)},
              'training_spend_range': {'min': float(spend[:ntrain].min()), 'max': float(spend[:ntrain].max())},
              'response_grid': manifest['response_grid'], 'response_curve': {
                  'estimate': response.tolist(), 'lower': [interval(b,s)['lower'] for b,s in zip(response,response_se)],
                  'upper': [interval(b,s)['upper'] for b,s in zip(response,response_se)],
                  'interval_kind': 'pointwise_not_simultaneous'},
              'software': {'python': environment['python'], 'numpy': np.__version__,
                           'hypoforge_commit': HYPOFORGE_COMMIT}, 'claim': manifest['claim']}
    v.validate_result(result, root)  # no successful artifact published until all checks pass
    prediction_path = output.with_name(output.stem + '.predictions.csv')
    write_once(prediction_path, csv_bytes(['period','semi_synthetic_outcome','prediction','residual'],
               [(p, format(actual,'.17g'), format(predicted,'.17g'), format(actual-predicted,'.17g'))
                for p,actual,predicted in zip(periods[ntrain:],y[ntrain:],predictions[ntrain:])]))
    store(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--manifest', required=True)
    args = parser.parse_args()
    from .isolation import guard
    reads = guard(args.root.resolve())
    result = estimate(args.root.resolve(), args.manifest)
    manifest = v.artifact_json(result['manifest'], args.root.resolve())
    output = v.contained(manifest['outputs']['result'], args.root.resolve())
    access = output.with_name(output.name.removesuffix('.result.json') + '.access.json')
    store(access, {'phase': 'estimator_data_access', 'reads': sorted(reads)})


if __name__ == '__main__':
    main()
