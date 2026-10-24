"""Frozen, exploratory private diagnostics; pending real inputs fail before analysis."""

import argparse
import csv
from importlib.metadata import version
import json
from pathlib import Path
import warnings

import numpy as np

from attention.import_trends import (
    ROOT,
    build_import,
    csv_bytes,
    derive_windows,
    periods,
    sha,
)
from attention.transform import timestamp

PROTOCOL = ROOT / "docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md"
KBA = ROOT / "data/kba/derived/observations.csv"
WINDOWS = [("2018-01", "2025-12"), ("2021-01", "2025-12")]


def contained(root, name):
    path = (root / name).resolve()
    if path.parent != root.resolve():
        raise ValueError("Artifact must be a contained basename")
    return path


def admit(raw_path, metadata_path, import_dir, admission_path, kba_path, fixture=False):
    raw, meta_raw = raw_path.read_bytes(), metadata_path.read_bytes()
    meta = json.loads(meta_raw)
    # Intentionally before reading the KBA values or importing diagnostic libraries.
    rows, fresh = build_import(raw, meta, fixture)
    if meta["version"] != "1.1.0" or fresh["status"] != (
        "synthetic_fixture" if fixture else "empirically_populated"
    ):
        raise ValueError("Requires an admitted extended Trends import")
    if (
        meta["query"]["kind"] != "search_term"
        or meta["query"]["value"] != "Tesla"
        or meta["request_window"] != {"selection": "all_available_history"}
    ):
        raise ValueError(
            "Source query/window conflicts with the frozen Tesla full-history protocol"
        )
    a = json.loads(admission_path.read_text())
    if a.get("origin") != ("synthetic" if fixture else "observed") or a.get(
        "status"
    ) != ("synthetic_fixture_only" if fixture else "admitted_private_retrospective"):
        raise ValueError("Pending/unverified human admission")
    for key, expected in [
        ("raw_sha256", sha(raw)),
        ("metadata_sha256", sha(meta_raw)),
        ("kba_sha256", sha(kba_path.read_bytes())),
        ("protocol_sha256", sha(PROTOCOL.read_bytes())),
    ]:
        if a.get(key) != expected:
            raise ValueError("Admission hash mismatch: " + key)
    if not fixture:
        if timestamp(a["reviewed_at"]) < timestamp(meta["retrieved_at"]):
            raise ValueError("Human review cannot predate the export")
        if (
            a.get("source_review_confirmed") is not True
            or a.get("terms_review_confirmed") is not True
            or not isinstance(a.get("review_evidence"), str)
            or not a["review_evidence"].strip()
        ):
            raise ValueError(
                "Explicit human source and terms review required; hashes alone are not legal verification"
            )
        if kba_path.resolve() != KBA.resolve() or ROOT in raw_path.resolve().parents:
            raise ValueError(
                "Requires private original and verified repository KBA data"
            )
        if any(
            sha(p.read_bytes()) == sha(raw)
            for p in (ROOT / "tests/fixtures/trends").glob("*.csv")
        ):
            raise ValueError("Known synthetic fixture cannot be real evidence")
        from kba.pipeline import audit

        audit(
            ROOT / "data/kba/sources.json",
            ROOT / "data/kba/acquisition-plan.json",
            KBA.parent,
        )
    elif kba_path.resolve() == KBA.resolve():
        raise ValueError("Fixture mode cannot consume real KBA observations")
    saved = json.loads((import_dir / "coverage.json").read_text())
    for key in ("status", "raw_sha256", "provenance"):
        if saved.get(key) != fresh.get(key):
            raise ValueError("Imported provenance/status mismatch")
    if saved.get("metadata_sha256") != sha(meta_raw):
        raise ValueError("Imported metadata mismatch")
    series = {"source": rows, **derive_windows(rows, meta)}
    if set(saved.get("outputs", {})) != set(series):
        raise ValueError("Missing/extra source or subset artifact")
    for name, expected in series.items():
        entry = saved["outputs"][name]
        b = contained(import_dir, entry["file"]).read_bytes()
        if (
            b != csv_bytes(expected)
            or sha(b) != entry["sha256"]
            or entry["raw_sha256"] != sha(raw)
        ):
            raise ValueError("Tampered/incorrect derived subset")
    return rows, {
        "label": "SYNTHETIC_FIXTURE_ONLY"
        if fixture
        else "PRIVATE_RETROSPECTIVE_EXPLORATORY",
        "protocol_sha256": sha(PROTOCOL.read_bytes()),
        "implementation_sha256": sha(Path(__file__).read_bytes()),
        "admission_sha256": sha(admission_path.read_bytes()),
        "raw_sha256": sha(raw),
        "metadata_sha256": sha(meta_raw),
        "kba_sha256": sha(kba_path.read_bytes()),
        "source_normalization": meta["normalization"],
        "source_window": meta["source_window"],
    }


