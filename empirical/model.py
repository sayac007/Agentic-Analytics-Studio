"""Fixed observed-data comparison, as declared before fitting in workorder 03c."""
import numpy as np
from fuel_oil.scoped_study import fit_hac, json_safe
from .features import feature, verify_library
from .diagnostics import profile, residual_profile

NAMES = ('calendar', 'dynamic', 'macro', 'macro_diesel', 'macro_lag2', 'macro_diesel_lag2', 'macro_lag3', 'macro_diesel_lag3')


def matrices(data):
    series = {k: np.array([np.nan if x is None else x for x in v], dtype=float) for k, v in data['series'].items()}
    y = feature(np.log1p(series['tesla_count']), 'diff')
    months = np.array([int(p[5:]) for p in data['periods']])
    x = np.column_stack([np.ones(len(y))] + [(months == m).astype(float) for m in range(2, 13)])
    terms = ['intercept'] + [f'month_{m:02d}' for m in range(2, 13)]
    designs = {'calendar': (x, terms)}
    x = np.column_stack([x, feature(y, 'lag', 1)])
    terms = terms + ['target_change_lag1']
    designs['dynamic'] = (x, terms)
    dynamic_x, dynamic_terms = x, terms
    for lag in (1, 2, 3):
        x, terms = dynamic_x, list(dynamic_terms)
        suffix = '' if lag == 1 else f'_lag{lag}'
        for key in ('cpi', 'consumer_credit', 'eurusd'):
            values = series[key] if key == 'consumer_credit' else np.log(series[key])
            x = np.column_stack([x, feature(feature(values, 'diff'), 'lag', lag)])
            terms = terms + [key + f'_change_lag{lag}']
        designs['macro' + suffix] = (x, terms)
        designs['macro_diesel' + suffix] = (np.column_stack([x, feature(feature(np.log(series['diesel_de']), 'diff'), 'lag', lag)]),
                                            terms + [f'diesel_de_change_lag{lag}'])
    return y, designs


def metrics(actual, predicted, p=None):
    error = actual - predicted
    sst = float(np.sum((actual - np.mean(actual)) ** 2))
    r2 = None if sst == 0 else 1 - float(error @ error) / sst
    return {'n': len(actual), 'rmse': float(np.sqrt(np.mean(error**2))),
            'mae': float(np.mean(np.abs(error))), 'r2': r2,
            'adjusted_r2': None if p is None or r2 is None or len(actual) <= p else 1-(1-r2)*(len(actual)-1)/(len(actual)-p)}


def fit(y, x, names, mask, periods):
    idx = np.flatnonzero(mask)
    model = fit_hac(y[mask], x[mask], idx)
    predicted = x[mask] @ model['coefficients']
    return {'status': 'estimated', 'n': model['n'], 'rank': model['rank'], 'residual_df': model['residual_df'],
            'condition_number': model['condition_number'], 'terms': names,
            'coefficients': {name: {'estimate': model['coefficients'][i], 'standard_error': model['se'][i],
                                   'lower': model['ci95'][i, 0], 'upper': model['ci95'][i, 1]}
                             for i, name in enumerate(names)},
            'metrics': metrics(y[mask], predicted, len(names)),
            'periods': [periods[i] for i in idx], 'calendar_indices': idx,
            'predicted_change': predicted, 'residuals': model['residuals']}, model


