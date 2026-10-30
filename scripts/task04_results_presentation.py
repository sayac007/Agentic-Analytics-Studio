"""Present preserved Task04 outputs in English; no fitting, tuning or downloads.

Run with --check to verify the committed tables, figures and their source hashes.
Only the marked README section and results/task04/presentation may be written.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/aas-task04-presentation-mpl")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/aas-task04-presentation-cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import FuncFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/task04/stage1"
OUTPUT = ROOT / "results/task04/presentation"
BEGIN = "<!-- BEGIN TASK04 COMPUTED RESULTS -->"
END = "<!-- END TASK04 COMPUTED RESULTS -->"
MODELS = ("M0", "M1", "M2", "M2_sd0.05", "M2_sd0.10", "M2_sd0.20", "M2_portal", "M2_logit")
PAIRS = ((2025, 1), (2025, 3), (2026, 1), (2026, 3))
BLUE, GOLD = "#0072B2", "#E69F00"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def number(value, digits=1, signed=False):
    text = format(float(value), ("+" if signed else "") + f",.{digits}f")
    return text.replace("-", "−")


def table(headers, rows):
    def line(row):
        return "| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |"
    return "\n".join([line(headers), line(["---"] * len(headers)), *[line(r) for r in rows]])


def interval(row, digits=3, mark=False):
    text = (f"{number(row['median'], digits, True)} "
            f"[{number(row['lower95'], digits, True)}; {number(row['upper95'], digits, True)}]")
    return text + (" **†**" if mark and excludes_zero(row) else "")


def excludes_zero(row):
    return float(row["lower95"]) > 0 or float(row["upper95"]) < 0


def load():
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    # Every original output and every bound public input stays immutable.
    for name, expected in manifest["files"].items():
        if sha((SOURCE / name).read_bytes()) != expected:
            raise ValueError("Original result hash mismatch: " + name)
    for name, expected in manifest["input_hashes"].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError("Original input hash mismatch: " + name)
    names = ("coefficients.csv", "metrics.csv", "decomposition.csv", "contrasts.csv", "predictions.csv")
    data = {name: list(csv.DictReader((SOURCE / name).open(newline=""))) for name in names}
    c, metrics, predictions = data["coefficients.csv"], data["metrics.csv"], data["predictions.csv"]
    if len(c) != 132 or len(metrics) != 128 or len(predictions) != 1280:
        raise ValueError("Incomplete preserved study")
    if {r["model"] for r in c} != set(MODELS):
        raise ValueError("Unexpected model family")
    grouped = defaultdict(list)
    for p in predictions:
        key = (p["model"], p["outcome"], int(p["year"]), int(p["horizon"]))
        if not math.isclose(float(p["error"]), float(p["prediction_mean"]) - float(p["actual"]), abs_tol=1e-8):
            raise ValueError("Prediction/error disagreement")
        grouped[key].append(p)
    seen = set()
    for m in metrics:
        key = (m["model"], m["outcome"], int(m["year"]), int(m["horizon"]))
        ps = grouped[key]
        if key in seen or len(ps) != int(m["n"]) or len({p["target"] for p in ps}) != len(ps):
            raise ValueError("Invalid comparison mask")
        seen.add(key)
        rmse = math.sqrt(sum(float(p["error"]) ** 2 for p in ps) / len(ps))
        if not math.isclose(rmse, float(m["rmse"]), rel_tol=1e-12):
            raise ValueError("Saved RMSE does not match saved prediction errors")
    masks = defaultdict(set)
    for (model, outcome, year, h), ps in grouped.items():
        masks[(outcome, year, h)].add(tuple(sorted(p["target"] for p in ps)))
    if any(len(x) != 1 for x in masks.values()) or len(seen) != len(grouped):
        raise ValueError("Models do not use identical forecast targets")
    data["diagnostics"] = json.loads((SOURCE / "diagnostics.json").read_text())
    data["audit"] = json.loads((ROOT / "data/task04_regimes/data_audit.json").read_text())
    data["manifest"] = manifest
    data["coef"] = {(r["model"], r["term"]): r for r in c}
    data["metric"] = {(r["model"], r["outcome"], int(r["year"]), int(r["horizon"])): r for r in metrics}
    return data


def rmse_table(data, outcome):
    get = data["metric"]
    return table(["Model", "2025 · h=1", "2025 · h=3", "2026 · h=1", "2026 · h=3"],
                 [[m, *[number(get[(m, outcome, y, h)]["rmse"]) for y, h in PAIRS]] for m in MODELS])


def diagnostic_p(result, test):
    p = result[test]["p"]
    if test == "kpss" and p == .1 and any("greater" in w for w in result["warnings"]):
        return ">0.1000"
    if test == "kpss" and p == .01 and any("smaller" in w for w in result["warnings"]):
        return "<0.0100"
    return number(p, 4)


def tables(data):
    c, metrics = data["coef"], data["metric"]
    annual = []
    for r in data["decomposition.csv"]:
        annual.append([r["year"] + (" Jan–Sep" if r["months"] == "9" else ""),
                       number(r["Tesla_after"], 0),
                       number(100 * (float(r["Tesla_after"]) / float(r["Tesla_before"]) - 1), 1, True) + " %",
                       number(100 * (float(r["market_after"]) / float(r["market_before"]) - 1), 1, True) + " %",
                       number(100 * float(r["share_after"]), 2) + " %",
                       *[number(r[k], 0, True) for k in ("market_component", "share_component", "Tesla_change")]])
    specs = [
        ["M0", "Fixed market trend; constant relative brand levels", "0", "None"],
        ["M1", "Local market trend and relative brand levels", "0.03", "None"],
        ["M2 **primary**", "M1 + subsidy steps and transition pulses", "0.03", "Eligibility from January 2026"],
        ["M2_sd0.05", "M2; more flexible states", "0.05", "As M2"],
        ["M2_sd0.10", "M2; more flexible states", "0.10", "As M2"],
        ["M2_sd0.20", "M2; most flexible states", "0.20", "As M2"],
        ["M2_portal", "M2; alternative start for the 2026 subsidy", "0.03", "Portal opens in May rather than January 2026"],
        ["M2_logit", "M2; logit(BEV/passenger cars) instead of log(BEV)", "0.03", "As M2; seasonal-naive passenger-car forecast denominator"],
    ]
    calendar = []
    for m in MODELS:
        calendar.append([m, interval(c[(m, "Tesla:quarter_end")], mark=True),
                         interval(c[(m, "market:quarter_end")], mark=True),
                         interval(c[(m, "market:national_weekdays")], 4, mark=True),
                         interval(c[(m, "market:sin_12")], mark=True),
                         str(sum(excludes_zero(r) for r in data["coefficients.csv"] if r["model"] == m))])
    policy = []
    for m in MODELS[2:]:
        policy.append([m, *[interval(c[(m, "market:" + term)], mark=True) for term in
                           ("grant_cut_2023_01", "business_end_2023_09", "post_end_2024_01", "grant_2026_01")]])
    delta = []
    for outcome in ("BEV_market", "Tesla"):
        for y, h in PAIRS:
            row = metrics[("M2", outcome, y, h)]
            cells = ["BEV market" if outcome == "BEV_market" else outcome, y, h, row["n"]]
            for base in ("M0", "M1"):
                old = float(metrics[(base, outcome, y, h)]["rmse"])
                diff = float(row["rmse"]) - old
                cells.append(f"{number(diff, 1, True)} ({number(100 * diff / old, 1, True)} %)")
            delta.append(cells)
    contrasts = [[r["model"], interval(r),
                  "Fixed at zero" if r["model"] == "M0" else
                  "Negative; interval excludes zero" if excludes_zero(r) else "Interval includes zero"]
                 for r in data["contrasts.csv"] if r["group"] == "Tesla"]
    diag = []
    for m in MODELS:
        d = data["diagnostics"][m]
        t = d["innovations"]["1"]
        lb = min(x["p_holm"] for x in t["ljung_box"])
        vw = min(x["p_holm"] for x in d["innovations"]["2"]["ljung_box"])
        diag.append([m, diagnostic_p(t, "adf"), diagnostic_p(t, "kpss"),
                     f"{lb:.4g}", f"{vw:.4g}"])
    sources = "Source: preserved KBA FZ10 analysis of 29 October 2026; own presentation, no refitting."
    return f"""## 1. What actually changed