def join_months(trends, kba_path, fixture=False):
    with kba_path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != [
            "period",
            "value",
            "series",
            "source",
            "vintage",
            "powertrain",
        ]:
            raise ValueError("Wrong KBA columns")
        rows = list(reader)
    if fixture and any(
        r["source"] != "synthetic_fixture" or r["vintage"] != "synthetic_fixture"
        for r in rows
    ):
        raise ValueError("Fixture KBA provenance required")
    source_periods = [r["period"] for r in trends]
    if source_periods != sorted(set(source_periods)):
        raise ValueError("Duplicate/disordered Trends source timeline")
    selected = [r for r in rows if r["series"] == "brand:TESLA"]
    pp = [r["period"] for r in selected]
    if pp != periods() or any(r["powertrain"] != "all" for r in selected):
        raise ValueError("KBA Tesla must be unique ordered complete 2018-2025")
    tt = [r for r in trends if "2018-01" <= r["period"] <= "2025-12"]
    if [r["period"] for r in tt] != pp:
        raise ValueError("Trends join is not one-to-one complete")
    if any(
        r["value_status"] != "observed_index"
        or r["period_completeness"] != "completed_calendar_month"
        for r in tt
    ):
        raise ValueError(
            "Missing, censored or partial attention months cannot be modeled"
        )
    y = np.array([float(r["value"]) for r in selected])
    x = np.array([r["search_interest_index"] for r in tt], dtype=float)
    if (
        not np.isfinite(y).all()
        or not np.isfinite(x).all()
        or (y < 0).any()
        or (y != np.floor(y)).any()
        or (x < 0).any()
        or (x > 100).any()
    ):
        raise ValueError("Invalid registrations/index units or nonfinite values")
    return pp, y, x


def controls(pp):
    mm = np.array([int(p[5:]) for p in pp])
    return np.column_stack(
        [
            np.ones(len(pp)),
            np.arange(len(pp)),
            np.sin(2 * np.pi * (mm - 1) / 12),
            np.cos(2 * np.pi * (mm - 1) / 12),
            np.isin(mm, [3, 6, 9, 12]),
        ]
    )


def lagged(values, k):
    if k < 0 or k >= len(values):
        raise ValueError("Invalid lag")
    out = np.full(len(values), np.nan)
    out[k:] = values[: len(values) - k] if k else values
    return out


def fit(y, design):
    import statsmodels.api as sm

    if (
        not np.isfinite(design).all()
        or not np.isfinite(y).all()
        or len(y) <= design.shape[1]
        or np.linalg.matrix_rank(design) != design.shape[1]
    ):
        raise ValueError("Nonfinite/rank-deficient/insufficient fit")
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    result = sm.OLS(y, design).fit(
        cov_type="HAC", cov_kwds={"maxlags": 3, "use_correction": True}, use_t=False
    )
    if not np.isfinite(result.bse).all():
        raise ValueError("Nonfinite HAC uncertainty")
    return beta, result


def pseudo_holdout(pp, y, x):
    train = np.array([p < "2025-01" for p in pp])
    mean = float(x[train].mean())
    sd = float(x[train].std(ddof=1))
    if not sd > 0:
        raise ValueError("Constant training attention")
    xx = (x - mean) / sd
    c = controls(pp)
    augmented = np.column_stack([c] + [lagged(xx, k) for k in range(4)])
    valid = np.arange(len(pp)) >= 3
    tr = train & valid
    te = (~train) & valid
    out = {
        "label": "RETROSPECTIVE_CONDITIONAL_PSEUDO_HOLDOUT_NOT_REAL_TIME_FORECAST",
        "attention_training_mean": mean,
        "attention_training_sd": sd,
        "training_periods": [p for p, b in zip(pp, tr) if b],
        "holdout_periods": [p for p, b in zip(pp, te) if b],
        "models": {},
    }
    for name, design in [("calendar", c), ("calendar_plus_trends_lags_0_3", augmented)]:
        beta, result = fit(y[tr], design[tr])
        pred = design[te] @ beta
        out["models"][name] = {
            "coefficients": beta.tolist(),
            "training_se": result.bse.tolist(),
            "predictions": pred.tolist(),
            "rmse": float(np.sqrt(np.mean((y[te] - pred) ** 2))),
        }
    return out