def analyze(data):
    y, designs = matrices(data)
    indices = np.arange(len(y)); periods = data['periods']
    counts = np.array(data['series']['tesla_count'])
    outcome_stationarity = {'registrations_count': profile(counts, True),
                            'registrations_log1p': profile(np.log1p(counts), True),
                            'modeled_log1p_change': profile(y, False)}
    output = {}
    for name, (x, terms) in designs.items():
        eligible = np.isfinite(y) & np.isfinite(x).all(axis=1)
        train = eligible & (indices < 84)
        test = eligible & (indices >= 84)
        entry = {'eligible_periods': [p for p, ok in zip(periods, eligible) if ok],
                 'excluded_periods': [p for p, ok in zip(periods, eligible) if not ok]}
        try:
            full, _ = fit(y, x, terms, eligible, periods)
            fitted, model = fit(y, x, terms, train, periods)
            if not test.any():
                raise ValueError('No eligible fixed 2025 holdout months')
            pred = x[test] @ model['coefficients']
            with np.errstate(over='raise', invalid='raise'):
                pred_count = np.expm1(np.log1p(counts[indices[test]-1]) + pred)
            comparator = 'calendar' if name in ('calendar', 'dynamic') else 'dynamic'
            cx, cn = designs[comparator]
            paired_full, _ = fit(y, cx, cn, eligible, periods)
            paired_train, paired_model = fit(y, cx, cn, train, periods)
            cpred = cx[test] @ paired_model['coefficients']
            ccounts = np.expm1(np.log1p(counts[indices[test]-1]) + cpred)
            entry.update(status='estimated', full=full, training=fitted,
                stationarity={'training_residuals': residual_profile(fitted),
                              'full_residuals': residual_profile(full)},
                holdout={'label': 'RETROSPECTIVE_CONDITIONAL_ONE_MONTH_AHEAD_2025',
                         'periods': [p for p, ok in zip(periods, test) if ok],
                         'change_metrics': metrics(y[test], pred), 'count_metrics': metrics(counts[test], pred_count),
                         'observed_counts': counts[test], 'predicted_counts': pred_count,
                         'predicted_change': pred, 'negative_predictions': int(np.sum(pred_count < 0))},
                paired_comparator={'name': comparator, 'full_metrics': paired_full['metrics'],
                                   'training_metrics': paired_train['metrics'],
                                   'holdout_change_metrics': metrics(y[test], cpred),
                                   'holdout_count_metrics': metrics(counts[test], ccounts),
                                   'holdout_predicted_counts': ccounts})
        except (ValueError, FloatingPointError, np.linalg.LinAlgError) as exc:
            entry.update(status='not_estimable', reason=str(exc))
        if entry['status'] == 'estimated':
            supported = outcome_stationarity['modeled_log1p_change']['training_only']['verdict'] == 'supports_stationarity' and entry['stationarity']['training_residuals']['verdict'] == 'supports_stationarity'
            entry['model_assessment'] = 'diagnostic_support_only' if supported else 'stationarity_review_required'
        else:
            entry['stationarity'] = {'status': 'not_estimable', 'reason': 'No estimated residual series'}
        output[name] = entry
    peaks = []
    chosen = output['macro']
    if chosen['status'] == 'estimated':
        fit_result = chosen['training']
        scale = fit_result['metrics']['rmse']
        order = np.argsort(np.abs(fit_result['residuals']))[::-1][:8]
        for offset in order:
            month = fit_result['periods'][offset]
            t = periods.index(month)
            candidate_months = periods[max(0, t-3):t+1]
            peaks.append({'period': month, 'residual_change': fit_result['residuals'][offset],
                          'standardized_by_training_rmse': fit_result['residuals'][offset]/scale,
                          'search_months': candidate_months,
                          'documented_candidates': [e for e in data['events'] if e['date'][:7] in candidate_months],
                          'interpretation': 'Post-hoc research lead; candidate events are not causal explanations.'})
    return json_safe({'classification': 'OBSERVED_PRIVATE', 'target': 'monthly_change_log1p_registrations',
                      'models': output, 'residual_research': peaks,
                      'outcome_stationarity': outcome_stationarity, 'feature_library': verify_library(),
                      'limits': data['warnings'] + [
                          'Conditional associations, not identified promotion, launch or fuel-price effects.',
                          'HAC intervals are asymptotic and conditional; actual coverage is not validated.',
                          '2025 was previously examined in separate frozen research. This is not an untouched prospective test.',
                          'No best model selected. Shared exogenous lags 1/2/3 are prespecified; no variable, lag or significance search.',
                          'Stationarity diagnostics are mandatory but exploratory. Conflicting or inconclusive tests do not trigger automatic refits.',
                          'Launch/promotion records are evidence annotations, not zero-filled exposure regressors.']})
