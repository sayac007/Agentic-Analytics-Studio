"""Preregistered Task 01I.3; private outputs and admitted diesel/FX only."""

import argparse
import csv
import json
import math
import platform
from pathlib import Path
import subprocess
import warnings

import numpy as np
from scipy.stats import norm
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.diagnostic import breaks_cusumolsresid
from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss

from fuel_oil import rights_admission as rights
from fuel_oil.fetch_fuel_oil import encoded, sha, month_range

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md"
PROTOCOL_SHA = "429bca69a59d978bf2bb038a358dfd21bffd36ad1b21c66ca03214ed22ba7376"
PROTOCOL_COMMIT = "94d013ab1e2b623899641760d9524ac8f3ed59e9"
AUTHORIZATION = ROOT / "workorders/01i3-scoped-energy-econometrics.md"
AUTHORIZATION_SHA = "6cc6352ebe1280e62a82d8e92aa4aa7cbaf50bd34f526d4631f7e722418bb5fc"
KBA = ROOT / "data/kba/derived/observations.csv"
PERIODS = month_range("2018-01", "2025-12")
SOURCES = ("eurusd", "diesel_de")


def json_safe(value):
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def freeze_gate():
    if (
        sha(PROTOCOL.read_bytes()) != PROTOCOL_SHA
        or sha(AUTHORIZATION.read_bytes()) != AUTHORIZATION_SHA
    ):
        raise ValueError(
            "Frozen protocol or separate scope authorization hash mismatch"
        )
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", PROTOCOL_COMMIT, "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    original = subprocess.run(
        [
            "git",
            "show",
            PROTOCOL_COMMIT + ":docs/SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout
    if sha(original) != PROTOCOL_SHA:
        raise ValueError("Protocol was not frozen in required first commit")


def private_output(path):
    resolved = Path(path).resolve()
    if resolved.is_relative_to(ROOT.resolve()) or resolved.exists():
        raise ValueError("Use a NEW private output outside Git")
    return resolved


def read_json(path):
    return json.loads(Path(path).read_text())


def gate(energy, permits, kba, fixture=False):
    """Verify energy permits/hashes FIRST; numeric KBA parsing occurs only afterwards."""
    freeze_gate()
    energy, permits, kba = Path(energy), Path(permits), Path(kba)
    provenance = {
        "scope": "SYNTHETIC_FIXTURE_ONLY"
        if fixture
        else "PRIVATE_RETROSPECTIVE_EXPLORATORY_TASK_01I3",
        "protocol_sha256": PROTOCOL_SHA,
        "protocol_commit": PROTOCOL_COMMIT,
        "scope_authorization_sha256": AUTHORIZATION_SHA,
        "historical_point_in_time": "not_established",
        "task_01j_executed": False,
        "public_redistribution_approval": "not_granted",
        "sources": {},
    }
    catalog = read_json(rights.DATA / "real_sources.json")
    if fixture:
        manifest_path = energy / "fixture_manifest.json"
        manifest = read_json(manifest_path)
        if manifest["scope"] != "SYNTHETIC_FIXTURE_ONLY" or set(
            manifest["sources"]
        ) != set(SOURCES):
            raise ValueError(
                "Synthetic scope must contain only admitted-shaped FX and diesel; no Brent"
            )
        source_meta = manifest["sources"]
    else:
        if energy.resolve().is_relative_to(
            ROOT.resolve()
        ) or permits.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Real energy/permits must remain private")
        matrix = read_json(rights.DATA / "rights_admission.json")
        decisions = rights.check(matrix, catalog)
        if (
            any(decisions[id]["status"] != "admitted" for id in SOURCES)
            or decisions["brent_usd"]["status"] != "blocked"
        ):
            raise ValueError("Required source admission or Brent exclusion failed")
        inv = rights.verify_private(
            matrix, catalog, energy, ids=list(SOURCES)
        )  # Never reads Brent files.
    for id in SOURCES:
        permit_path = permits / (id + ".admission.json")
        a = read_json(permit_path)
        key, unit = rights.IDENTITIES[id]
        expected_scope = (
            "SYNTHETIC_FIXTURE_ONLY" if fixture else "private_retrospective_only"
        )
        if (
            a["scope"] != expected_scope
            or a["source_id"] != id
            or a["series_id"] != key
            or a["unit"] != unit
        ):
            raise ValueError(
                "Permit source/key/unit/scope mismatch; no Brent or mixed fixtures"
            )
        native_path = energy / (id + ".quarantined.json")
        native_raw = native_path.read_bytes()
        native = json.loads(native_raw)
        if (
            sha(native_raw) != a["native_normalized_sha256"]
            or native["raw_sha256"] != a["raw_sha256"]
        ):
            raise ValueError("Native/source hash mismatch")
        if fixture:
            meta = source_meta[id]
            raw_name = meta["raw_file"]
            if raw_name != f"SYNTHETIC_{id}.raw":
                raise ValueError("Noncanonical fixture raw filename")
            raw = (energy / raw_name).read_bytes()
            if (
                a["fixture_manifest_sha256"] != sha(manifest_path.read_bytes())
                or sha(raw) != meta["raw_sha256"]
                or sha(raw) != a["raw_sha256"]
                or sha(raw) == catalog["files"][id]["sha256"]
            ):
                raise ValueError("Fixture identity/hash/mixing gate failed")
        else:
            record = next(r for r in matrix["series"] if r["id"] == id)
            if (
                a["raw_sha256"] != catalog["files"][id]["sha256"]
                or a["rights_matrix_sha256"]
                != sha((rights.DATA / "rights_admission.json").read_bytes())
                or a["native_normalized_sha256"] != inv[id]["normalized_sha256"]
            ):
                raise ValueError("Actual permit/source/matrix binding mismatch")
            if (
                a["human_decision_evidence_hash"]
                != record["human_admission_decision"]["evidence_hash"]
                or a["human_decision_source_message_hash"]
                != record["human_admission_decision"]["source_message_hash"]
                or a["human_decision_date"]
                != record["human_admission_decision"]["decision_date"]
                or a["conditions"] != record["conditions"]
                or a["source_attribution"] != record["source_attribution"]
                or a["historical_point_in_time"] != "not_established"
                or a["task_01j_authorized"] is not False
                or a["public_redistribution_approval"] != "not_granted"
            ):
                raise ValueError("Human scope/rights boundary failed")
            if id == "diesel_de" and (
                a["admission_qualification"] != "qualified_project_specific_private_use"
                or a["legal_status"] != "not_verified"
                or a["unresolved_limitations"] != record["unresolved_limitations"]
            ):
                raise ValueError("Qualified diesel limits missing")
        for row in native["observations"]:
            if (
                row["series_id"] != key
                or row["unit"] != unit
                or row["frequency"] != ("monthly" if id == "eurusd" else "weekly")
            ):
                raise ValueError("Native identity/unit/frequency drift")
        proof = {
            "permit_sha256": sha(permit_path.read_bytes()),
            "raw_sha256": a["raw_sha256"],
            "native_normalized_sha256": sha(native_raw),
            "series_id": key,
            "source_unit": unit,
            "conditions": a.get("conditions", []),
            "attribution": a.get("source_attribution"),
            "qualification": a.get("admission_qualification"),
            "unresolved_limitations": a.get("unresolved_limitations", []),
        }
        if id == "diesel_de":
            monthly_path = energy / "diesel_de.monthly_approx.quarantined.json"
            raw = monthly_path.read_bytes()
            if (
                sha(raw) != a["monthly_approx_sha256"]
                or json.loads(raw)["raw_sha256"] != a["raw_sha256"]
                or a["missing_months"] != rights.GAPS
            ):
                raise ValueError("Monthly diesel hash/missingness binding failed")
            proof["monthly_approx_sha256"] = sha(raw)
        provenance["sources"][id] = proof
    # Only after both energy sources pass, inspect/parse outcome bytes.
    if fixture:
        if (
            kba.resolve() == KBA.resolve()
            or sha(kba.read_bytes()) != manifest["kba_sha256"]
            or sha(kba.read_bytes())
            == read_json(ROOT / "data/kba/derived/coverage.json")["A"][
                "normalized_data_sha256"
            ]
        ):
            raise ValueError("Fixture KBA identity/mixing failure")
    else:
        if kba.resolve() != KBA.resolve():
            raise ValueError("Real mode requires verified repository KBA")
        from kba.pipeline import audit

        audit(
            ROOT / "data/kba/sources.json",
            ROOT / "data/kba/acquisition-plan.json",
            KBA.parent,
        )
        reports = read_json(KBA.parent / "coverage.json")
        selected = [r for r in reports.values() if r["series"] == "brand:TESLA"]
        if (
            len(selected) != 1
            or selected[0]["admission_regimes"]["retrospective_immutable_reference"][
                "status"
            ]
            != "admitted"
            or selected[0]["license_status"] != "dl-de/by-2-0"
            or selected[0]["normalized_data_sha256"] != sha(kba.read_bytes())
        ):
            raise ValueError("KBA retrospective source/rights admission failed")
        provenance["kba_admission_scope"] = (
            "Audited retrospective source/rights plus explicit Task 01I.3 observed-outcome research authorization; not as-of/causal validation"
        )
        provenance["kba_catalog_sha256"] = sha(
            (ROOT / "data/kba/sources.json").read_bytes()
        )
    provenance["kba_sha256"] = sha(kba.read_bytes())
    return provenance


def unique_periods(rows):
    seen = {}
    for r in rows:
        p = r["period"]
        if (
            not isinstance(p, str)
            or len(p) != 7
            or p not in month_range("1900-01", "2100-12")
            or p in seen
        ):
            raise ValueError("Invalid/duplicate monthly period")
        seen[p] = r
    return seen


def load_aligned(energy, kba):
    energy = Path(energy)
    fx = unique_periods(read_json(energy / "eurusd.quarantined.json")["observations"])
    diesel = unique_periods(
        read_json(energy / "diesel_de.monthly_approx.quarantined.json")["observations"]
    )
    series = {}
    for id, source, unit in [
        ("eurusd", fx, "USD_per_EUR"),
        ("diesel_de", diesel, "EUR_per_litre"),
    ]:
        if any(p not in source for p in PERIODS):
            raise ValueError("Missing calendar slots, no silent fills")
        values = []
        for p in PERIODS:
            r = source[p]
            v = r["value"]
            if r["unit"] != unit or r.get("partial", False):
                raise ValueError("Wrong unit/partial modeling period")
            if id == "diesel_de" and ((p in rights.GAPS) != (v is None)):
                raise ValueError("Unexpected diesel missingness or filled gap")
            if v is None:
                if id == "eurusd":
                    raise ValueError("FX value missing")
                values.append(np.nan)
            elif isinstance(v, bool) or not np.isfinite(v) or v <= 0:
                raise ValueError("Invalid energy value")
            else:
                values.append(float(v))
        series[id] = np.array(values)
    with Path(kba).open(newline="") as f:
        rows = list(csv.DictReader(f))
    chosen = [
        r
        for r in rows
        if r.get("series") == "brand:TESLA"
        and "2018-01" <= r.get("period", "") <= "2025-12"
    ]
    by = unique_periods(chosen)
    if set(by) != set(PERIODS):
        raise ValueError("KBA Tesla must have exactly 96 completed outcome months")
    counts = []
    for p in PERIODS:
        row = by[p]
        if row.get("powertrain") != "all" or not str(row["value"]).isdigit():
            raise ValueError("Wrong KBA definition/count")
        counts.append(int(row["value"]))
    return np.array(counts, dtype=float), series


def difference(values):
    return np.r_[
        np.nan, np.diff(values)
    ]  # NaNs propagate across actual adjacent months.


def lagged(values, k):
    if k not in range(7):
        raise ValueError("Only preregistered lags 0..6")
    out = np.full(len(values), np.nan)
    out[k:] = values[: len(values) - k] if k else values
    return out


def controls(periods):
    month = np.array([int(p[5:]) for p in periods])
    time = np.array([(int(p[:4]) - 2018) * 12 + int(p[5:]) - 1 for p in periods])
    return np.column_stack(
        [np.ones(len(periods)), time]
        + [(month == m).astype(float) for m in range(2, 13)]
    )


def fit_hac(y, x, calendar_indices, min_df=20):
    y, x, indices = np.asarray(y), np.asarray(x), np.asarray(calendar_indices)
    n, p = x.shape
    if (
        y.shape != (n,)
        or indices.shape != (n,)
        or len(set(indices.tolist())) != n
        or np.any(np.diff(indices) <= 0)
    ):
        raise ValueError("Bad calendar/design alignment")
    if (
        not np.isfinite(y).all()
        or not np.isfinite(x).all()
        or n - p < min_df
        or np.linalg.matrix_rank(x) != p
    ):
        raise ValueError("Nonfinite/rank-deficient/insufficient residual df")
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    resid = y - x @ beta
    scores = x * resid[:, None]
    meat = scores.T @ scores
    lookup = {int(t): i for i, t in enumerate(indices)}
    for h in range(1, 4):
        for i, t in enumerate(indices):
            j = lookup.get(int(t) - h)
            if j is not None:
                cross = np.outer(scores[i], scores[j])
                meat += (1 - h / 4) * (cross + cross.T)
    bread = np.linalg.inv(x.T @ x)
    cov = bread @ meat @ bread * (n / (n - p))
    cov = (cov + cov.T) / 2
    if not np.isfinite(cov).all() or np.any(np.diag(cov) < -1e-10):
        raise ValueError("Invalid HAC covariance")
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    if np.any(se == 0):
        raise ValueError("Degenerate zero HAC standard error")
    z = beta / se
    pv = 2 * norm.sf(np.abs(z))
    ci = np.column_stack([beta - norm.ppf(0.975) * se, beta + norm.ppf(0.975) * se])
    return {
        "coefficients": beta,
        "se": se,
        "covariance": cov,
        "ci95": ci,
        "pvalues": pv,
        "n": n,
        "rank": p,
        "residual_df": n - p,
        "condition_number": float(np.linalg.cond(x)),
        "residuals": resid,
        "calendar_indices": indices,
    }


def contiguous_segment(values):
    best = []
    current = []
    for i, v in enumerate(values):
        if np.isfinite(v):
            current.append(i)
        else:
            if len(current) > len(best):
                best = current
            current = []
    if len(current) > len(best):
        best = current
    return np.array(best, dtype=int)


def diagnostics(values, level):
    segment = contiguous_segment(values)
    v = values[segment]
    meta = {
        "n": len(v),
        "segment_periods": [PERIODS[i] for i in segment],
        "method": "longest contiguous finite segment; earliest tie",
        "deterministic": "ct" if level else "c",
    }
    if len(v) < 27 or np.std(v) == 0:
        return dict(
            meta,
            status="not_estimable",
            reason="Fewer than 27 contiguous months or constant series",
        )
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            aa, ac = acf(v, nlags=12, alpha=0.05, fft=False, bartlett_confint=True)
            pa, pc = pacf(v, nlags=12, alpha=0.05, method="ywm")
            ad = adfuller(v, maxlag=3, regression=meta["deterministic"], autolag=None)
            kp = kpss(v, regression=meta["deterministic"], nlags=3)
        return dict(
            meta,
            status="estimated",
            acf=aa,
            acf_ci95=ac,
            pacf=pa,
            pacf_ci95=pc,
            adf={
                "statistic": ad[0],
                "pvalue": ad[1],
                "lags": ad[2],
                "n": ad[3],
                "critical_values": ad[4],
                "null": "unit root",
            },
            kpss={
                "statistic": kp[0],
                "pvalue": kp[1],
                "lags": kp[2],
                "critical_values": kp[3],
                "null": "trend stationarity" if level else "level stationarity",
            },
            warnings=[str(w.message) for w in caught],
            caution="Short samples/breaks limit tests; pointwise asymptotic intervals, not stationarity proof or simultaneous bands",
        )
    except (ValueError, np.linalg.LinAlgError) as exc:
        return dict(meta, status="not_estimable", reason=str(exc))


def holdout(y, values):
    xx = lagged(values, 1)
    eligible = np.isfinite(xx)
    idx = np.arange(len(y))
    train = eligible & (idx < 84)
    test = eligible & (idx >= 84)
    meta = {
        "label": "RETROSPECTIVE_CONDITIONAL_PSEUDO_HOLDOUT_NOT_REAL_TIME_BACKTEST",
        "lag": 1,
        "training_periods": [p for p, b in zip(PERIODS, train) if b],
        "holdout_periods": [p for p, b in zip(PERIODS, test) if b],
    }
    if test.sum() != 12:
        return dict(
            meta, status="not_estimable", reason="Incomplete fixed 2025 holdout"
        )
    c = controls(PERIODS)
    aug = np.column_stack([c, xx])
    models = {}
    try:
        for name, x in [("baseline", c), ("plus_one_energy_lag1", aug)]:
            fit = fit_hac(np.log1p(y[train]), x[train], idx[train])
            pred = x[test] @ fit["coefficients"]
            with np.errstate(over="raise", invalid="raise"):
                counts = np.expm1(pred)
            models[name] = {
                "fit": fit,
                "predicted_log1p": pred,
                "predicted_counts": counts,
                "negative_count_predictions": int(np.sum(counts < 0)),
                "rmse_log1p": float(np.sqrt(np.mean((np.log1p(y[test]) - pred) ** 2))),
                "rmse_counts": float(np.sqrt(np.mean((y[test] - counts) ** 2))),
            }
        return dict(meta, status="estimated", observed_counts=y[test], models=models)
    except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
        return dict(meta, status="not_estimable", reason=str(exc))


def analyze(y, energy):
    if y.shape != (96,) or not np.isfinite(y).all() or np.any(y < 0):
        raise ValueError("Invalid fixed outcome")
    z = np.log1p(y)
    c = controls(PERIODS)
    idx = np.arange(96)
    diagnostics_out = {}
    for name, values in [("tesla_log1p", z), *energy.items()]:
        diagnostics_out[name] = {
            "levels": diagnostics(values, True),
            "differences": diagnostics(difference(values), False),
        }
    models = []
    cross = []
    for id in SOURCES:
        for transform in ["differences", "levels"]:
            yy = difference(z) if transform == "differences" else z
            base = difference(energy[id]) if transform == "differences" else energy[id]
            for k in range(7):
                xx = lagged(base, k)
                ok = np.isfinite(yy) & np.isfinite(xx)
                row = {
                    "source": id,
                    "transformation": transform,
                    "lag": k,
                    "role": "primary" if k <= 3 else "sensitivity",
                    "n": int(ok.sum()),
                    "eligible_periods": [p for p, b in zip(PERIODS, ok) if b],
                    "excluded_periods": [p for p, b in zip(PERIODS, ok) if not b],
                }
                if transform == "differences":
                    corr = (
                        float(np.corrcoef(yy[ok], xx[ok])[0, 1])
                        if ok.sum() > 1 and np.std(yy[ok]) > 0 and np.std(xx[ok]) > 0
                        else None
                    )
                    cross.append(
                        {
                            "source": id,
                            "lag": k,
                            "n": int(ok.sum()),
                            "pearson_r": corr,
                            "inference": "descriptive_only_no_pvalue",
                        }
                    )
                try:
                    baseline = fit_hac(yy[ok], c[ok], idx[ok])
                    fit = fit_hac(yy[ok], np.column_stack([c, xx])[ok], idx[ok])
                    row.update(
                        status="estimated",
                        baseline=baseline,
                        augmented=fit,
                        energy_coefficient=fit["coefficients"][-1],
                        energy_se=fit["se"][-1],
                        energy_ci95=fit["ci95"][-1],
                        raw_pvalue=fit["pvalues"][-1],
                    )
                except (ValueError, np.linalg.LinAlgError) as exc:
                    row.update(status="not_estimable", reason=str(exc), raw_pvalue=None)
                models.append(row)
    adjusted = multipletests(
        [r["raw_pvalue"] if r["raw_pvalue"] is not None else 1 for r in models],
        method="holm",
    )[1]
    for row, p in zip(models, adjusted):
        row["holm_pvalue_28_tests"] = (
            float(p) if row["raw_pvalue"] is not None else None
        )
    baseline = fit_hac(z, c, idx)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        stat, pvalue, critical = breaks_cusumolsresid(
            baseline["residuals"], ddof=c.shape[1]
        )
    stability = {
        "statistic": stat,
        "pvalue": pvalue,
        "critical_values": critical,
        "warnings": [str(w.message) for w in caught],
        "caution": "CUSUM calibration not repaired by HAC; serial correlation/heteroskedasticity may invalidate it; no breakpoint/model selection",
    }
    seasonal = {
        name: [
            {
                "month": m,
                "n": int(
                    np.sum(np.isfinite(v[np.array([int(p[5:]) == m for p in PERIODS])]))
                ),
                "mean": float(
                    np.nanmean(v[np.array([int(p[5:]) == m for p in PERIODS])])
                ),
            }
            for m in range(1, 13)
        ]
        for name, v in [("tesla_count", y), *energy.items()]
    }
    return {
        "periods": PERIODS,
        "series": {"tesla_count": y, "tesla_log1p": z, **energy},
        "diagnostics": diagnostics_out,
        "associations": models,
        "descriptive_cross_correlations": cross,
        "seasonality_trend_confounded": seasonal,
        "cusum_calendar_baseline": stability,
        "holdout": {id: holdout(y, energy[id]) for id in SOURCES},
        "warnings": [
            "Exploratory conditional associations, not causal effects or real-time forecasts",
            "Current vintage, unmodelled confounders, missingness, short samples and multiple testing limit interpretation",
            "2022 is descriptive only; diesel January/April 2022 missing; no 2026 outcomes or Brent",
        ],
    }


def plots(result, out):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def save(fig, name):
        fig.tight_layout()
        fig.savefig(
            out / name,
            dpi=120,
            metadata={"Software": "Agentic Analytics Studio Task 01I.3"},
        )
        plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(12, 9))
    for i, (name, v) in enumerate(
        [
            ("tesla_count", result["series"]["tesla_count"]),
            ("eurusd", result["series"]["eurusd"]),
            ("diesel_de", result["series"]["diesel_de"]),
        ]
    ):
        for j, values in enumerate(
            [v, difference(np.log1p(v)) if name == "tesla_count" else difference(v)]
        ):
            axes[i, j].plot(np.arange(96), values)
            axes[i, j].axvspan(48, 59, color="gray", alpha=0.15)
            axes[i, j].set_title(name + (" levels" if j == 0 else " changes"))
    save(fig, "series.png")
    fig, axes = plt.subplots(6, 2, figsize=(12, 16))
    i = 0
    for name, types in result["diagnostics"].items():
        for transform, d in types.items():
            for j, key in enumerate(["acf", "pacf"]):
                ax = axes[i, j]
                ax.set_title(name + " " + transform + " " + key)
                if d["status"] == "estimated":
                    vals = np.array(d[key])
                    ci = np.array(d[key + "_ci95"])
                    ax.errorbar(
                        np.arange(len(vals)),
                        vals,
                        yerr=np.maximum(
                            np.vstack([vals - ci[:, 0], ci[:, 1] - vals]), 0
                        ),
                        fmt="o",
                    )
                    ax.axhline(0, color="gray")
                else:
                    ax.text(0.1, 0.5, "Not estimable", transform=ax.transAxes)
            i += 1
    save(fig, "acf_pacf.png")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for i, id in enumerate(SOURCES):
        for j, transform in enumerate(["differences", "levels"]):
            ax = axes[i, j]
            ax.set_title(id + " " + transform + " conditional HAC 95%")
            for r in result["associations"]:
                if (
                    r["source"] == id
                    and r["transformation"] == transform
                    and r["status"] == "estimated"
                ):
                    ci = np.array(r["energy_ci95"])
                    beta = r["energy_coefficient"]
                    ax.errorbar(
                        r["lag"],
                        beta,
                        yerr=np.array([[max(beta - ci[0], 0)], [max(ci[1] - beta, 0)]]),
                        fmt="o",
                        color="blue" if r["lag"] <= 3 else "gray",
                    )
            ax.axhline(0, color="black")
            ax.set_xlabel("Calendar-month lag")
    save(fig, "lag_associations.png")
    fig, axes = plt.subplots(2, 1, figsize=(12, 7))
    for ax, id in zip(axes, SOURCES):
        h = result["holdout"][id]
        ax.set_title(id + " retrospective 2025 conditional comparison")
        if h["status"] == "estimated":
            ax.plot(h["observed_counts"], label="observed Tesla registrations")
            for label, m in h["models"].items():
                ax.plot(m["predicted_counts"], label=label)
            ax.legend()
        else:
            ax.text(0.1, 0.5, "Not estimable", transform=ax.transAxes)
    save(fig, "holdout.png")


def report(result):
    lines = [
        "# PRIVATE Task 01I.3 exploratory results",
        "",
        *result["warnings"],
        "",
        "## Fixed model comparisons",
        "Source | transform | lag | n | beta | conditional 95% interval | Holm p (28)",
        "---|---|---|---|---|---|---",
    ]
    for r in result["associations"]:
        lines.append(
            f"{r['source']} | {r['transformation']} | {r['lag']} | {r['n']} | {r.get('energy_coefficient')} | {r.get('energy_ci95')} | {r.get('holm_pvalue_28_tests')}"
            if r["status"] == "estimated"
            else f"{r['source']} | {r['transformation']} | {r['lag']} | {r['n']} | not estimable | {r['reason']} | NA"
        )
    fitted = [r for r in result["associations"] if r["status"] == "estimated"]
    negative = sum(r["energy_coefficient"] < 0 for r in fitted)
    rejected = sum(r["holm_pvalue_28_tests"] < 0.05 for r in fitted)
    lines += [
        "",
        f"Across the complete prespecified family, {len(fitted)} models are estimable; {negative} coefficients are negative and {len(fitted) - negative} nonnegative. {rejected} tests have Holm-adjusted p<0.05. This is conditional multiple-tested association, not causal identification.",
    ]
    if rejected == 0:
        lines.append(
            "No coefficient test meets the adjusted threshold; this is not proof of no effect or adequate power."
        )
    lines += [
        "",
        "## Fixed stationarity diagnostics on contiguous segments",
        "Series / transform | n | bounds | ADF p | KPSS p",
        "---|---|---|---|---",
    ]
    for name, types in result["diagnostics"].items():
        for transform, d in types.items():
            bounds = (
                (d["segment_periods"][0], d["segment_periods"][-1])
                if d["segment_periods"]
                else None
            )
            lines.append(
                f"{name}/{transform} | {d['n']} | {bounds} | {d.get('adf', {}).get('pvalue')} | {d.get('kpss', {}).get('pvalue')}"
            )
    lines.append(
        "ADF null: unit root. KPSS null: trend stationarity for levels, level stationarity for differences. P-value warnings/bounds are retained; neither test settles the data-generating process or changes this specification."
    )
    lines.append(
        f"Fixed calendar-baseline CUSUM p-value: {result['cusum_calendar_baseline']['pvalue']}; its usual calibration may fail with serial correlation/heteroskedasticity, despite HAC in separate coefficient fits."
    )
    lines += [
        "",
        "## Retrospective pseudo-holdout; not a historical real-time forecast",
    ]
    for id, h in result["holdout"].items():
        lines.append(id + ": " + h["status"])
        if h["status"] == "estimated":
            for name, m in h["models"].items():
                lines.append(
                    f"- {name}: log1p RMSE {m['rmse_log1p']}; count RMSE {m['rmse_counts']}; negative inverse predictions {m['negative_count_predictions']}"
                )
            difference_rmse = (
                h["models"]["plus_one_energy_lag1"]["rmse_counts"]
                - h["models"]["baseline"]["rmse_counts"]
            )
            lines.append(
                f"- Count RMSE change (augmented minus baseline): {difference_rmse}. Negative is descriptive improvement; positive is deterioration. No causal/predictive-generalisation guarantee."
            )
            lines.append(
                "The fixed added predictor improves this retrospective count-scale error."
                if difference_rmse < 0
                else "The fixed added predictor does not improve this retrospective count-scale error. This result is retained without changing the model."
            )
    lines += [
        "",
        "## Interpretation",
        "Every prespecified model, including null/negative estimates and failed fits, is retained. Intervals and Holm-adjusted p-values describe conditional model uncertainty; they do not establish exogeneity or remove unmodelled subsidies, prices, launches, supply, macro or attention confounding. No specification was selected or changed from these results.",
        "Diagnostics/CUSUM and longest-segment limitations are in results.json. Short/broken samples and gaps make conventional unit-root and stability tests uncertain. January and April 2022 diesel gaps prevent an uninterrupted price episode; no war treatment or causal oil shock is identified.",
        "The private source observations/metadata remain unchanged. Preserve attribution and all qualified EC limitations; no redistribution or historical as-of claim. No Brent, 2026 outcomes, Task 01J or Task 01G modification.",
    ]
    return "\n".join(lines) + "\n"


def run(energy, permits, kba, output, fixture=False):
    output = private_output(output)
    provenance = gate(energy, permits, kba, fixture)  # Before numeric outcomes/joins.
    y, sources = load_aligned(energy, kba)
    result = analyze(y, sources)
    import scipy, statsmodels, matplotlib

    provenance.update(
        implementation_sha256=sha(Path(__file__).read_bytes()),
        implementation_commit=subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip(),
        versions={
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "statsmodels": statsmodels.__version__,
            "matplotlib": matplotlib.__version__,
        },
    )
    output.mkdir(parents=True)
    (output / "results.json").write_bytes(encoded(json_safe(result)))
    (output / "provenance.json").write_bytes(encoded(json_safe(provenance)))
    (output / "samples.json").write_bytes(
        encoded(
            {
                "sources": {
                    id: {
                        "observed_months": int(np.isfinite(v).sum()),
                        "missing_months": [
                            p for p, z in zip(PERIODS, v) if not np.isfinite(z)
                        ],
                    }
                    for id, v in sources.items()
                },
                "association_samples": [
                    {
                        k: r[k]
                        for k in [
                            "source",
                            "transformation",
                            "lag",
                            "n",
                            "eligible_periods",
                            "excluded_periods",
                        ]
                    }
                    for r in result["associations"]
                ],
            }
        )
    )
    with (output / "associations.csv").open("w", newline="") as f:
        fields = [
            "source",
            "transformation",
            "lag",
            "role",
            "n",
            "status",
            "energy_coefficient",
            "energy_se",
            "raw_pvalue",
            "holm_pvalue_28_tests",
        ]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in result["associations"]:
            writer.writerow({k: r.get(k) for k in fields})
    (output / "report.md").write_text(report(json_safe(result)))
    plots(result, output)
    (output / "manifest.json").write_bytes(
        encoded(
            {
                "scope": provenance["scope"],
                "protocol_sha256": PROTOCOL_SHA,
                "file_hashes": {
                    p.name: sha(p.read_bytes()) for p in sorted(output.iterdir())
                },
                "completed": True,
                "public_results_allowed": False,
            }
        )
    )
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["energy-dir", "permits-dir", "output"]:
        p.add_argument("--" + name, required=True, type=Path)
    p.add_argument("--kba", type=Path, default=KBA)
    p.add_argument("--fixture", action="store_true")
    a = p.parse_args()
    try:
        run(a.energy_dir, a.permits_dir, a.kba, a.output, a.fixture)
        print(
            "Scoped private study completed; no empirical values printed. Fixture mode."
            if a.fixture
            else "Scoped private study completed; no empirical values printed. Real admitted-source mode."
        )
    except Exception as exc:
        p.exit(
            1,
            f"Scoped study refused ({type(exc).__name__}); no completed public study or private values printed\n",
        )


if __name__ == "__main__":
    main()
