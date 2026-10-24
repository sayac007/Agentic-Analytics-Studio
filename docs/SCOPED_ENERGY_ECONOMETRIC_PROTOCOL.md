# Task 01I.3 — frozen scoped private energy protocol

Version 1.0.0; 2026-10-24. Preregistered from main merge
`2f644e4ba85731aef023a82b4378043f52c1f00b`, **before any real cross-series join,
plot, correlation or fit**. Commit this document alone first. Its exact byte hash is
required in every run. No later methodological edits or result-driven alternatives.
This is the separately authorised Task 01I.3, not Task 01J or an amendment of Task 01G.

## Purpose, permission and information timing

Ask whether German diesel prices and EUR/USD have descriptive and conditional
predictive associations with Tesla registrations. No identified oil shock, exogenous
instrument, advertising effect, ROI or causal effect. Substitution and purchasing-power
channels may have opposite signs; no expected sign or significance target.

Use **only** admitted ECB monthly `EXR.M.USD.EUR.SP00.A` (USD per EUR) and qualified
EC German automotive diesel with taxes, monthly calendar-overlap approximation
(EUR/litre). Check the merged source-specific rights matrix, actual private permits,
original/native/monthly hashes, keys, units, human decision evidence, qualified
limitations and all source-integrity gates before numeric outcome access. The
separate user workorder authorises this scope; a permit's `task_01j_authorized=false`
is retained, not changed into Task 01J permission. Refuse RBRTE/Brent and all other
energy variables, ratios/proxies or new controls. No 2026 appendix in this increment.

KBA Tesla brand **all-powertrain new registrations**, count units, is the sole outcome.
Use its unchanged audited official series, retrospective immutable source/rights
admission, and this workorder's authorisation as an observed research outcome.
Generator-reference admission alone is not a causal or econometric validation. No
BEV-only reinterpretation, Toyota/VW outcome search, BEV share or unverifiable denominator.
Historical KBA/as-of restrictions remain. Search, order, delivery and registration
months represent different stages; monthly registration associations cannot date orders.

All empirical rows, results, estimates, plots and numerical report content stay in
new private directories outside Git. Public reporting is status/methods only. Source
attribution, change notices, EC scope limitations and missingness are preserved.
Current retrospectively downloaded/revised snapshots are **not historical real-time
information**, even with a lag. No public redistribution or historical as-of approval.

## Fixed calendar, variables and missingness

Exactly 2018-01–2025-12, 96 unique consecutive calendar slots. One-to-one period
alignment is checked before calculation. Reject duplicates, wrong source/unit,
nonfinite/nonpositive energy values and negative/noninteger counts. Native source
rows outside the window are excluded by documented calendar selection, never spliced.
Retain original energy scales; no standardisation, rescaling or outcome-based trimming.

Retain missing diesel at: 2018-04, 2018-12, 2019-01, 2019-04, 2019-12, 2020-01,
2020-04, 2020-12, 2021-01, 2021-04, 2021-12, 2022-01, 2022-04. No fill/interpolation,
bridging, zero substitution or compressed-time differencing. Full FX sample and
complete-case diesel samples are separate; never restrict FX to diesel availability.
At each lag report exact eligible months, effective n and exclusions. A difference
requires both actual adjacent months; a lag is an actual calendar shift.

Outcome: original count for plots/count error, `z[t]=log1p(count[t])` for modeling.
Primary association: `Delta z[t]` on `Delta x[t-k]`. A single prespecified robustness
alternative uses `z[t]` on `x[t-k]`. Diesel differences are EUR/litre changes; FX
differences are USD-per-EUR changes. Coefficients are log1p units per original energy
unit (or changes thereof), not elasticities or percentage effects. Log1p handles zeros.
Levels may produce spurious association in trending/broken processes; differences
do not remove all confounding or guarantee stationarity.

## Calendar baseline and fixed lag grid

All association models have intercept, **11 month-of-year indicators** (January
reference) and a linear month trend `t=0..95` on the original calendar; then add
**one energy predictor** at a time at one lag. No quarter-end dummy with month
indicators, extra break dummies, Google attention or post-hoc model selection.

For each source and transformation fit separate lags **0,1,2,3 primary** and **4,5,6
sensitivity**. Positive k means `x[t-k] -> y[t]`. Do not search/select a winner or
combine all lag terms. Fit baseline and augmented model on identical eligible rows.
Require full design rank, finite calculations, condition number reported and at
least **20 residual degrees of freedom** in each fitted specification; otherwise
report `not_estimable` with reason, not another specification.

