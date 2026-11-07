# Multi-brand BVARX protocol `multibrand-bvarx/1.0.0`

Frozen **before** any fit on real data. Committed alone; the runner refuses to run
if this file's SHA-256 differs from the value recorded in its output manifest at
execution. Changes after the first real fit require a new version number and are
reported as deviations.

Mandate: repository owner, 2026-11-07 — all incentive programmes as monthly
dummies, fuel price as an endogenous variable, other prices as exogenous variables;
other choices at the implementer's discretion (work order 05).

## 1. Data (all versioned in this repository)

| Block | Series | File |
|---|---|---|
| Outcomes | Official BEV registrations; BEV registrations of Tesla, VW Group (VW, AUDI, SKODA, SEAT, PORSCHE), BMW Group (BMW, MINI), Mercedes, Hyundai-Kia (HYUNDAI, KIA); Rest = official total minus groups | `data/competition_vintage_2026_11/` |
| Fuel (endogenous) | Euro-super 95, Germany, incl. taxes, **mean of bulletins dated in the month** (complete 70/70) | `data/fuel_prices_de/monthly.csv` |
| Prices (exogenous) | HICP electricity (CP0451) and new motor cars (CP07111), Germany, 2025=100 | `data/hicp_de/monthly.csv` |
| Policy (exogenous) | `innovation_premium`, `grant_2023_all`, `grant_2023_private`, `tax_package_2025_07`, `grant_2026` (day shares), pulses `pre_cut_2022_12`, `pre_business_end_2023_08` | `data/policy_regimes_de/` |
| Calendar (exogenous) | sin/cos annual pair, quarter-end month, national working days (definitions of `regimes.data.calendars`) | code |

Chinese brands are **not** a group: several are reported only inside KBA `SONSTIGE`
in 66 of 69 months, so an exact monthly series does not exist. They remain in Rest.

Estimation sample: **2021-01 – 2026-09 (69 months)**, the last month with all
exogenous prices. October 2026 is used only as an out-of-sample target.

## 2. Model

Endogenous vector (k = 7), in this order:
`log_fuel, log_market, alr_Tesla, alr_VW_Group, alr_BMW_Group, alr_Mercedes, alr_Hyundai_Kia`,
with `alr_g = log(group_g / Rest)`.

VARX(1): `y_t = A y_{t-1} + B x_t + e_t`, `e_t ~ N(0, Σ)`, where `x_t` holds the
14 exogenous terms (intercept, 4 calendar, 7 policy, 2 log prices). All equations
share the regressors.

Prior: conjugate normal–inverse-Wishart (Kadiyala–Karlsson Minnesota form).
- Prior mean of `A`: 0.9 on the own lag, 0 elsewhere.
- `Var(B_all[:, i]) = Σ_ii · Ω0` with `Ω0` diagonal: lag of variable j:
  `λ² / s_j²`; exogenous term m: `(10 / sd(x_m))²` (intercept: `10²`), i.e.
  effectively uninformative. `λ = 0.2`.
- `s_j²`: residual variance of a univariate AR(1) with intercept on the
  estimation window.
- `Σ ~ IW(S0, ν0)` with `ν0 = k + 2`, `S0 = diag(s²)`.
- 4,000 exact posterior draws, seed `20261107`.

## 3. Reported quantities (all reported, including nulls)

1. **Coefficients** of the 7 policy and 2 price terms in every equation:
   posterior median and 95 % interval; † when the interval excludes zero.
   Interpretation is conditional association relative to the baseline
   January 2024 – June 2025.
2. **Fuel shock.** Recursive (Cholesky) identification with `log_fuel` first:
   German BEV registrations are assumed not to move the EU-reported German fuel
   price within the same month. Only the fuel shock is interpreted; the ordering
   of the other variables is irrelevant for it. Impulse responses of all variables
   to a one-standard-deviation fuel shock, h = 0 … 12, 95 % bands, plus the
   cumulative 12-month response.
3. **Forecast evaluation**, expanding window from 2021-01, re-estimated at every
   origin with the same prior rules (s_j² recomputed on the training window):
   - h = 1: origins 2024-12 … 2026-08 (targets 2025-01 … 2026-09) and 2026-09 → 2026-10;
   - h = 3: origins 2024-12 … 2026-06 (targets 2025-03 … 2026-09) and 2026-07 → 2026-10.
   - After the origin: calendar exact; policy masked by `known_by`
     (`multibrand.data.policy`); HICP held at the last observed value; fuel
     forecast by the model.
   - Point forecast = median of 4,000 simulated predictive paths (parameter and
     shock uncertainty); 95 % interval from the same draws. Group counts from
     `market · exp(alr_g) / (1 + Σ exp(alr))`.
   - Metrics: RMSE and MAE for Tesla and the BEV market; comparison on identical
     target months with Task 04 M0 and M2 (`results/task04/stage1/predictions.csv`,
     2025 and 2026 Jan–Sep) and seasonal-naive (same month one year earlier).
     October 2026 is reported separately (no Task 04 comparator).
4. **Sensitivities (only these):** λ = 0.1 and λ = 0.5; fuel by the calendar-day
   definition on 2022-05 – 2026-09; model without the two HICP price terms.

## 4. Decision rules

| Hypothesis | Rule | Supported / weakened / open |
|---|---|---|
| H-F market: higher fuel prices go with more BEV registrations | Cumulative 12-month response of `log_market` to the fuel shock | 95 % band entirely > 0 / entirely < 0 / otherwise |
| H-F Tesla share | Same for `alr_Tesla` | same |
| H-P2026: the 2026 grant is associated with a higher BEV market | `grant_2026` in the `log_market` equation | interval > 0 / < 0 / includes 0 |
| H-Tax: the 2025-07 tax package is associated with higher premium-brand shares | `tax_package_2025_07` in `alr_BMW_Group` **and** `alr_Mercedes` | both > 0 / any < 0 / otherwise |
| Forecast gain for Tesla | BVARX RMSE below Task 04 M2 in 2025 and 2026 at h = 1 and h = 3 | all four / none / mixed (= open) |
| Forecast gain for market | same for the BEV market | same |

A sensitivity that flips a verdict is reported next to it; it never replaces the
primary result. No causal language: policy and fuel coincide with the 2022 energy
shock, model launches and Tesla's 2025 share loss.

## 5. Disclosure

Not outcome-blind: before this protocol the author had seen the Task 04 results,
brand shares by year, and one year-on-year correlation of log Euro-super 95 with
the log BEV share of passenger cars (computed in chat, not stored). The data layer
(`multibrand/data.py`) was built and its design matrix checked for completeness
and conditioning (condition number of the standardized exogenous matrix ≈ 16)
before this protocol; no model was fitted.