{table(['Year-on-year comparison', 'Tesla registrations', 'Tesla Δ', 'BEV market Δ', 'Tesla BEV share', 'Market component', 'Share component', 'Tesla absolute Δ'], annual)}

All comparisons use full years except **2026: January–September versus January–September 2025**.
In 2025, Tesla recorded 19,390 registrations versus 37,574; the BEV market recorded
545,142 versus 380,609. Tesla's BEV share fell from 9.87% to 3.56%. Market growth
arithmetically offsets part of its share loss. Tesla's share was already falling
in 2023. In 2026, both the market and Tesla's share rose against the low prior-year base.

![Tesla Germany: annual market and share components](results/task04/presentation/annual_market_share.png)

{sources} The symmetric decomposition adds up exactly before rounding:
`ΔTesla = mean(share) × Δmarket + mean(market) × Δshare`.
This is an accounting decomposition, not causal attribution.
The captions therefore avoid the unproven claim that a single subsidy event
caused the entire market decline.

![Monthly Tesla registrations and market/share decomposition](results/task04/stage1/market_share_decomposition.png)

Source: Kraftfahrt-Bundesamt, FZ10, own calculation. Policy markers provide
context; the globally reported Model Y changeover in Q1 2025 is not a precisely
dated German delivery event. Administrative counts receive no invented sampling intervals.

