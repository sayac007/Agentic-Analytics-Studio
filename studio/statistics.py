"""Fixed-design OLS and conditional Newey-West/Bartlett uncertainty."""
import numpy as np
from .transforms import finite, media_feature

NORMAL_95 = 1.959963984540054


def design(periods, spend, specification):
    months = np.array([int(period[5:]) for period in periods])
    origin = int(periods[0][:4]) * 12 + int(periods[0][5:])
    trend = np.array([int(p[:4]) * 12 + int(p[5:]) - origin for p in periods], dtype=float)
    columns = [np.ones(len(periods)), trend,
               np.sin(2*np.pi*(months-1)/12), np.cos(2*np.pi*(months-1)/12),
               media_feature(spend, specification['parameters'])]
    names = ['intercept', 'trend', 'annual_sin_1', 'annual_cos_1', 'media']
    if specification['controls']['include_quarter_end']:
        names.append('quarter_end')
        columns.append(np.isin(months, [3, 6, 9, 12]).astype(float))
    for change in specification['controls']['structural_breaks']:
        names.append('break:' + change['id'])
        columns.append(np.array([p >= change['start'] for p in periods], dtype=float))
    return finite(np.column_stack(columns)), names


def ols_hac(X, y, max_lags=3):
    X, y = finite(X), finite(y)
    if X.ndim != 2 or y.shape != (len(X),):
        raise ValueError('Invalid design/target dimensions')
    n, p = X.shape
    if n <= p or not isinstance(max_lags, int) or not 0 <= max_lags < n:
        raise ValueError('Positive residual df and valid HAC lag count required')
    coefficients, _, rank, _ = np.linalg.lstsq(X, y, rcond=None)
    if rank != p:
        raise ValueError('Rank-deficient training design')
    scales = X[:, 1:].std(axis=0, ddof=1)
    if np.any(scales <= 0):
        raise ValueError('Zero-variance training regressor')
    scaled = np.column_stack([X[:, 0], (X[:, 1:] - X[:, 1:].mean(axis=0))/scales])
    condition = float(np.linalg.cond(scaled))
    residuals = y - X @ coefficients
    scores = X * residuals[:, None]
    meat = scores.T @ scores
    for lag in range(1, max_lags + 1):
        cross = scores[lag:].T @ scores[:-lag]
        meat += (1 - lag/(max_lags+1)) * (cross + cross.T)
    bread = np.linalg.solve(X.T @ X, np.eye(p))
    covariance = bread @ meat @ bread * (n/(n-p))
    covariance = (covariance + covariance.T)/2
    finite(coefficients)
    finite(covariance)
    if not np.isfinite(condition) or np.any(np.diag(covariance) < 0):
        raise ValueError('Invalid condition diagnostic or HAC variance')
    return coefficients, covariance, int(rank), condition


def interval(estimate, standard_error):
    finite([estimate, standard_error])
    if standard_error < 0:
        raise ValueError('Negative standard error')
    return {'estimate': float(estimate), 'standard_error': float(standard_error),
            'lower': float(estimate - NORMAL_95*standard_error),
            'upper': float(estimate + NORMAL_95*standard_error), 'confidence_level': .95}


def metrics(actual, predicted):
    residual = finite(actual) - finite(predicted)
    return {'n': len(residual), 'mae': float(np.mean(np.abs(residual))),
            'rmse': float(np.sqrt(np.mean(residual**2)))}
