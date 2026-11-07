"""Conjugate normal-inverse-Wishart BVARX(1) with a Minnesota-type prior.

Model (rows = time):  y_t' = y_{t-1}' A + x_t' C + e_t',  e_t ~ N(0, Sigma).
Stacked coefficients B = [A; C] with shape (k + m, k).
Prior: B | Sigma ~ MN(B0, Omega0, Sigma), Sigma ~ IW(S0, nu0) (Kadiyala-Karlsson).
"""
import numpy as np
from scipy.stats import invwishart


def ar1_variances(y):
    """Residual variance of a univariate AR(1) with intercept for every column."""
    out = []
    for j in range(y.shape[1]):
        z = np.column_stack([np.ones(len(y) - 1), y[:-1, j]])
        coef, *_ = np.linalg.lstsq(z, y[1:, j], rcond=None)
        resid = y[1:, j] - z @ coef
        out.append(resid @ resid / (len(resid) - 2))
    return np.array(out)


def fit(y, x, lam=0.2, delta=0.9, exog_scale=10.0):
    """Posterior hyperparameters for y (n x k) and exogenous x (n x m), lag 1.

    The first observation is the initial condition; x[0] is unused."""
    y, x = np.asarray(y, float), np.asarray(x, float)
    if np.isnan(y).any() or np.isnan(x).any():
        raise ValueError("Missing values are not allowed in the estimation window")
    n, k = y.shape
    m = x.shape[1]
    s2 = ar1_variances(y)
    Y = y[1:]
    Z = np.column_stack([y[:-1], x[1:]])
    sd = x[1:].std(axis=0)
    omega0 = np.concatenate([lam ** 2 / s2,
                             np.where(sd > 0, (exog_scale / np.where(sd > 0, sd, 1)) ** 2, exog_scale ** 2)])
    B0 = np.zeros((k + m, k))
    B0[:k, :k] = delta * np.eye(k)
    O0inv = np.diag(1 / omega0)
    Oninv = O0inv + Z.T @ Z
    On = np.linalg.inv(Oninv)
    On = (On + On.T) / 2
    Bn = On @ (O0inv @ B0 + Z.T @ Y)
    S0 = np.diag(s2)
    Sn = S0 + Y.T @ Y + B0.T @ O0inv @ B0 - Bn.T @ Oninv @ Bn
    Sn = (Sn + Sn.T) / 2
    return {"Bn": Bn, "On": On, "Sn": Sn, "nun": k + 2 + len(Y), "k": k, "m": m, "s2": s2,
            "lam": lam, "delta": delta}


def draw(post, ndraws, rng):
    """Exact joint posterior draws of (B, Sigma)."""
    k, km = post["k"], post["Bn"].shape[0]
    sig = invwishart(df=post["nun"], scale=post["Sn"]).rvs(size=ndraws, random_state=rng)
    sig = sig.reshape(ndraws, k, k)
    LO = np.linalg.cholesky(post["On"])
    Bs = np.empty((ndraws, km, k))
    for d in range(ndraws):
        LS = np.linalg.cholesky(sig[d])
        Bs[d] = post["Bn"] + LO @ rng.standard_normal((km, k)) @ LS.T
    return Bs, sig


def irf_first_shock(Bs, sig, horizon):
    """Responses to a one-SD recursive shock in variable 0 (h = 0..horizon)."""
    nd, _, k = Bs.shape
    out = np.empty((nd, horizon + 1, k))
    for d in range(nd):
        Phi = Bs[d, :k, :].T          # y_t = Phi y_{t-1} + ...
        impact = np.linalg.cholesky(sig[d])[:, 0]
        r = impact
        for h in range(horizon + 1):
            out[d, h] = r
            r = Phi @ r
    return out


def simulate(Bs, sig, y_last, x_future, rng):
    """Predictive paths (draws x horizon x k) given future exogenous rows."""
    nd, _, k = Bs.shape
    H = len(x_future)
    paths = np.empty((nd, H, k))
    for d in range(nd):
        Phi, C = Bs[d, :k, :].T, Bs[d, k:, :].T
        L = np.linalg.cholesky(sig[d])
        prev = y_last
        for h in range(H):
            prev = Phi @ prev + C @ x_future[h] + L @ rng.standard_normal(k)
            paths[d, h] = prev
    return paths