## 2. What the eight state-space models test

{table(['Model', 'Specification', 'Monthly level SD', 'Subsidy coding / distinguishing feature'], specs)}

Every specification includes one annual sine/cosine seasonal pair, quarter-end
and national weekdays net of nationwide public holidays. M0 sets all state
innovations to zero; the dynamic specifications retain slope SD 0.01. A larger
level SD permits more flexible latent states and changes how variation is
allocated, not the observed registration counts.

The joint system models the market, `log(Tesla/Rest)` and `log(VW/Rest)`;
Rest = official BEV market minus Tesla minus VW. **VW denotes the brand, not the group.**
All eight specifications were fixed before fitting the real data. The variant
with the best observed RMSE does not retrospectively replace the primary model.

## 3. Which drivers stand out statistically

Estimation is Bayesian. **† means that the conditional, pointwise 95% posterior
interval excludes zero.** This is neither a frequentist p-value nor a
multiplicity-adjusted significance test, and does not establish causality.
The following two tables cover every coefficient type meeting this criterion
in at least one specification; negative and unstable associations remain visible.
All **132 coefficients**, including posterior SDs and intervals containing zero,
are available in the [complete table appendix](results/task04/presentation/DETAILS.md).

### Calendar: median [95% posterior interval]

{table(['Model', 'Quarter-end Tesla/Rest', 'Quarter-end market', 'National weekdays: market', 'Sine seasonality: market', 'Total coefficients with †'], calendar)}

**The most stable measured association is Tesla quarter-end: positive in all eight
specifications.** This is consistent with delivery/registration waves. The primary
estimate {interval(c[('M2','Tesla:quarter_end')])} is in log-ratio units,
not a universal percentage effect on Tesla sales. VW quarter-end, all other VW
calendar terms, Tesla sine/cosine/weekday terms and market cosine terms include
zero in every specification. The market weekday association appears only with
larger level SDs; negative market sine seasonality appears only in the logit branch.

### Government subsidies: median [95% posterior interval]

{table(['Model', 'January 2023 cut', 'Business eligibility ends: September 2023', 'After subsidy end: January 2024', '2026 programme'], policy)}

M0/M1 contain no subsidy coefficients. The steps are **incremental coefficients
on cumulative indicator variables**, included only in the market equation.
In the portal specification, the final step starts in May 2026; the canonical
CSV term remains `grant_2026_01`. Logit coefficients describe log-odds of the
BEV share of the passenger-car market; the other market coefficients use log-count
units. They must not be compared as if they were the same elasticity.

The cut and the end of business eligibility are negative, with intervals excluding
zero in all six policy specifications. The post-end interval includes zero at
SD 0.20. **The 2026 programme interval includes zero in every specification**,
with changing signs. The December 2023 and January 2024 transition pulses also
include zero in every specification; the primary estimates are
{interval(c[('M2','market:transition_2023_12')])} and
{interval(c[('M2','market:transition_2024_01')])}, respectively.

The historical policy coefficients are conditional associations with compensating
trends/states. A negative coefficient identifies neither an isolated subsidy
effect nor its causal registration contribution.
[Primary sources and subsidy chronology](data/task04_regimes/policy_chronology.json).

