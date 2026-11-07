# Amendment `multibrand-bvarx/1.1.0-fuel-lags` — fuel price at lags 1 to 4

Frozen **before** any fit of these variants; committed alone. The base protocol
[`multibrand-bvarx/1.0.0`](MULTIBRAND_BVAR_PROTOCOL.md) and its results stay
unchanged. Requested by the repository owner on 2026-11-07 ("Benzinpreis versetzt,
Lag 1, 2, 3, 4"). Everything not stated here is as in 1.0.0 (data, endogenous
vector, exogenous terms, prior form, λ = 0.2, draws, seed, forecast design).

## 1. Variants

For L ∈ {1, 2, 3, 4} every equation contains

`y_{t-1}` (all 7 endogenous variables) + `log_fuel_{t-2}, …, log_fuel_{t-L}` + the 14 exogenous terms.

L = 1 is the base model (its posterior must equal 1.0.0 primary; regression test).
Only extra lags of the fuel price are added, not of the other variables
(restricted VAR(L); 7 + (L − 1) + 14 regressors per equation).

- Fuel values before 2021-01 come from the same published series
  (`data/fuel_prices_de/monthly.csv`, bulletin mean, available from 2018-01), so
  all four variants use **the identical 68 outcome months** (2021-02 – 2026-09).
- Prior for `log_fuel_{t-l}`, l ≥ 2: mean 0, variance `λ² / (l² · s_fuel²)` times
  `Σ_ii` (Minnesota lag decay).
- Fuel shock: recursive, fuel first, on the companion form with the extra fuel lags.

## 2. Reported quantities (all variants, all reported)

1. Coefficients of every fuel lag 1 … L in every equation, and the **sum of the
   fuel-lag coefficients** in `log_market` and `alr_Tesla` (direct long-lag
   association), each with 95 % and Bonferroni 98.75 % (= 1 − 0.05/4) intervals.
2. Cumulative 12-month impulse responses (months 0–11) of all variables to a
   one-SD fuel shock, 95 % and 98.75 % intervals.
3. Log marginal likelihood of each variant (closed form for the conjugate prior;
   identical outcome sample) — descriptive comparison of lag depth.
4. Forecast RMSE for Tesla and the BEV market with the 1.0.0 windows (h = 1, 3;
   2025, 2026 Jan–Sep, October 2026), against Task 04 M2 and L = 1. Future fuel
   lags come from the simulated fuel path.

## 3. Decision rules

- **H-F (market, Tesla share) per variant:** as in 1.0.0 on the cumulative IRF,
  95 % interval → supported / weakened / open.
- **H-F across lags:** "supported across lags" only if the 98.75 % interval of the
  cumulative market response lies above zero in **at least one** variant **and**
  no variant has a 95 % interval entirely below zero; otherwise reported as
  "not robust to lag choice".
- No variant replaces the 1.0.0 primary model, whatever its likelihood or RMSE.

## 4. Disclosure

The author had seen all 1.0.0 results (including the fuel IRF, which peaks at
months 1–2 with an interval including zero) before writing this amendment.
