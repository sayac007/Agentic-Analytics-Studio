# Task 01G — frozen exploratory attention protocol

Version 1.0.0, specified **before any cross-series results** on 2026-10-24.
Base: merged PR #9, `9013913bbca7f60efe7226ad797e15d16d9d90ae`.
This document is committed before implementing/running the diagnostic CLI. Its hash
is recorded in every run. No empirical relationship has been inspected to select it.

## Hard admission gate

Use only the original private native monthly Trends export and importer 1.1.0 with
actual exact offset-aware retrieval evidence, exporter attestation and an explicit
review statement confirming lawful private analysis under Google/export conditions.
A checkbox/hash/URL does not independently verify legal rights; a human must review
source and rights evidence. Republishing values requires a separate decision.
The original file's exact download time is **unknown**: "today and now" on October 23
is not an exact instant. No substitute upload time or invented seconds are admitted.
The present run therefore remains pending unless a newly timestamped official export
and rights confirmation are supplied. Neither fixture data nor the existing screenshot
can bypass this gate. No empirical statistics are computed on pending inputs.

The CLI revalidates raw bytes and metadata through the existing importer, compares
all source/subset bytes and declared hashes against deterministic re-derivation, and
requires a separate human admission record bound to the raw/metadata hashes. In real
mode the KBA file must be the unchanged, audited repository series; fixture mode uses
only explicitly synthetic Trends and KBA fixtures. No cross-mixing is allowed.

## Samples, units and exclusions

- Primary window: 2018-01–2025-12, 96 consecutive unique months.
- Separate common-window view: 2021-01–2025-12, 60 months; Tesla outcome again, not
  an invented pre-2021 BEV total or an additional unreviewed outcome.
- Outcome: KBA **Tesla brand new registrations**, count units, not sales/orders/deliveries.
- Attention: literal Tesla search term, DE Web Search, all categories; sampled
  request-relative 0–100 index on the **original whole-export scale**. Not absolute
  searches, reach, spend, favorability or causal advertising exposure.
- Retain the original export privately; row-select subsets without rescaling or
  splicing. A full history exported in 2026 can use post-2025 information for scaling.
- Reject duplicate, unordered, missing, blank, censored or nonfinite modeling values;
  reject incomplete-month rows. Do not silently fill, average or interpolate. `<1`
  can remain censored in acquisition but needs a separately reviewed analysis policy.
- Validate exact one-to-one monthly join before any statistics. No 2026 KBA analysis.

## Fixed descriptive diagnostics

For each window, plot separate levels panels for registrations, log1p(registrations)
(as a distinct sensitivity view) and Trends. Plot calendar-month and quarter mean
profiles of the two levels, labeled descriptive and potentially trend-confounded.
Shade 2022 only as a descriptive event window. No oil/policy series is verified here;
no Ukraine-war oil-shock or 2026 Iran-war attribution is made.

Compute ACF/PACF at lags 0–12 for registrations, log1p(registrations), Trends and first
differences of each. ACF: non-FFT, Bartlett pointwise 95% intervals; PACF: Yule–Walker
maximum-likelihood (`ywm`), asymptotic pointwise 95% intervals. These intervals assume
suitable stationary short-memory behavior; they are not valid evidence of stationarity
for trending/broken series and are not simultaneous confidence bands.

ADF: fixed 3 augmentation lags, **no autolag search**, `ct` deterministic terms for
levels/log levels and `c` for first differences; null is a unit root. KPSS: fixed 3
lags, `ct` for levels/log levels and `c` for differences; null is trend/level
stationarity respectively. Record test statistics, p-value bounds/warnings, critical
values, lags and sample sizes. Small samples and structural breaks limit both tests;
a slowly decaying ACF alone does not prove a unit root. No seasonal/break unit-root
extensions, repeated specification search or opportunistic alternative models.

Flag spurious-level-regression risk when ADF does not reject at 5% or KPSS rejects
at 5% for either level series; this is a conservative descriptive warning, not a
binary proof. Even favorable tests do not establish causality or reliable inference.

## Fixed associations and uncertainty

Primary association family uses **first differences** of registrations and Trends,
not a naive levels causal regression. Positive lag k means attention change at t-k
is associated with registration change at t. Run separate single-lag models for
k=0,1,2,3; k=4,5,6 are explicitly sensitivity only. Use a common trimmed sample per
window: first difference loses one month, lag 6 loses six more; expected n=89/53.
Each model controls intercept, linear month trend, annual Fourier order 1 (sin/cos)
and quarter-end dummy. No choice is based on p-values or holdout fit.

OLS via NumPy least squares; Newey–West HAC covariance with Bartlett weights,
**3 lags**, finite-sample covariance correction, normal 95% intervals. Report original
units, standard errors, n, raw p-values and Holm-adjusted p-values across **all 14**
window-by-lag tests (not separate favorable subfamilies). These are exploratory,
conditional, multiple-tested associations; adjustments do not repair confounding,
short-sample uncertainty, omitted dynamics or model misspecification.

Quarter ends enter prospectively. Price cuts, subsidy termination, launches, supply
constraints and other breaks are known potential confounders but **no independently
reviewed dated control series is supplied**. They remain explicitly unmodeled; no
policy dummy is fabricated or added after looking at residuals/significance. Fourier
seasonality is parsimonious and may leave monthly patterns. Month dummies are not
combined with a collinear quarter-end dummy.

## Fixed retrospective pseudo-holdout comparison

Reserve January–December **2025**. Fit on earlier months in each window, losing the
first three months to declared attention history. Compare the identical calendar
baseline above against that baseline plus contemporaneous/lagged Trends **0–3 jointly**.
No lag selection. Center/scale attention with pre-2025 mean/sample SD only and reuse
that scale for holdout/historical lags. Reject constant/rank-deficient fits.
Report n/train boundaries, coefficients, monthly predictions and test RMSE for both.
No confidence interval for their paired RMSE difference is invented.

This is a **retrospective conditional pseudo-holdout**, not a genuine forecast or
historical real-time backtest: contemporaneous realized attention and a 2026 vintage
are not available for a month-ahead prediction origin. Full-window Google scaling
may also include later observations. Preprocessing/model fit never reads holdout
outcomes, but no actual historical availability claim follows. The primary comparison
uses count levels for descriptive error, with an explicit nonstationarity warning;
no naive levels coefficient is presented as causal. Diagnostics do not trigger model
changes. Log1p is a plotted diagnostic sensitivity, not another selected winner.

Future differenced/ARDL/VAR/local-projection work needs a separately reviewed
stationarity/break/identification design. Reverse causality is central: launches,
registrations and publicity can generate searches. No marketing effect, ROI,
experiment calibration, MMM extension, causal claim or repeated simulation.

## Outputs and reproducibility

All real raw/derived values, plots, tables and reports stay in a new private directory
outside Git. Record input hashes, protocol hash, source normalization, versions,
admission decisions, date windows and warnings. Save machine-readable calculations
and standalone plots. Numerical replay must be deterministic at pinned versions.
Public documentation reports only actually completed stages and blockers; no real
values are published without separate authorization. Synthetic fixture output is
prominently `SYNTHETIC_FIXTURE_ONLY`, never empirical results, power or effect recovery.

Existing KBA as-of blocks, Statistical Contracts, Stage-A benchmarks and estimator
isolation stay unchanged. This exploratory CLI is outside that MMM estimator interface.