## 4. How well do the models predict? RMSE for all eight specifications

RMSE = root mean squared prediction error, **in registrations per month; lower
is better**. At least 48 training months; strictly historical training prefixes.
h=1 covers twelve target months in 2025 and nine in 2026; h=3 covers ten in 2025
and nine in 2026. Three-month-ahead forecasts predict the third target month,
not the sum of the following three months. They overlap.
Here, 2026 always means January–September.

### Official BEV market

{rmse_table(data, 'BEV_market')}

### Tesla

{rmse_table(data, 'Tesla')}

![RMSE for all eight market and Tesla models, including deteriorations](results/task04/presentation/rmse_comparison.png)

{sources} Each cell shows RMSE and its percentage change from M0 on identical
target months; blue = smaller error, orange = larger error. Colours are not
significance tests. The shared colour scale saturates at ±60%; displayed numerical
values are not capped.

### What does the subsidy specification M2 add over the baselines?

{table(['Outcome', 'Year', 'h', 'n', 'RMSE M2 − M0 (relative)', 'RMSE M2 − M1 (relative)'], delta)}

**A negative difference indicates improvement; a positive difference indicates deterioration.**
Moving from M1 to M2 adds four subsidy steps and two transition pulses together.
It does not attribute a separate RMSE gain to any individual subsidy event.
There is also no specification without the quarter-end term: its isolated
incremental RMSE benefit has not been estimated.

M2 improves market forecasts over M1 in all four groups, but loses to M0 in 2025.
In 2026, the advantage over both baselines survives leaving each individual
target error out of the metric. The prespecified H-P rule requires that advantage
in both years and at both horizons; **H-P remains open**.
For Tesla, M1 outperforms M2 in 2025, and M0 outperforms M2 in 2026. Better market
forecasts therefore do not imply a general Tesla forecasting improvement.

The sensitivities produce no universal winner: SD 0.20 improves market RMSE
in 2026/h=1 but substantially worsens 2026/h=3 relative to the primary model.
The logit branch improves market forecasts in 2025 and uses a seasonal-naive
passenger-car denominator; its uncertainty is not additionally modelled.
M2 and portal are structurally identical in the 2025 training windows; small
differences arise from different fixed Monte Carlo seeds.

<details>
<summary>All eight models for VW and Rest</summary>

**VW:**

{rmse_table(data, 'VW')}

**Rest of the BEV market:**

{rmse_table(data, 'Rest')}

For VW too, M0 outperforms every dynamic specification in 2026.
Rest is an accounting remainder, not a measured China basket.

</details>

These are retrospective backtests using the current source vintage, not
historically reconstructed real-time forecasts. Future subsidy rules enter
only when known at the forecast origin. Wide intervals limit usefulness:
Tesla M2 2025/h=1 has a mean interval width of
**{number(metrics[('M2','Tesla',2025,1)]['mean_interval_width'])}** registrations,
against roughly 1,616 observed registrations per month.
The empirical hit rate of {number(100*float(metrics[('M2','Tesla',2025,1)]['coverage95']),1)}%
does not validate 95% coverage with twelve target months and such wide bands.
[All 128 metric rows](results/task04/stage1/metrics.csv) include MAE, MASE and
interval widths; [all 1,280 forecast rows](results/task04/stage1/predictions.csv) are preserved.

## 5. How robust is the latent Tesla level?

{table(['Model', 'Annual mean 2025 − 2024: Tesla/Rest level [95% interval]', 'Interpretation'], contrasts)}

![Stable quarter-end association and prior-dependent Tesla level contrast](results/task04/presentation/tesla_robustness.png)

{sources} The primary level-contrast interval includes zero; only the more
flexible SD specifications produce entirely negative intervals. The observed
share loss is undisputed, but its allocation to the latent level depends on the
model. M0 imposes a zero contrast; it is not empirical counterevidence.
A latent state measures neither brand image nor an isolated Model Y effect.

## 6. Stationarity, remaining errors and limits of the evidence

In the primary model, market target levels have ADF p=0.2961 / KPSS p=0.0454;
Tesla/Rest levels 0.0457 / 0.0178; VW/Rest 0.3160 / 0.0536.
The conflicting Tesla level tests do not permit a simple stationarity conclusion.
Target levels: 69 months, ADF effective n=65; fixed three lags and intercept/trend.

