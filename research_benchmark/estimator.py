"""Estimator-only batch FWL/QR OLS; no generator, reference or truth imports."""
import numpy as np


def estimate(y, h, include_quarter):
    y, h = np.asarray(y, dtype=float), np.asarray(h, dtype=float)
    if y.ndim != 2 or y.shape != h.shape or y.shape[1] != 72:
        raise ValueError('Expected matching seed x 72 estimator arrays')
    if not np.isfinite(y).all() or not np.isfinite(h).all():
        raise ValueError('Nonfinite estimator inputs')
    t = np.arange(60)
    columns = [np.ones(60), t, np.sin(2*np.pi*t/12), np.cos(2*np.pi*t/12)]
    if include_quarter:
        columns.append(((t+1) % 3 == 0).astype(float))
    c = np.column_stack(columns)
    q, _ = np.linalg.qr(c, mode='reduced')
    yt, ht = y[:, :60], h[:, :60]
    v = ht - (ht @ q) @ q.T
    yr = yt - (yt @ q) @ q.T
    denominator = np.sum(v*v, axis=1)
    valid = denominator > 1e-20
    beta = np.full(len(y), np.nan)
    np.divide(np.sum(v*yr, axis=1), denominator, out=beta, where=valid)
    residual = yr-beta[:, None]*v
    scores = v*residual
    meat = np.sum(scores*scores, axis=1)
    for lag in range(1, 4):
        meat += 2*(1-lag/4)*np.sum(scores[:, lag:]*scores[:, :-lag], axis=1)
    variance = np.full(len(y), np.nan)
    np.divide(meat * (60/(60-c.shape[1]-1)), denominator**2, out=variance, where=valid)
    valid &= np.isfinite(variance) & (variance >= 0)
    se = np.sqrt(np.maximum(variance, 0))
    beta[~valid], se[~valid] = np.nan, np.nan
    reason = np.where(valid, '', 'rank_deficient_or_invalid_variance')
    return dict(beta=beta, se=se, valid=valid, reason=reason)


def main():
    # Bootstrap only NumPy, then apply the existing data-access guard in a new cwd.
    from isolation import guard
    from pathlib import Path
    guard(Path('.').resolve())
    with np.load('safe.npz', allow_pickle=False) as data:
        result = {}
        for include, name in [(True, 'with-quarter'), (False, 'without-quarter')]:
            for key, value in estimate(data['y'], data['h'], include).items():
                result[name+'__'+key] = value
    np.savez('fit.npz', **result)


if __name__ == '__main__':
    main()
