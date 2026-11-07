# Amendment `multibrand-bvarx/1.2.0-fuel-tv` — time-varying (rising) fuel coefficient at lag 1

Frozen **before** any fit of these variants; committed alone. Protocols 1.0.0 and
1.1.0 and their results stay unchanged. Requested by the repository owner on
2026-11-07 ("Variante mit zeitlich abhängigem steigendem Koeffizienten für den
ersten Lag für Benzinpreis"). Everything not stated here is as in 1.0.0 (data,
endogenous vector, exogenous terms, λ = 0.2, draws, seed, forecast design) with
the outcome months of 1.1.0 (2021-02 – 2026-09, 68 months).

## 1. Variants

All variants keep the base model (L = 1) and add **one** regressor to every
equation, the interaction of the lagged fuel price with a deterministic time
function `g(t)`:

`… + b0 · log_fuel_{t-1} + b1 · g(t) · log_fuel_{t-1} + …`

so the fuel coefficient at lag 1 is `b(t) = b0 + b1 · g(t)`.

| Variant | `g(t)` | Prior on `b1` |
|---|---|---|
| `tv_linear` (primary) | `τ_t = (m_t − 34.5) / 12`, `m_t` = months since 2021-01 (2021-02 → 1 … 2026-09 → 68); years, centred so that `b0` is the mid-sample coefficient; same fixed formula at every forecast origin | mean 0, variance `λ² / s_fuel²` × `Σ_ii` per year (same scale as the lag coefficient) |
| `tv_linear_loose` | as primary | variance × 25 (prior SD × 5) |
| `tv_step_2024` | `1` from 2024-01 (first month without the Umweltbonus), else `0` | as primary |

The slope is **not** constrained to be positive: the sign is the test.

## 2. Reported quantities

1. `b1` (slope or step) and `b0` in every equation, 95 % intervals; for
   `log_market` and `alr_Tesla` also the implied coefficient `b(t)` at 2021-06,
   2022-06, 2023-06, 2024-06, 2025-06 and 2026-09 with 95 % intervals.
2. Log marginal likelihood of each variant and of the constant-coefficient base
   model on the same 68 months (descriptive).
3. Forecast RMSE for Tesla and the BEV market with the 1.0.0 windows, against the
   constant base model (1.1.0 `L1`) and Task 04 M2; future interaction terms use the
   simulated fuel path.

## 3. Decision rules

| Hypothesis | Rule (primary `tv_linear`) |
|---|---|
| H-TV market: the fuel coefficient in `log_market` rises over time | `b1` 95 % interval > 0 → supported; < 0 → weakened; else open |
| H-TV Tesla share: the same in `alr_Tesla` | same |

Sensitivities that flip a verdict are reported next to it and do not replace it.
No variant replaces the 1.0.0 primary model.

## 4. Disclosure

The author had seen all 1.0.0 and 1.1.0 results before writing this amendment
(including a lag-1 fuel coefficient in `log_market` of +0.95 [−0.11; +1.99]).