**One-step filter-innovation diagnostics for every specification:** after a
twelve-month burn-in, 57 values remain, ADF effective n=53; intercept and three lags.

{table(['Model', 'Tesla ADF p', 'Tesla KPSS p', 'Tesla min. Holm Ljung–Box p', 'VW min. Holm Ljung–Box p'], diag)}

The ADF null is a unit root; the KPSS null is level stationarity of the innovations.
Holm adjustment applies within the three Ljung–Box lags 3/6/12 for each series.
The minimum above summarises the full diagnostics, not a post-hoc choice of lag.
Complete raw/Holm values are in the [appendix](results/task04/presentation/DETAILS.md).

**Tesla retains persistence and serial correlation in the primary model; VW
retains strong serial correlation.** Larger SDs mitigate these findings but can
worsen forecasts. Numerical convergence does not establish model adequacy.
The primary market's smallest Holm-adjusted Ljung–Box p-value is 0.0928.

![Primary innovation ACF and filtered/smoothed state comparison](results/task04/diagnostics/innovation_acf.png)

Source: preserved KBA model innovations. Diagnostics condition on covariance
estimated over the full training window; these are not calibrated specification
tests. Smoothed states on the right use later observations; the displayed filter
curve also conditions on full-sample covariance. Neither is a historical live estimate.
The [scientific assessment](results/task04/SCIENTIFIC_REVIEW.md) includes unusual
months, changes in dispersion and alternative explanations.

A particularly important warning: in September 2026, `exp(mu)` of the
calendar/policy-adjusted market component in the primary model is 538,438,
with interval [215,782; 1,276,463], against 88,599 actual BEV registrations and
256,774 passenger cars in total. Large compensating state/subsidy terms make
this algebraic component **unsuitable as market potential or a causal
no-subsidy counterfactual**. The [original figure](results/task04/stage1/latent_market.png)
remains available.
"""


def details(data):
    text = """# Task 04: complete tables for the results README

Presented on 30 October 2026, using only the archived results from
29 October 2026. No model estimation or new hypothesis testing. Numbers here
are rounded; the original CSV/JSON files retain full numerical precision.

## All 132 coefficients

Posterior SD is the dispersion of the conditional posterior, not a HAC standard error.
† = pointwise 95% posterior interval excluding zero, with no claim of causality or
frequentist significance. All unmarked coefficients remain visible.
Market terms are in log counts, or log odds in the logit branch;
Tesla/VW terms are in log ratios to the rest group. In the portal branch, the canonical
term `grant_2026_01` applies from May, not January 2026.