Conditional OLS via NumPy least squares. Newey–West HAC, **three calendar-month lags**,
Bartlett weights `1-h/4`, covariance correction `n/(n-p)`, two-sided normal 95%
intervals/p-values. For irregular complete-case diesel samples, sum residual-score
cross-products only where **original calendar indices differ by h**. Never treat
observations separated by missing months as consecutive HAC periods. Contiguous
results must agree with the standard corrected three-lag implementation. Record
rank, condition and df. Intervals are conditional, asymptotic and not causal; short
samples, misspecification/breaks and heteroskedasticity/autocorrelation limit inference.

Holm adjustment across **all 28** source × transformation × lag coefficient tests,
including the robustness family. A not-estimable model occupies its prespecified
family slot with p=1 for adjustment, but its adjusted result remains null. No reduced
family chosen after seeing fits. Descriptive cross-correlations use the same primary
paired calendar values at each lag, report n and Pearson r only, **no additional
inferential p-values**. They are not conditional regression or causal identification.

## Fixed diagnostics, seasonality and structural instability

Plot each original/transformed series separately, show missing slots and shade 2022
as descriptive only. Tabulate calendar-month means with counts (trend-confounded),
levels, differences and missingness. No deseasonalisation learned on holdout outcomes.

ACF/PACF and ADF/KPSS are computed on each series/transform's **longest contiguous
finite monthly segment**, earliest segment on a tie, with bounds and n recorded.
This is essential for diesel: do not concatenate disjoint months. If fewer than 27
months, constant or invalid, report not estimable without selecting other lags.
ACF lags 0–12, non-FFT, Bartlett pointwise 95% intervals; PACF `ywm`, lags 0–12 with
pointwise asymptotic intervals. These require suitable stationary short-memory
behavior and are not simultaneous bands or evidence that a broken series is stationary.

ADF: fixed augmentation **3**, no autolag; `ct` for levels/log levels and `c` for
changes. Null unit root. KPSS: fixed **3**, same deterministic choice, null trend
stationarity (ct) or level stationarity (c). Preserve warnings/p-value bounds and
critical values. Neither test definitively classifies a short/broken process and
neither triggers specification changes. No diagnostic-based lag/control searching.

Structural stability: predeclared CUSUM-of-OLS-residuals diagnostic on the full
calendar-only **log1p outcome** baseline (`ddof=p`), report statistic/p-value/critical
values with the warning that its usual calibration is not repaired by HAC and may
be unreliable under serial correlation/heteroskedasticity. No breakpoint search or
response-selected dummies. Show the 2022 window and energy gaps; do not label it an
identified Ukraine/oil treatment or infer a general effect from a single episode.

## Fixed retrospective 2025 pseudo-holdout

Separate from coefficient-test family: fit **level log1p outcome** calendar baseline
versus that baseline plus a single energy-level predictor at **lag 1**, independently
for FX and diesel. This lag is fixed prospectively, not selected from associations.
Training ends 2024-12, holdout is all 12 months of 2025. Eligibility is the identical
lag-1 source mask for baseline/augmented comparison. Require every holdout predictor
and all outcome months available, full rank and >=20 training residual df; otherwise
mark that comparison not estimable. No alternate holdout/window/lag.

Fit coefficients and all learned quantities on training only. Report log1p-scale
RMSE and original-count RMSE. Count-scale prediction is `expm1(predicted log1p)`
without clipping or holdout-based smearing; flag negative predictions if present.
This is a transformed conditional predictor, not an unbiased expected-count estimate.
Holdout outcomes enter scoring only. Full-window descriptive/association outputs
include 2025 under the already frozen specification; they never feed model selection.

This is **retrospective conditional prediction**, not a real-time historical forecast
or independent untouched prospective validation. The vintage and even lagged realised
energy inputs lack verified historical availability. No causal or marketing benefit
follows from incremental RMSE; no confidence interval for RMSE differences is invented.

## Interpretation and stop conditions

Subsidy changes, Tesla prices/launches, supply, model mix, macro conditions and
endogenous Google attention remain unmodelled. Do not add them after residuals or
significance; they require separate admission/preregistration. Calendar controls and
HAC cannot establish exogeneity. Keep null/negative results, instability warnings and
failed fits visible in the private report, without adjusting specifications.

No Brent, 2026 outcome comparisons, BEV experiment, Task 01J execution, Task 01G edit,
new causal identification, ROI or public empirical values. Refuse failed input,
admission, hash, series/unit, protocol identity or privacy gates before fitting.
Source/protocol failures produce no completed study artifact; individual numerical
not-estimable results are reported under the fixed protocol, never silently omitted.
