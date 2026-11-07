"""Amendment 1.1.0: fuel price at lags 1..L (restricted VAR(L)), L = 1..4.

python -m multibrand.fuel_lags [--output results/multibrand_fuel_lags] [--draws 4000]
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.special import multigammaln

from . import bvar, data, study

ROOT = data.ROOT
PROTOCOL = ROOT / "docs/MULTIBRAND_FUEL_LAGS_PROTOCOL.md"
PROTOCOL_SHA256 = "035768d7b037037b6021c7309c011a39bb07fc7b75c696bbc9d30ed36dc7af98"
LAGS = (1, 2, 3, 4)
SPEC = study.SPECS["primary"]
BONF = 1 - 0.05 / len(LAGS)
FUEL_START = "2018-01"


def fuel_history(end):
    periods = data.months(FUEL_START, end)
    return dict(zip(periods, data.fuel(periods, SPEC["fuel"])))


def shift(period, back):
    y, m = map(int, period.split("-"))
    idx = y * 12 + m - 1 - back
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def regressors(periods, y, x, L, fuel):
    """Z rows for t = 1..n-1: [y_{t-1}, fuel_{t-2..t-L}, x_t]."""
    extra = np.array([[fuel[shift(p, l)] for l in range(2, L + 1)] for p in periods[1:]]).reshape(len(periods) - 1, L - 1)
    return np.column_stack([y[:-1], extra, x[1:]])


def fit(y, Z, L, lam=SPEC["lam"], delta=0.9, exog_scale=10.0):
    k = y.shape[1]
    s2 = bvar.ar1_variances(y)
    Y = y[1:]
    sd = Z[:, k + L - 1:].std(axis=0)
    omega0 = np.concatenate([
        lam ** 2 / s2,
        [lam ** 2 / (l ** 2 * s2[0]) for l in range(2, L + 1)],
        np.where(sd > 0, (exog_scale / np.where(sd > 0, sd, 1)) ** 2, exog_scale ** 2)])
    B0 = np.zeros((Z.shape[1], k))
    B0[:k, :k] = delta * np.eye(k)
    O0inv = np.diag(1 / omega0)
    Oninv = O0inv + Z.T @ Z
    On = np.linalg.inv(Oninv)
    On = (On + On.T) / 2
    Bn = On @ (O0inv @ B0 + Z.T @ Y)
    S0 = np.diag(s2)
    Sn = S0 + Y.T @ Y + B0.T @ O0inv @ B0 - Bn.T @ Oninv @ Bn
    Sn = (Sn + Sn.T) / 2
    nu0, T = k + 2, len(Y)
    nun = nu0 + T
    logml = (-T * k / 2 * np.log(np.pi) + multigammaln(nun / 2, k) - multigammaln(nu0 / 2, k)
             + nu0 / 2 * np.linalg.slogdet(S0)[1] - nun / 2 * np.linalg.slogdet(Sn)[1]
             + k / 2 * (np.linalg.slogdet(On)[1] - np.sum(np.log(omega0))))
    return {"Bn": Bn, "On": On, "Sn": Sn, "nun": nun, "k": k, "L": L, "logml": float(logml)}


def irf(Bs, sig, L, horizon=12):
    """Fuel-first recursive shock on the companion state [y_t, f_{t-1}..f_{t-L+1}]."""
    nd, _, k = Bs.shape
    out = np.empty((nd, horizon + 1, k))
    for d in range(nd):
        A, C = Bs[d, :k, :].T, Bs[d, k:k + L - 1, :].T  # C: k x (L-1)
        state_y = np.linalg.cholesky(sig[d])[:, 0]
        lags = np.zeros(L - 1)                              # f_{t-1}..f_{t-L+1} responses
        for h in range(horizon + 1):
            out[d, h] = state_y
            new_y = A @ state_y + (C @ lags if L > 1 else 0)
            if L > 1:
                lags = np.concatenate([[state_y[0]], lags[:-1]])
            state_y = new_y
    return out


def simulate(Bs, sig, y_last, fuel_lags, x_future, L, rng):
    """fuel_lags = [f_{T-1}, ..., f_{T-L+1}] at the origin T."""
    nd, _, k = Bs.shape
    paths = np.empty((nd, len(x_future), k))
    for d in range(nd):
        A, C, X = Bs[d, :k, :].T, Bs[d, k:k + L - 1, :].T, Bs[d, k + L - 1:, :].T
        Lc = np.linalg.cholesky(sig[d])
        prev, lags = y_last, np.array(fuel_lags, float)
        for h in range(len(x_future)):
            new = A @ prev + (C @ lags if L > 1 else 0) + X @ x_future[h] + Lc @ rng.standard_normal(k)
            if L > 1:
                lags = np.concatenate([[prev[0]], lags[:-1]])
            prev = new
            paths[d, h] = new
    return paths


def interval(draws, level):
    a = (1 - level) / 2
    return np.quantile(draws, [0.5, a, 1 - a], axis=0)


def full_sample(L, ndraws, rng, fuel):
    periods = data.months(SPEC["start"], study.END)
    _, y, x, names = study.build(periods, SPEC)
    Z = regressors(periods, y, x, L, fuel)
    post = fit(y, Z, L)
    Bs, sig = bvar.draw(post, ndraws, rng)
    k = y.shape[1]
    rows = []
    fuel_rows = [0] + [k + l - 2 for l in range(2, L + 1)]       # row index of fuel lag 1..L
    for i, eq in enumerate(data.ENDOGENOUS):
        draws_by_lag = [Bs[:, r, i] for r in fuel_rows]
        for lag, dr in enumerate(draws_by_lag, start=1):
            rows.append(lag_row(L, eq, f"fuel_lag{lag}", dr))
        rows.append(lag_row(L, eq, "fuel_lag_sum", np.sum(draws_by_lag, axis=0)))
    resp = irf(Bs, sig, L)
    irf_rows = [lag_row(L, var, "cum_irf_0_11", resp[:, :12, i].sum(axis=1)) for i, var in enumerate(data.ENDOGENOUS)]
    return post, rows, irf_rows, resp


def lag_row(L, eq, term, draws):
    m, lo, hi = interval(draws, 0.95)
    _, blo, bhi = interval(draws, BONF)
    return dict(L=L, equation=eq, term=term, median=float(m), lower95=float(lo), upper95=float(hi),
                lower_bonf=float(blo), upper_bonf=float(bhi), excludes_zero_95=bool(lo > 0 or hi < 0),
                excludes_zero_bonf=bool(blo > 0 or bhi < 0))


def forecasts(L, ndraws, rng, fuel):
    all_periods = data.months("2021-01", study.LAST_TARGET)
    actual = {r["period"]: r for r in data.counts(all_periods)}
    rows = []
    for origin in data.months("2024-12", study.END):
        train = data.months(SPEC["start"], origin)
        _, y, x, _ = study.build(train, SPEC)
        post = fit(y, regressors(train, y, x, L, fuel), L)
        Bs, sig = bvar.draw(post, ndraws, rng)
        idx = all_periods.index(origin)
        future = all_periods[idx + 1: idx + 4]
        last = data.prices((origin,))
        fx, _ = study.exog(train + future, SPEC, origin=origin,
                           price_rows=np.vstack([data.prices(train), np.repeat(last, len(future), axis=0)]))
        lags = [fuel[shift(origin, l)] for l in range(1, L)]
        paths = simulate(Bs, sig, y[-1], lags, fx[len(train):], L, rng)
        market, groups = study.to_counts(paths)
        for h, target in enumerate(future, start=1):
            if h not in (1, 3):
                continue
            for outcome, dr in (("BEV_market", market[:, h - 1]), ("Tesla", groups[:, h - 1, 0])):
                med, lo, hi = np.quantile(dr, [0.5, 0.025, 0.975])
                act = actual[target]["market" if outcome == "BEV_market" else outcome]
                rows.append(dict(spec=f"L{L}", origin=origin, target=target, year=target[:4], horizon=h,
                                 outcome=outcome, actual=act, prediction_median=float(med), lower95=float(lo),
                                 upper95=float(hi), error=float(med - act)))
    return rows


def verdict(lo, hi):
    return "supported" if lo > 0 else "weakened" if hi < 0 else "open"


def run(output, ndraws):
    proto = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if proto != PROTOCOL_SHA256:
        raise SystemExit("Amendment bytes differ from the frozen version; refusing to run")
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    fuel = fuel_history(study.END)
    rng = np.random.default_rng(study.SEED)
    coef, irfs, ml, fc, hyp = [], [], [], [], []
    for L in LAGS:
        post, c, i, _ = full_sample(L, ndraws, rng, fuel)
        coef += c
        irfs += i
        ml.append(dict(L=L, log_marginal_likelihood=post["logml"], regressors_per_equation=post["Bn"].shape[0]))
        fc += forecasts(L, ndraws, rng, fuel)
        ir = {r["equation"]: r for r in i}
        for label, var in (("H-F market", "log_market"), ("H-F Tesla share", "alr_Tesla")):
            r = ir[var]
            hyp.append(dict(L=L, hypothesis=label, median=r["median"], lower95=r["lower95"], upper95=r["upper95"],
                            lower_bonf=r["lower_bonf"], upper_bonf=r["upper_bonf"],
                            verdict=verdict(r["lower95"], r["upper95"])))
    for label in ("H-F market", "H-F Tesla share"):
        sel = [h for h in hyp if h["hypothesis"] == label]
        robust = any(h["lower_bonf"] > 0 for h in sel) and not any(h["upper95"] < 0 for h in sel)
        hyp.append(dict(L="all", hypothesis=label + " across lags", median="", lower95="", upper95="",
                        lower_bonf="", upper_bonf="",
                        verdict="supported across lags" if robust else "not robust to lag choice"))
    targets = {(r["target"], r["horizon"]) for r in fc}
    base = [r for r in study.comparators(targets) if r["spec"] == "M2" and (r["target"], r["horizon"]) in targets]
    met = study.metrics(fc + base)
    for name, rows in (("lag_coefficients.csv", coef), ("irf_cumulative.csv", irfs), ("marginal_likelihood.csv", ml),
                       ("predictions.csv", fc), ("metrics.csv", met), ("hypotheses.csv", hyp)):
        study.write_csv(out / name, rows)
    files = {n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in
             ("lag_coefficients.csv", "irf_cumulative.csv", "marginal_likelihood.csv", "predictions.csv",
              "metrics.csv", "hypotheses.csv")}
    code = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "multibrand").glob("*.py"))}
    manifest = dict(protocol="multibrand-bvarx/1.1.0-fuel-lags", protocol_sha256=proto, seed=study.SEED,
                    draws=ndraws, lags=list(LAGS), bonferroni_level=BONF, outcome_months="2021-02..2026-09",
                    inputs_sha256=data.inputs_sha256(), code_sha256=code, outputs_sha256=files,
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--output", default="results/multibrand_fuel_lags")
    p.add_argument("--draws", type=int, default=4000)
    a = p.parse_args()
    m = run(a.output, a.draws)
    print(json.dumps({k: m[k] for k in ("protocol", "draws", "outputs_sha256")}, indent=2))