"""
    for m in MODELS:
        rows = [r for r in data["coefficients.csv"] if r["model"] == m]
        text += f"### {m}\n\n" + table(["Term", "Median [95% interval]", "Posterior SD", "Months with active term"],
                 [[r["term"], interval(r, 4, mark=True), number(r["posterior_sd"], 4), r["observed_nonzero_months"]] for r in rows]) + "\n\n"
    text += "## All 128 forecast comparisons\n\nRMSE/MAE/width in registrations. MASE is scaled by seasonal naive training errors; no separately tested naive future forecast. Coverage rates are descriptive. A negative RMSE difference indicates improvement.\n\n"
    for m in MODELS:
        rows = [r for r in data["metrics.csv"] if r["model"] == m]
        text += f"### {m}\n\n" + table(["Outcome", "Year", "h", "n", "RMSE", "Δ M0", "Δ M1", "MAE", "MASE", "95% coverage", "Mean interval width"],
                 [[r["outcome"], r["year"], r["horizon"], r["n"], number(r["rmse"]), number(r["rmse_difference"], 1, True),
                   number(r["rmse_difference_vs_M1"], 1, True), number(r["mae"]), number(r["mase"], 3),
                   number(100*float(r["coverage95"]), 1)+" %", number(r["mean_interval_width"])] for r in rows]) + "\n\n"
    text += "## ADF, KPSS and Ljung–Box: all eight models\n\nADF/KPSS use a fixed three lags; levels include a trend, innovations include a constant after a twelve-month burn-in. Holm adjustment across the three Ljung–Box lags within each series. No diagnostic lags are selected.\n\n"
    for m in MODELS:
        rows = []
        for kind in ("levels", "innovations"):
            for j, group in enumerate(("Market", "Tesla/Rest", "VW/Rest")):
                r = data["diagnostics"][m][kind][str(j)]
                lb = r.get("ljung_box", [])
                rows.append([kind + " " + group, r["n"], r["adf"]["effective_n"], diagnostic_p(r, "adf"), diagnostic_p(r, "kpss"),
                             *[f"{v['p']:.6g} / {v['p_holm']:.6g}" for v in lb]] + (["—"]*3 if not lb else []))
        text += f"### {m}\n\n" + table(["Series", "n", "ADF eff. n", "ADF p", "KPSS p", "LB 3 raw / Holm", "LB 6 raw / Holm", "LB 12 raw / Holm"], rows) + "\n\n"
    text += "Originals: [Coefficients](../stage1/coefficients.csv), [Metrics](../stage1/metrics.csv), [Diagnostics](../stage1/diagnostics.json), [Manifest](../stage1/manifest.json). [Back to README](../../../README.md).\n"
    return text


def figures(data):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "svg.hashsalt": "task04-german-results-v1"})
    files = {}

    def save(fig, name):
        for ext in ("png", "svg"):
            buf = io.BytesIO()
            fig.savefig(buf, format=ext, dpi=160, metadata={"Software": "Matplotlib"} if ext == "png" else {"Date": None})
            files[f"{name}.{ext}"] = buf.getvalue()
        plt.close(fig)

    r = data["decomposition.csv"]
    market = np.array([float(x["market_component"]) for x in r])
    share = np.array([float(x["share_component"]) for x in r])
    total = np.array([float(x["Tesla_change"]) for x in r])
    x = np.arange(len(r))
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.subplots_adjust(left=.11, right=.97, top=.77, bottom=.20)
    fig.text(.055, .94, "Tesla in Germany: market or brand?", fontsize=24, weight="bold")
    fig.text(.055, .89, "Year-on-year change, arithmetically decomposed into market and share components", fontsize=12, color="#444444")
    ax.bar(x, market, .52, color=GOLD, label="Market component (BEV market)")
    ax.bar(x, share, .52, bottom=np.where(market*share > 0, market, 0), color=BLUE, label="Share component (Tesla BEV share)")
    ax.scatter(x, total, color="black", marker="D", s=65, zorder=4, label="Total change")
    for i, value in enumerate(total):
        ax.annotate(number(value, 0, True), (i, value), xytext=(12, 0), textcoords="offset points", fontsize=12, weight="bold", va="center")
    ax.axhline(0, color="black", lw=.8)
    ax.set_ylim(-41000, 40500)
    ax.set_xlim(-.5, 4.85)
    ax.set_xticks(x, ["2022", "2023", "2024", "2025", "2026\nJan–Sep"])
    ax.set_ylabel("Change in new Tesla registrations")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, pos: number(value, 0, True)))
    ax.grid(axis="y", alpha=.25); ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, 1.19), ncol=1, frameon=False, fontsize=10)
    fig.text(.055, .09, "Source: Kraftfahrt-Bundesamt, FZ10; own calculation, dl-de/by-2-0. 2026: same nine months in each year.", fontsize=9, color="#555555")
    fig.text(.055, .055, "Exact symmetric accounting decomposition before rounding; no causal attribution or isolated subsidy-effect estimate.", fontsize=9, color="#555555")
    save(fig, "annual_market_share")

    fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharey=True)
    fig.subplots_adjust(left=.13, right=.94, top=.78, bottom=.19, wspace=.12)
    for ax, outcome, title in zip(axes, ("BEV_market", "Tesla"), ("BEV market", "Tesla")):
        values = np.array([[float(data["metric"][(m, outcome, y, h)]["rmse"]) for y, h in PAIRS] for m in MODELS])
        delta = 100 * (values / values[0] - 1)
        cmap = LinearSegmentedColormap.from_list("rmse", [BLUE, "#FAFAFA", "#B25D00"])
        ax.imshow(delta, cmap=cmap, norm=TwoSlopeNorm(vmin=-60, vcenter=0, vmax=60), aspect="auto")
        for i in range(8):
            for j in range(4):
                ax.text(j, i, number(values[i,j], 0)+"\n"+number(delta[i,j], 1, True)+" %", ha="center", va="center", fontsize=10,
                        color="white" if abs(delta[i,j]) > 35 else "black")
        ax.set_title(title, fontsize=15, pad=14)
        ax.set_xticks(range(4), ["2025\nh=1", "2025\nh=3", "2026\nh=1", "2026\nh=3"])
        ax.set_yticks(range(8), [m + (" *" if m == "M2" else "") for m in MODELS])
    fig.suptitle("All eight models: forecast error and change from M0", fontsize=19, y=.95)
    fig.text(.13, .87, "Each cell: RMSE in registrations / relative change. Lower error: blue; higher error: orange.", fontsize=10)
    fig.text(.13, .09, "Source: archived KBA-FZ10 backtests. * Primary model. 2026: January–September; identical target months.", fontsize=9)
    fig.text(.13, .055, "Color scale saturated at ±60%; numbers unchanged. Retrospective, with no causality or significance assessment.", fontsize=9)
    save(fig, "rmse_comparison")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    fig.subplots_adjust(left=.15, right=.97, top=.77, bottom=.2, wspace=.25)
    contrasts = {r["model"]: r for r in data["contrasts.csv"] if r["group"] == "Tesla"}
    for ax, title, getter in ((axes[0], "Tesla quarter-end", lambda m: data["coef"][(m, "Tesla:quarter_end")]),
                              (axes[1], "Latent Tesla level: 2025 minus 2024", lambda m: contrasts[m])):
        for i, m in enumerate(MODELS):
            row = getter(m); med, lo, hi = (float(row[k]) for k in ("median", "lower95", "upper95"))
            ax.errorbar(med, i, xerr=[[med-lo], [hi-med]], fmt="D" if m == "M2" else "o", color=BLUE if excludes_zero(row) else "#777777", capsize=3, ms=6)
        ax.axvline(0, color="black", lw=.8)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("Tesla/rest log-ratio units")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, pos: number(value, 1)))
        ax.set_yticks(range(8), MODELS); ax.grid(axis="x", alpha=.2)
    axes[0].invert_yaxis()
    fig.suptitle("Robust calendar association, model-dependent level contrast", fontsize=18, y=.95)
    fig.text(.15, .86, "Median and pointwise conditional 95% posterior interval; diamond = primary model M2.", fontsize=10)
    fig.text(.08, .09, "Source: archived KBA-FZ10 analysis. Blue: interval excludes zero; gray: includes zero. No causal claim.", fontsize=9)
    fig.text(.08, .055, "M0, right: zero contrast fixed by construction. The primary level SD of 0.03 is not changed retrospectively.", fontsize=9)
    save(fig, "tesla_robustness")
    return files


def run(check=False):
    data = load()
    readme = ROOT / "README.md"
    text = readme.read_text()
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Expected exactly one presentation section")
    before, tail = text.split(BEGIN)
    _, after = tail.split(END)
    computed = BEGIN + "\n\n" + tables(data).strip() + "\n\n" + END
    expected_readme = before + computed + after
    outputs = {"DETAILS.md": details(data).encode(), **figures(data)}
    source_paths = [SOURCE / name for name in ("manifest.json", "coefficients.csv", "metrics.csv", "decomposition.csv", "contrasts.csv", "predictions.csv", "diagnostics.json")]
    source_paths += [ROOT / "data/task04_regimes/data_audit.json", Path(__file__)]
    manifest = {
        "scope": "English presentation only; no model fits, changed protocols, new observations or new significance tests",
        "original_execution_commit": data["manifest"]["execution_commit"],
        "protocol": data["manifest"]["protocol"]["version"],
        "source_sha256": {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in source_paths},
        "computed_readme_section_sha256": sha(computed.encode()),
        "matplotlib": matplotlib.__version__, "numpy": np.__version__,
        "files": {name: sha(content) for name, content in outputs.items()},
    }
    outputs["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    if check:
        if text != expected_readme:
            raise ValueError("README tables/narrative differ from saved-output presentation")
        for name, content in outputs.items():
            if not (OUTPUT / name).exists() or (OUTPUT / name).read_bytes() != content:
                raise ValueError("Presentation differs: " + name)
    else:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        readme.write_text(expected_readme)
        for name, content in outputs.items():
            (OUTPUT / name).write_bytes(content)
    nonzero = sum(excludes_zero(r) for r in data["coefficients.csv"])
    print("Verified" if check else "Presented", f"132 coefficients, all {nonzero} intervals excluding zero, 128 RMSE rows recomputed from 1280 saved predictions; no fits.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args().check)
