"""Amendment 1.2.1: time-varying fuel coefficient with its trend main effect.

python -m multibrand.fuel_tv_trend [--output results/multibrand_fuel_tv_trend] [--draws 4000]
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from . import bvar, data, fuel_tv, study

ROOT = data.ROOT
PROTOCOL = ROOT / "docs/MULTIBRAND_FUEL_TV_TREND_PROTOCOL.md"
PROTOCOL_SHA256 = "1842323cb5f40152b50be1d07a7dcfc0cbc7c41f5d4151295ca74a1e384a9c26"
SPEC = study.SPECS["primary"]
VARIANTS = {
    "trend_only": dict(interaction=False, prior_mult=1.0),
    "tv_linear_trend": dict(interaction=True, prior_mult=1.0),
    "tv_linear_trend_loose": dict(interaction=True, prior_mult=25.0),
}


def tau(periods):
    return np.array([fuel_tv.g(p, "linear") for p in periods])


def augmented(periods, x):
    return np.column_stack([x, tau(periods)])


def fit(y, x_aug, periods, variant):
    return fuel_tv.fit(y, x_aug, list(tau(periods)) if variant["interaction"] else None, variant["prior_mult"])


def full_sample(name, variant, ndraws, rng):
    periods = data.months(SPEC["start"], study.END)
    _, y, x, _ = study.build(periods, SPEC)
    post = fit(y, augmented(periods, x), periods, variant)
    Bs, sig = bvar.draw(post, ndraws, rng)
    k = y.shape[1]
    coef, path = [], []
    for i, eq in enumerate(data.ENDOGENOUS):
        terms = [("b0_fuel_lag1", Bs[:, 0, i]), ("trend_tau", Bs[:, -1, i])]
        if variant["interaction"]:
            terms.append(("b1_time_interaction", Bs[:, k, i]))
        for term, dr in terms:
            m, lo, hi = fuel_tv.q(dr)
            coef.append(dict(variant=name, equation=eq, term=term, median=float(m), lower95=float(lo),
                             upper95=float(hi), excludes_zero=bool(lo > 0 or hi < 0)))
        if eq in ("log_market", "alr_Tesla"):
            for p in fuel_tv.REPORT_MONTHS:
                b = Bs[:, 0, i] + (Bs[:, k, i] * fuel_tv.g(p, "linear") if variant["interaction"] else 0)
                m, lo, hi = fuel_tv.q(b)
                path.append(dict(variant=name, equation=eq, month=p, g=fuel_tv.g(p, "linear"),
                                 coefficient_median=float(m), lower95=float(lo), upper95=float(hi)))
    return post, coef, path


def forecasts(name, variant, ndraws, rng):
    all_periods = data.months("2021-01", study.LAST_TARGET)
    actual = {r["period"]: r for r in data.counts(all_periods)}
    rows = []
    for origin in data.months("2024-12", study.END):
        train = data.months(SPEC["start"], origin)
        _, y, x, _ = study.build(train, SPEC)
        post = fit(y, augmented(train, x), train, variant)
        Bs, sig = bvar.draw(post, ndraws, rng)
        idx = all_periods.index(origin)
        future = all_periods[idx + 1: idx + 4]
        last = data.prices((origin,))
        fx, _ = study.exog(train + future, SPEC, origin=origin,
                           price_rows=np.vstack([data.prices(train), np.repeat(last, len(future), axis=0)]))
        fx = augmented(train + future, fx)[len(train):]
        if variant["interaction"]:
            paths = fuel_tv.simulate(Bs, sig, y[-1], fx, list(tau(future)), rng)
        else:
            paths = bvar.simulate(Bs, sig, y[-1], fx, rng)
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


def run(output, ndraws):
    proto = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if proto != PROTOCOL_SHA256:
        raise SystemExit("Amendment bytes differ from the frozen version; refusing to run")
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(study.SEED)
    periods = data.months(SPEC["start"], study.END)
    _, y, x, _ = study.build(periods, SPEC)
    ml = [dict(variant="constant (base, 1.1.0 L1)", log_marginal_likelihood=fuel_tv.fit(y, x, None, 1.0)["logml"])]
    coef, path, fc, hyp = [], [], [], []
    for name, variant in VARIANTS.items():
        post, c, pth = full_sample(name, variant, ndraws, rng)
        coef += c
        path += pth
        ml.append(dict(variant=name, log_marginal_likelihood=post["logml"]))
        fc += forecasts(name, variant, ndraws, rng)
        if variant["interaction"]:
            by = {(r["equation"], r["term"]): r for r in c}
            for label, eq in (("H-TV market", "log_market"), ("H-TV Tesla share", "alr_Tesla")):
                r = by[(eq, "b1_time_interaction")]
                hyp.append(dict(variant=name, hypothesis=label, median=r["median"], lower95=r["lower95"],
                                upper95=r["upper95"], verdict=fuel_tv.verdict(r["lower95"], r["upper95"])))
    targets = {(r["target"], r["horizon"]) for r in fc}
    comp = [r for r in study.comparators(targets) if r["spec"] == "M2" and (r["target"], r["horizon"]) in targets]
    with (ROOT / "results/multibrand_fuel_lags/predictions.csv").open(newline="") as fh:
        base = [dict(r, spec="constant_L1", horizon=int(r["horizon"]), error=float(r["error"]))
                for r in csv.DictReader(fh) if r["spec"] == "L1"]
    met = study.metrics(fc + comp + base)
    names = ("coefficients.csv", "coefficient_path.csv", "marginal_likelihood.csv", "predictions.csv",
             "metrics.csv", "hypotheses.csv")
    for fname, rows in zip(names, (coef, path, ml, fc, met, hyp)):
        study.write_csv(out / fname, rows)
    code = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "multibrand").glob("*.py"))}
    manifest = dict(protocol="multibrand-bvarx/1.2.1-fuel-tv-trend", protocol_sha256=proto, seed=study.SEED,
                    draws=ndraws, variants=VARIANTS, outcome_months="2021-02..2026-09",
                    inputs_sha256=data.inputs_sha256(), code_sha256=code,
                    outputs_sha256={n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in names},
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--output", default="results/multibrand_fuel_tv_trend")
    p.add_argument("--draws", type=int, default=4000)
    a = p.parse_args()
    m = run(a.output, a.draws)
    print(json.dumps({k: m[k] for k in ("protocol", "draws", "outputs_sha256")}, indent=2))
