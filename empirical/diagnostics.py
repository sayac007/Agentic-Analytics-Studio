"""Mandatory fixed stationarity diagnostics; no automated specification search."""
import numpy as np
from fuel_oil.scoped_study import diagnostics as fixed_diagnostics


def check(values, levels=False, residuals=False):
    result = fixed_diagnostics(np.asarray(values, dtype=float), levels)
    if result['status'] != 'estimated':
        result['verdict'] = 'not_estimable'
    else:
        adf_reject = result['adf']['pvalue'] < .05
        kpss_reject = result['kpss']['pvalue'] < .05
        result['verdict'] = ('supports_stationarity' if adf_reject and not kpss_reject else
                             'evidence_against_stationarity' if not adf_reject and kpss_reject else
                             'conflicting' if adf_reject and kpss_reject else 'inconclusive')
    if result['status'] == 'estimated':
        warnings_text = ' '.join(result.get('warnings', [])).lower()
        pv = result['kpss']['pvalue']
        result['kpss']['pvalue_bound'] = '>' if pv == .1 and 'greater' in warnings_text else '<' if pv == .01 and 'smaller' in warnings_text else None
    result['assessment'] = 'Diagnostic evidence only; no proof of stationarity or automatic model acceptance.'
    if residuals:
        result['assessment'] += ' Residuals are estimated by regression: ordinary ADF/KPSS p-values are exploratory, not a calibrated residual cointegration test. Stationary does not mean white noise.'
    return result


def profile(values, levels=False):
    array = np.asarray(values, dtype=float)
    training = array.copy(); training[84:] = np.nan
    return {'training_only': check(training, levels), 'retrospective_full': check(array, levels)}


def residual_profile(fit, size=96):
    # Do not concatenate irregular complete cases: preserve their calendar positions.
    array = np.full(size, np.nan)
    array[np.asarray(fit['calendar_indices'], dtype=int)] = fit['residuals']
    return check(array, residuals=True)