def series_diagnostics(values, level):
    from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss

    if not np.isfinite(values).all() or np.std(values) == 0:
        raise ValueError("Degenerate diagnostic series")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        aa, ac = acf(values, nlags=12, alpha=0.05, fft=False, bartlett_confint=True)
        pa, pc = pacf(values, nlags=12, alpha=0.05, method="ywm")
        ad = adfuller(values, maxlag=3, regression="ct" if level else "c", autolag=None)
        kp = kpss(values, regression="ct" if level else "c", nlags=3)
    return {
        "n": len(values),
        "acf": aa.tolist(),
        "acf_ci": ac.tolist(),
        "pacf": pa.tolist(),
        "pacf_ci": pc.tolist(),
        "adf": {
            "statistic": float(ad[0]),
            "pvalue": float(ad[1]),
            "lags": int(ad[2]),
            "n": int(ad[3]),
            "critical_values": ad[4],
            "null": "unit root",
        },
        "kpss": {
            "statistic": float(kp[0]),
            "pvalue": float(kp[1]),
            "lags": int(kp[2]),
            "critical_values": kp[3],
            "null": "trend stationarity" if level else "level stationarity",
        },
        "deterministic": "ct" if level else "c",
        "warnings": [str(w.message) for w in caught],
        "bands": "pointwise asymptotic; stationary-short-memory assumptions, not simultaneous",
    }


def analyze(pp, y, x, label):
    from statsmodels.stats.multitest import multipletests

    results = {
        "label": label,
        "windows": {},
        "causal_interpretation": False,
        "historical_point_in_time": "not_verified",
    }
    association_rows = []
    for start, end in WINDOWS:
        keep = np.array([start <= p <= end for p in pp])
        ps = [p for p, b in zip(pp, keep) if b]
        yy = y[keep]
        xx = x[keep]
        diag = {}
        for name, v in [
            ("registrations", yy),
            ("log1p_registrations", np.log1p(yy)),
            ("trends", xx),
        ]:
            diag[name] = series_diagnostics(v, True)
            diag["diff_" + name] = series_diagnostics(np.diff(v), False)
        risk = any(
            diag[n]["adf"]["pvalue"] >= 0.05 or diag[n]["kpss"]["pvalue"] < 0.05
            for n in ("registrations", "trends")
        )
        dy, dx = np.diff(yy), np.diff(xx)
        c = controls(ps)[1:]
        valid = np.arange(len(dy)) >= 6
        for k in range(7):
            design = np.column_stack([c, lagged(dx, k)])
            beta, res = fit(dy[valid], design[valid])
            association_rows.append(
                dict(
                    window=start + "_" + end,
                    lag=k,
                    group="primary" if k <= 3 else "sensitivity",
                    n=int(valid.sum()),
                    estimate=float(beta[-1]),
                    se=float(res.bse[-1]),
                    ci95=res.conf_int()[-1].tolist(),
                    p_raw=float(res.pvalues[-1]),
                )
            )
        profiles = {}
        for season in ("month", "quarter"):
            keys = [
                int(p[5:]) if season == "month" else (int(p[5:]) - 1) // 3 + 1
                for p in ps
            ]
            profiles[season] = [
                dict(
                    group=k,
                    n=keys.count(k),
                    registrations=float(yy[np.array(keys) == k].mean()),
                    trends=float(xx[np.array(keys) == k].mean()),
                )
                for k in sorted(set(keys))
            ]
        results["windows"][start + "_" + end] = {
            "periods": ps,
            "registrations": yy.tolist(),
            "log1p_registrations": np.log1p(yy).tolist(),
            "trends": xx.tolist(),
            "diagnostics": diag,
            "profiles": profiles,
            "spurious_level_regression_risk": risk,
            "pseudo_holdout": pseudo_holdout(ps, yy, xx),
        }
    adjusted = multipletests([r["p_raw"] for r in association_rows], method="holm")[1]
    for r, p in zip(association_rows, adjusted):
        r["p_holm_14"] = float(p)
    results["associations"] = association_rows
    return results


