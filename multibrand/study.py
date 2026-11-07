"""Run the frozen multi-brand BVARX protocol and write results/multibrand/.

python -m multibrand.study [--output results/multibrand] [--draws 4000]
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from regimes.data import calendars
from . import bvar, data

ROOT = data.ROOT
PROTOCOL = ROOT / "docs/MULTIBRAND_BVAR_PROTOCOL.md"
PROTOCOL_SHA256 = "e33dd45d93e29a0c5dfcae3de0f8078a94d38540fc3fb83f8052144427f0c432"
SEED = 20261107
SPECS = {
    "primary": dict(lam=0.2, fuel="euro95_bulletin_mean_eur_per_litre", start="2021-01", prices=True, forecast=True),
    "lambda_0.1": dict(lam=0.1, fuel="euro95_bulletin_mean_eur_per_litre", start="2021-01", prices=True, forecast=True),
    "lambda_0.5": dict(lam=0.5, fuel="euro95_bulletin_mean_eur_per_litre", start="2021-01", prices=True, forecast=True),
    "no_prices": dict(lam=0.2, fuel="euro95_bulletin_mean_eur_per_litre", start="2021-01", prices=False, forecast=True),
    "fuel_calendar_day": dict(lam=0.2, fuel="euro95_eur_per_litre", start="2022-05", prices=True, forecast=False),
}
END = "2026-09"
LAST_TARGET = "2026-10"
IRF_H = 12
GROUP_NAMES = tuple(data.GROUPS)


def build(periods, spec):
    counts = data.counts(periods)
    y = np.column_stack([data.fuel(periods, spec["fuel"]), np.log([r["market"] for r in counts])]
                        + [np.log([r[g] / r["Rest"] for r in counts]) for g in GROUP_NAMES])
    x, names = exog(periods, spec, origin=None)
    return counts, y, x, names


def exog(periods, spec, origin=None, price_rows=None):
    pol = data.policy(periods, origin)
    pr = data.prices(periods) if price_rows is None else price_rows
    cols = [np.ones(len(periods)), calendars(periods), pol]
    names = list(data.EXOGENOUS[:5]) + list(data.POLICY)
    if spec["prices"]:
        cols.append(pr)
        names += list(data.PRICES)
    return np.column_stack(cols), names


def summarize(draws_2d):
    q = np.quantile(draws_2d, [0.5, 0.025, 0.975], axis=0)
    return q[0], q[1], q[2]


def to_counts(paths):
    """paths[..., k] -> market and group counts."""
    market = np.exp(paths[..., 1])
    e = np.exp(paths[..., 2:])
    shares = e / (1 + e.sum(axis=-1, keepdims=True))
    return market, market[..., None] * shares


def full_sample(name, spec, ndraws, rng):
    periods = data.months(spec["start"], END)
    _, y, x, names = build(periods, spec)
    post = bvar.fit(y, x, lam=spec["lam"])
    Bs, sig = bvar.draw(post, ndraws, rng)
    k = y.shape[1]
    coef_rows = []
    for j, term in enumerate(names):
        med, lo, hi = summarize(Bs[:, k + j, :])
        for i, eq in enumerate(data.ENDOGENOUS):
            coef_rows.append(dict(spec=name, equation=eq, term=term, median=med[i], lower95=lo[i], upper95=hi[i],
                                  excludes_zero=bool(lo[i] > 0 or hi[i] < 0)))
    for i, eq in enumerate(data.ENDOGENOUS):          # lag matrix too, for completeness
        for j, lagged in enumerate(data.ENDOGENOUS):
            med, lo, hi = summarize(Bs[:, j, i])
            coef_rows.append(dict(spec=name, equation=eq, term=f"lag1:{lagged}", median=float(med), lower95=float(lo),
                                  upper95=float(hi), excludes_zero=bool(lo > 0 or hi < 0)))
    irf = bvar.irf_first_shock(Bs, sig, IRF_H)
    irf_rows = []
    for i, var in enumerate(data.ENDOGENOUS):
        for h in range(IRF_H + 1):
            med, lo, hi = summarize(irf[:, h, i])
            irf_rows.append(dict(spec=name, variable=var, h=h, median=float(med), lower95=float(lo), upper95=float(hi)))
        cum = irf[:, :12, i].sum(axis=1)
        med, lo, hi = summarize(cum)
        irf_rows.append(dict(spec=name, variable=var, h="cum_0_11", median=float(med), lower95=float(lo), upper95=float(hi)))
    fuel_sd = float(np.median(np.sqrt(sig[:, 0, 0])))
    return dict(n=len(periods), periods=(periods[0], periods[-1]), coef=coef_rows, irf=irf_rows, fuel_shock_sd=fuel_sd)


def forecasts(name, spec, ndraws, rng):
    all_periods = data.months("2021-01", LAST_TARGET)
    actual = {r["period"]: r for r in data.counts(all_periods)}
    rows = []
    for origin in data.months("2024-12", END):
        train = data.months(spec["start"], origin)
        _, y, x, _ = build(train, spec)
        post = bvar.fit(y, x, lam=spec["lam"])
        Bs, sig = bvar.draw(post, ndraws, rng)
        idx = all_periods.index(origin)
        future = all_periods[idx + 1: idx + 4]
        last_prices = data.prices((origin,))
        fx, _ = exog(train + future, spec, origin=origin,
                     price_rows=np.vstack([data.prices(train), np.repeat(last_prices, len(future), axis=0)]))
        paths = bvar.simulate(Bs, sig, y[-1], fx[len(train):], rng)
        market, groups = to_counts(paths)
        for h, target in enumerate(future, start=1):
            if h not in (1, 3):
                continue
            for outcome, draws_h in (("BEV_market", market[:, h - 1]), ("Tesla", groups[:, h - 1, 0]),
                                     ("VW_Group", groups[:, h - 1, 1])):
                med, lo, hi = np.quantile(draws_h, [0.5, 0.025, 0.975])
                act = actual[target]["market" if outcome == "BEV_market" else outcome]
                rows.append(dict(spec=name, origin=origin, target=target, year=target[:4], horizon=h, outcome=outcome,
                                 actual=act, prediction_median=float(med), lower95=float(lo), upper95=float(hi),
                                 error=float(med - act)))
    return rows


def comparators(targets):
    """Task 04 M0/M2 and seasonal-naive predictions on the same targets."""
    out = []
    with (ROOT / "results/task04/stage1/predictions.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["model"] in ("M0", "M2") and r["outcome"] in ("Tesla", "BEV_market"):
                out.append(dict(spec=r["model"], target=r["target"], horizon=int(r["horizon"]), outcome=r["outcome"],
                                actual=float(r["actual"]), prediction_median=float(r["prediction_mean"]),
                                error=float(r["error"])))
    periods = data.months("2021-01", LAST_TARGET)
    actual = {r["period"]: r for r in data.counts(periods)}
    for target, h in sorted(targets):
        y, m = map(int, target.split("-"))
        prev = f"{y - 1}-{m:02d}"
        for outcome, key in (("BEV_market", "market"), ("Tesla", "Tesla")):
            act, pred = actual[target][key], actual[prev][key]
            out.append(dict(spec="seasonal_naive", target=target, horizon=h, outcome=outcome, actual=act,
                            prediction_median=pred, error=pred - act))
    return out


def metrics(rows):
    groups = {}
    for r in rows:
        period = "2026-10" if r["target"] == "2026-10" else r["target"][:4]
        groups.setdefault((r["spec"], r["outcome"], period, r["horizon"]), []).append(r["error"])
    out = []
    for (spec, outcome, period, h), errs in sorted(groups.items()):
        e = np.array(errs, float)
        out.append(dict(spec=spec, outcome=outcome, period=period, horizon=h, n=len(e),
                        rmse=float(np.sqrt(np.mean(e ** 2))), mae=float(np.mean(np.abs(e)))))
    return out


def verdict(lo, hi):
    return "supported" if lo > 0 else "weakened" if hi < 0 else "open"


def hypotheses(results, metric_rows):
    out = []
    for name, res in results.items():
        irf = {(r["variable"], r["h"]): r for r in res["irf"]}
        coef = {(r["equation"], r["term"]): r for r in res["coef"]}
        for label, var in (("H-F market", "log_market"), ("H-F Tesla share", "alr_Tesla")):
            r = irf[(var, "cum_0_11")]
            out.append(dict(spec=name, hypothesis=label, statistic=f"cumulative 12-month response of {var} to 1-SD fuel shock",
                            median=r["median"], lower95=r["lower95"], upper95=r["upper95"],
                            verdict=verdict(r["lower95"], r["upper95"])))
        r = coef[("log_market", "grant_2026")]
        out.append(dict(spec=name, hypothesis="H-P2026", statistic="grant_2026 in log_market",
                        median=r["median"], lower95=r["lower95"], upper95=r["upper95"],
                        verdict=verdict(r["lower95"], r["upper95"])))
        b, m = coef[("alr_BMW_Group", "tax_package_2025_07")], coef[("alr_Mercedes", "tax_package_2025_07")]
        v = ("supported" if b["lower95"] > 0 and m["lower95"] > 0 else
             "weakened" if b["upper95"] < 0 or m["upper95"] < 0 else "open")
        out.append(dict(spec=name, hypothesis="H-Tax", statistic="tax_package_2025_07 in alr_BMW_Group and alr_Mercedes",
                        median=f"{b['median']:.3f} / {m['median']:.3f}",
                        lower95=f"{b['lower95']:.3f} / {m['lower95']:.3f}",
                        upper95=f"{b['upper95']:.3f} / {m['upper95']:.3f}", verdict=v))
    rm = {(r["spec"], r["outcome"], r["period"], r["horizon"]): r["rmse"] for r in metric_rows}
    for name in [n for n, s in SPECS.items() if s["forecast"]]:
        for outcome in ("Tesla", "BEV_market"):
            wins = [rm[(name, outcome, p, h)] < rm[("M2", outcome, p, h)] for p in ("2025", "2026") for h in (1, 3)]
            v = "supported" if all(wins) else "weakened" if not any(wins) else "open"
            out.append(dict(spec=name, hypothesis=f"Forecast gain {outcome} vs M2",
                            statistic="RMSE below M2 in 2025/2026 at h=1/h=3", median=f"{sum(wins)}/4",
                            lower95="", upper95="", verdict=v))
    return out


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


def run(output, ndraws):
    proto = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if proto != PROTOCOL_SHA256:
        raise SystemExit("Protocol bytes differ from the frozen version; refusing to run")
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    results, fc = {}, []
    for name, spec in SPECS.items():
        results[name] = full_sample(name, spec, ndraws, rng)
        if spec["forecast"]:
            fc += forecasts(name, spec, ndraws, rng)
    targets = {(r["target"], r["horizon"]) for r in fc}
    comp = [r for r in comparators(targets) if (r["target"], r["horizon"]) in targets]
    met = metrics(fc + comp)
    hyp = hypotheses(results, met)
    write_csv(out / "coefficients.csv", [r for res in results.values() for r in res["coef"]])
    write_csv(out / "irf_fuel_shock.csv", [r for res in results.values() for r in res["irf"]])
    write_csv(out / "predictions.csv", fc + comp)
    write_csv(out / "metrics.csv", met)
    write_csv(out / "hypotheses.csv", hyp)
    files = {n: hashlib.sha256((out / n).read_bytes()).hexdigest()
             for n in ("coefficients.csv", "irf_fuel_shock.csv", "predictions.csv", "metrics.csv", "hypotheses.csv")}
    code = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "multibrand").glob("*.py"))}
    manifest = dict(protocol="multibrand-bvarx/1.0.0", protocol_sha256=proto, seed=SEED, draws=ndraws,
                    specs={n: dict(s, n_months=results[n]["n"], window=results[n]["periods"],
                                   fuel_shock_sd=results[n]["fuel_shock_sd"]) for n, s in SPECS.items()},
                    inputs_sha256=data.inputs_sha256(), code_sha256=code, outputs_sha256=files,
                    python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--output", default="results/multibrand")
    p.add_argument("--draws", type=int, default=4000)
    a = p.parse_args()
    m = run(a.output, a.draws)
    print(json.dumps({k: m[k] for k in ("protocol", "draws", "outputs_sha256")}, indent=2))
