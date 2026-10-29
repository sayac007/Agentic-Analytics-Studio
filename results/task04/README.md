# Task 04: Stage 1 scientific archive

This directory separates the **small synthetic model check** in `recovery/` from the **observed KBA analysis** in `stage1/`. Synthetic outcomes never replace real registrations. No private energy, Trends, credentials or permit files are Stage 1 inputs.

## Freeze and sources

The normative protocol is [`task-04-regimes/1.0.0`](../../docs/REGIME_STATE_SPACE_PROTOCOL.md). The [freeze record](../../data/task04_regimes/freeze.json) binds its SHA-256, configuration and original commit **before the first real fit**. The configuration binds every source and calibration input by SHA-256. Preserve the frozen commit in the Git history when merging.

Observations: existing public KBA-derived monthly registrations, January 2021–September 2026. Rest is the official BEV market minus Tesla and Volkswagen **brand**. Missing brand observations are never converted into zero. See the [audit](../../data/task04_regimes/data_audit.json) and [catalog](../../data/competition/kba_sources.json). Attribution: Kraftfahrt-Bundesamt, Flensburg, FZ10, own calculation, Datenlizenz Deutschland – Namensnennung – Version 2.0.

The [policy chronology](../../data/task04_regimes/policy_chronology.json) records primary sources actually consulted, content hashes, effective dates and historical announcement precision. Primary snapshots remain outside Git. Unknown exact announcement timestamps remain unknown.

## Reproduce or verify

Requires Python 3.12, complete Git history and writable temporary space. Use a new output directory. Raw posterior checkpoints must stay outside the repository. Four CPU chains are used; this is a full study, not a short CI smoke test.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-regimes.lock
JAX_PLATFORMS=cpu OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m regimes.study \
  --output /tmp/task04-new-results \
  --checkpoint /tmp/task04-private-checkpoints
.venv/bin/python -m regimes.verify /tmp/task04-new-results
.venv/bin/python -m scripts.task04_diagnostics /tmp/task04-new-results \
  --output /tmp/task04-new-diagnostics
```

Read-only verification of preserved results, **without fitting**:

```sh
.venv/bin/python -m regimes.verify results/task04/stage1
```

The manifest binds output bytes, input hashes, package-source hashes, execution commit, software versions and freeze record. Pinned seeds/environment permit reproduction; bit-identical floating-point results on different hardware are not promised.

## Outputs

| File | Meaning |
|---|---|
| `report.md`, `hypotheses.csv` | Computed findings, negative results and open hypotheses |
| `decomposition.csv` | Exact annual / matched YTD observed accounting, no invented intervals |
| `model_decomposition.csv` | Joint-draw latent intensity accounting with marginal posterior intervals |
| `coefficients.csv`, `contrasts.csv`, `states.csv` | All conditional coefficients, annual contrasts and states |
| `predictions.csv`, `metrics.csv` | All prespecified rolling forecasts and model comparisons |
| `diagnostics.json` | Full-window MCMC, design rank, ADF/KPSS and innovations |
| `rolling_inference.json` | Each training-prefix diagnostic, importance update or NUTS refresh |
| `frequentist_reference.json` | Same-Gaussian-initialization marginal ML reference, including failures |
| Three PNG/SVG pairs | Market/share changes and uncertain smoothed levels |
| `manifest.json` | SHA-256 and execution provenance |

The separate read-only `scripts.task04_diagnostics` command completes the
protocol's ACF graphic, descriptive largest-innovation and annual-variation
checks for all eight models. It recomputes conditional innovations from the
saved posterior mean covariance, with the same filter and fixed twelve-month
burn-in; it neither fits parameters nor changes observations. All 57 remaining
months stay in the analysis. The five largest absolute innovations per series
are descriptive, not a rule for deletion or a calibrated outlier test. Annual
windows have twelve months, except the nine observed months of 2026. The primary
ACF has fixed lags 1–12, without a post-hoc lag search or claimed test calibration.
Its second column separates smoothed state bands from conditional filtered
means; both condition on full-window covariance estimation and must not be
called historical real-time states. `forecast_covariates.csv` makes every
forecast's design path explicit, including intervening months and zero policy
entries for future interventions not yet known at that origin.

Observed accounting and uncertain latent decompositions answer different questions. The latter excludes observation noise; joint-draw component means add, marginal interval endpoints need not. The latent market graphic excludes calendar/policy terms and is not the total fitted market.

All eight fixed specifications, both horizons, both years and unfavourable results remain visible. Current-vintage reference-month backtests are retrospective, not publication-lag-correct real-time forecasts. Innovations use marginal prediction variances, not smoothed residuals. Overlapping three-month errors are dependent.

## Limits known before real fits

The recovery check used four artificial cases and three level SDs. All twelve fits converged, but every policy interval also included zero. SD 0.03 had the smallest planned mean absolute error by a small margin; this does **not** establish true state variance or a causal subsidy effect. No validated power, continuous MDE or frequentist 95% coverage is claimed.

A Tesla-relative decline does not identify brand controversy, Model Y changeover, price competition or delivery constraints as its cause. Fuel, diffusion and the unresolved China basket are outside Stage 1.

## Execution record (29 October 2026)

The initial real-data orchestration at `2c23a515e214b6471c1a6a39562828b80ad18e08`
completed M0, M1, M2 and M2 SD 0.05. It was stopped to complete two already
required outputs: training-window diagnostics and joint-draw decomposition
intervals. No protocol, configuration, sampler, likelihood or forecasting
arithmetic changed. The final orchestration at
`75a7d266bbf9632ae0292a004a1eb87975dfcb09` reused those four hash-checked
checkpoints, then continued the remaining prespecified work. This is a technical
restart, not a new specification or a selection between alternative results.

Executed local checks: **476 tests passed** (`unittest discover -s tests -v`,
351.631 s); the targeted Regime suite passed **23 tests** (28.298 s).
`pip check` reported no broken requirements. The existing Task 02 verifier
confirmed 18,000 truth rows, 36,000 evaluations and 36 summaries. All ten
Task 02 files, both frozen empirical protocols and the hash-bound Task 01I.3
authorization were compared byte-for-byte against the approved starting main
(`2bd964ea373aeac9519349bb1228ad14a4fa6501`) and are unchanged.



## Completed observed results

The [scientific assessment](SCIENTIFIC_REVIEW.md) reports the full findings and
important failures. M2 improves the market forecasts against both baselines in
2026, but loses against M0 in 2025. Tesla's primary innovations retain persistence
and serial correlation; VW innovations retain strong autocorrelation. The latent
Tesla decline depends materially on the state SD. The large algebraic market
baseline is not market potential or a valid no-subsidy counterfactual.

The complete real execution passed before any reader changes. The subsequently
hardened read-only verifier binds the original freeze-commit configuration,
result/input identities, every required payload and coherent forecast means.
The 4 mathematical checkpoint-core modules and frozen statistical definitions
remain unchanged. A full local suite passed **483 tests in 309.328 s**. After the
presentation-only correction, all **5 artifact/freeze negative tests passed**
(0.360 s), and the preserved-result verifier passed again.

Visual inspection found an accounting-bar width bug: NumPy month dates interpreted
numeric width 22 as months. Only its PNG/SVG were re-plotted using explicit days.
All 16 other Stage1 payloads and every diagnostic payload are byte-identical;
no observation, coefficient, prediction or interval changed and no model was
refit. The manifest records original/corrected hashes and the source correction.
The diagnostic manifest's source binding was updated solely for that presentation
change, with its original binding retained in metadata.