def plots(results, out):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for name, w in results["windows"].items():
        fig, axes = plt.subplots(3, 1, figsize=(10, 8))
        for ax, key in zip(axes, ("registrations", "log1p_registrations", "trends")):
            ax.plot(w["periods"], w[key])
            ax.set_ylabel(key)
            ax.axvspan(
                w["periods"].index("2022-01"),
                w["periods"].index("2022-12"),
                alpha=0.08,
                color="grey",
                label="2022 descriptive window",
            )
            ax.set_xticks(np.arange(0, len(w["periods"]), 12))
            ax.tick_params(axis="x", rotation=45)
        fig.suptitle(results["label"] + " — " + name)
        fig.tight_layout()
        fig.savefig(out / (name + "_levels.png"))
        plt.close(fig)
        fig, axes = plt.subplots(2, 2, figsize=(9, 6))
        for i, season in enumerate(("month", "quarter")):
            for j, key in enumerate(("registrations", "trends")):
                vals = w["profiles"][season]
                axes[i, j].plot([v["group"] for v in vals], [v[key] for v in vals])
                axes[i, j].set_title(season + " mean " + key)
        fig.suptitle(results["label"] + " descriptive seasonal profiles")
        fig.tight_layout()
        fig.savefig(out / (name + "_profiles.png"))
        plt.close(fig)
        fig, axes = plt.subplots(6, 2, figsize=(10, 14))
        for i, (key, d) in enumerate(w["diagnostics"].items()):
            for j, stat in enumerate(("acf", "pacf")):
                vals = np.array(d[stat])
                ci = np.array(d[stat + "_ci"])
                axes[i, j].stem(np.arange(13), vals)
                axes[i, j].fill_between(
                    np.arange(13), ci[:, 0] - vals, ci[:, 1] - vals, alpha=0.2
                )
                axes[i, j].set_title(key + " " + stat)
        fig.suptitle(
            results["label"]
            + " zero-centred pointwise reference bands; see stationarity caveats"
        )
        fig.tight_layout()
        fig.savefig(out / (name + "_acf_pacf.png"))
        plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("raw", "metadata", "import-dir", "admission", "kba", "output-dir"):
        p.add_argument("--" + arg, type=Path, required=True)
    p.add_argument("--fixture", action="store_true")
    a = p.parse_args()
    out = a.output_dir.resolve()
    if out.exists() or out == ROOT or ROOT in out.parents:
        raise ValueError("Output must be new and private outside checkout")
    rows, provenance = admit(
        a.raw, a.metadata, a.import_dir, a.admission, a.kba, a.fixture
    )
    pp, y, x = join_months(rows, a.kba, a.fixture)
    result = analyze(pp, y, x, provenance["label"])
    result["provenance"] = provenance
    result["versions"] = {
        name: version(name)
        for name in ("numpy", "scipy", "statsmodels", "matplotlib", "pandas")
    }
    # Validate all numeric outputs before producing a successful report.
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    out.mkdir(parents=True)
    plots(result, out)
    (out / "diagnostics.json").write_text(encoded)
    with (out / "associations.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(result["associations"][0]))
        writer.writeheader()
        writer.writerows(result["associations"])
    text = (
        "# "
        + provenance["label"]
        + "\n\nExploratory association only; no causal effect or ROI.\n"
    )
    text += "\n2025 is a retrospective conditional pseudo-holdout, not a real-time forecast.\n"
    text += "\n2022 is descriptive; no oil-shock/war attribution or 2026 registration analysis.\n"
    for name, w in result["windows"].items():
        h = w["pseudo_holdout"]
        text += "\n## " + name + "\n\n"
        text += f"Months: {len(w['periods'])}; training fits: {len(h['training_periods'])}; holdout: {len(h['holdout_periods'])}.\n\n"
        text += f"Spurious-level-regression risk flag: {w['spurious_level_regression_risk']}. This is not proof of stationarity or causality.\n\n"
        for model, v in h["models"].items():
            text += f"- {model}: retrospective conditional holdout RMSE = {v['rmse']:.6g} registration counts.\n"
    text += "\nSee diagnostics.json and associations.csv for conditional HAC uncertainty, Holm adjustment across all 14 lag tests, unit-root nulls/warnings, versions and input/protocol hashes.\n"
    (out / "report.md").write_text(text)
    inventory = {
        p.name: sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()
    }
    (out / "inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps({"label": provenance["label"], "output": str(out)}))


if __name__ == "__main__":
    main()
