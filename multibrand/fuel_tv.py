"""Amendment 1.2.0: time-varying fuel coefficient at lag 1, b(t) = b0 + b1 * g(t).

python -m multibrand.fuel_tv [--output results/multibrand_fuel_tv] [--draws 4000]
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.special import multigammaln

from . import bvar, data, study

ROOT = data.ROOT
PROTOCOL = ROOT / "docs/MULTIBRAND_FUEL_TV_PROTOCOL.md"
PROTOCOL_SHA256 = "23d090131f3f7d1d02e3b3998bd77ce753febecdd4661ef5f6154223679abb60"
SPEC = study.SPECS["primary"]
LAM = SPEC["lam"]
VARIANTS = {
    "tv_linear": dict(g="linear", prior_mult=1.0),
    "tv_linear_loose": dict(g="linear", prior_mult=25.0),
    "tv_step_2024": dict(g="step", prior_mult=1.0),
}
REPORT_MONTHS = ("2021-06", "2022-06", "2023-06", "2024-06", "2025-06", "2026-09")


def months_since_start(period):
    y, m = map(int, period.split("-"))
    return (y - 2021) * 12 + m - 1


def g(period, kind):
    if kind == "linear":
        return (months_since_start(period) - 34.5) / 12
    if kind == "step":
        return float(period >= "2024-01")
    raise ValueError(kind)


def fit(y, x, gvals, prior_mult, lam=LAM, delta=0.9, exog_scale=10.0):
    """Posterior with Z_t = [y_{t-1}, g(t) * fuel_{t-1}, x_t]; gvals=None -> base model."""
    k = y.shape[1]
    s2 = bvar.ar1_variances(y)
    Y = y[1:]
    cols, var = [y[:-1]], list(lam ** 2 / s2)
    if gvals is not None:
        cols.append((np.asarray(gvals)[1:] * y[:-1, 0])[:, None])
        var.append(prior_mult * lam ** 2 / s2[0])
    sd = x[1:].std(axis=0)
    var += list(np.where(sd > 0, (exog_scale / np.where(sd > 0, sd, 1)) ** 2, exog_scale ** 2))
    Z = np.column_stack(cols + [x[1:]])
    omega0 = np.array(var)
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
    return {"Bn": Bn, "On": On, "Sn": Sn, "nun": nun, "k": k, "logml": float(logml),
            "tv": gvals is not None}


def simulate(Bs, sig, y_last, x_future, g_future, rng):
    nd, _, k = Bs.shape
    paths = np.empty((nd, len(x_future), k))
    for d in range(nd):
        A, c, X = Bs[d, :k, :].T, Bs[d, k, :], Bs[d, k + 1:, :].T
        L = np.linalg.cholesky(sig[d])
        prev = y_last
        for h in range(len(x_future)):
            prev = A @ prev + c * g_future[h] * prev[0] + X @ x_future[h] + L @ rng.standard_normal(k)
            paths[d, h] = prev
    return paths


def q(draws):
    return np.quantile(draws, [0.5, 0.025, 0.975])


def full_sample(name, variant, ndraws, rng):
    periods = data.months(SPEC["start"], study.END)
    _, y, x, _ = study.build(periods, SPEC)
    gv = [g(p, variant["g"]) for p in periods]
    post = fit(y, x, gv, variant["prior_mult"])
    Bs, sig = bvar.draw(post, ndraws, rng)
    k = y.shape[1]
    coef, path = [], []
    for i, eq in enumerate(data.ENDOGENOUS):
        b0, b1 = Bs[:, 0, i], Bs[:, k, i]
        for term, dr in (("b0_fuel_lag1", b0), ("b1_time_interaction", b1)):
            m, lo, hi = q(dr)
            coef.append(dict(variant=name, equation=eq, term=term, median=float(m), lower95=float(lo),
                             upper95=float(hi), excludes_zero=bool(lo > 0 or hi < 0)))
        if eq in ("log_market", "alr_Tesla"):
            for p in REPORT_MONTHS:
                m, lo, hi = q(b0 + b1 * g(p, variant["g"]))
                path.append(dict(variant=name, equation=eq, month=p, g=g(p, variant["g"]),
                                 coefficient_median=float(m), lower95=float(lo), upper95=float(hi)))
    return post, coef, path


def forecasts(name, variant, ndraws, rng):
    all_periods = data.months("2021-01", study.LAST_TARGET)
    actual = {r["period"]: r for r in data.counts(all_periods)}
    rows = []
    for origin in data.months("2024-12", study.END):
        train = data.months(SPEC["start"], origin)
        _, y, x, _ = study.build(train, SPEC)
        post = fit(y, x, [g(p, variant["g"]) for p in train], variant["prior_mult"])
        Bs, sig = bvar.draw(post, ndraws, rng)
        idx = all_periods.index(origin)
        future = all_periods[idx + 1: idx + 4]
        last = data.prices((origin,))
        fx, _ = study.exog(train + future, SPEC, origin=origin,
                           price_rows=np.vstack([data.prices(train), np.repeat(last, len(future), axis=0)]))
        paths = simulate(Bs, sig, y[-1], fx[len(train):], [g(p, variant["g"]) for p in future], rng)
        market, groups = study.to_counts(paths)
        for h, target in enumerate(future, start=1):
            if h not in (1, 3):
                continue
            for outcome, dr in (("BEV_market", market[:, h - 1]), ("Tesla", groups[:, h - 1, 0])):
                med, lo, hi = np.quantile(dr, [0.5, 0.025, 0.975])
                act = actual[target]["market" if outcome == "BEV_market" else outcome]
                rows.append(dict(spec=name, origin=origin, target=target, year=target[:4], horizon=h,
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
    rng = np.random.default_rng(study.SEED)
    periods = data.months(SPEC["start"], study.END)
    _, y, x, _ = study.build(periods, SPEC)
    ml = [dict(variant="constant (base, 1.1.0 L1)", log_marginal_likelihood=fit(y, x, None, 1.0)["logml"])]
    coef, path, fc, hyp = [], [], [], []
    for name, variant in VARIANTS.items():
        post, c, pth = full_sample(name, variant, ndraws, rng)
        coef += c
        path += pth
        ml.append(dict(variant=name, log_marginal_likelihood=post["logml"]))
        fc += forecasts(name, variant, ndraws, rng)
        by = {(r["equation"], r["term"]): r for r in c}
        for label, eq in (("H-TV market", "log_market"), ("H-TV Tesla share", "alr_Tesla")):
            r = by[(eq, "b1_time_interaction")]
            hyp.append(dict(variant=name, hypothesis=label, median=r["median"], lower95=r["lower95"],
                            upper95=r["upper95"], verdict=verdict(r["lower95"], r["upper95"])))
    targets = {(r["target"], r["horizon"]) for r in fc}
    comp = [r for r in study.comparators(targets) if r["spec"] == "M2" and (r["target"], r["horizon"]) in targets]
    import csv
    with (ROOT / "results/multibrand_fuel_lags/predictions.csv").open(newline="") as fh:
        base = [dict(r, spec="constant_L1", horizon=int(r["horizon"]), error=float(r["error"]))
                for r in csv.DictReader(fh) if r["spec"] == "L1"]
    met = study.metrics(fc + comp + base)
    for fname, rows in (("coefficients.csv", coef), ("coefficient_path.csv", path), ("marginal_likelihood.csv", ml),
                        ("predictions.csv", fc), ("metrics.csv", met), ("hypotheses.csv", hyp)):
        study.write_csv(out / fname, rows)
    files = {n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in
             ("coefficients.csv", "coefficient_path.csv", "marginal_likelihood.csv", "predictions.csv",
              "metrics.csv", "hypotheses.csv")}
    code = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "multibrand").glob("*.py"))}
    manifest = dict(protocol="multibrand-bvarx/1.2.0-fuel-tv", protocol_sha256=proto, seed=study.SEED,
                    draws=ndraws, variants=VARIANTS, outcome_months="2021-02..2026-09",
                    inputs_sha256=data.inputs_sha256(), code_sha256=code, outputs_sha256=files,
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--output", default="results/multibrand_fuel_tv")
    p.add_argument("--draws", type=int, default=4000)
    a = p.parse_args()
    m = run(a.output, a.draws)
    print(json.dumps({k: m[k] for k in ("protocol", "draws", "outputs_sha256")}, indent=2))
