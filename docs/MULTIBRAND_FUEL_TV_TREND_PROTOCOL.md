# Amendment `multibrand-bvarx/1.2.1-fuel-tv-trend` — corrected time-varying fuel coefficient

Frozen **before** any fit of these variants; committed alone. Everything not
stated here is as in [1.2.0](MULTIBRAND_FUEL_TV_PROTOCOL.md).

## Why a correction

1.2.0 added `b1 · τ_t · log_fuel_{t-1}` **without** the main effect `τ_t`. Because
`log_fuel` stays far from zero (about 0.3–0.9), the interaction is close to
`const · τ_t`, so `b1` can pick up any linear time trend in an equation, not only a
rising fuel elasticity. This was noticed **after** seeing the 1.2.0 results: the
market slope was +0.33 [+0.01; +0.66] while the marginal likelihood fell by 8.7
log units and the 2026 market forecasts deteriorated — the signature of a
trend term. The 1.2.0 results stay published unchanged, marked as affected.

## Variants

| Variant | Regressors added to the base model (every equation) | Prior on the added terms |
|---|---|---|
| `trend_only` (reference) | `τ_t` | flat-ish exogenous prior as in 1.0.0 (`(10 / sd(τ))²`) |
| `tv_linear_trend` (primary) | `τ_t` and `τ_t · log_fuel_{t-1}` | `τ_t`: as `trend_only`; interaction: as 1.2.0 primary |
| `tv_linear_trend_loose` | as primary | interaction prior variance × 25 |

`τ_t` is the 1.2.0 definition. The step variant of 1.2.0 is **not** re-run: its
main effect (`1` from 2024-01) is already spanned by the intercept and the grant
indicators (they differ only in December 2023, 17/31 vs. 0).

## Reported quantities and decision rules

As in 1.2.0, for `tv_linear_trend`: `b1` 95 % interval > 0 → H-TV supported,
< 0 → weakened, else open (market and Tesla share). Also reported: the trend
coefficients, the implied `b(t)` path, log marginal likelihoods of all three
variants and of the constant base, and forecast RMSE against the constant base
and Task 04 M2. `trend_only` answers whether a deterministic trend alone changes
the base results; it carries no hypothesis.

## Disclosure

Written after seeing the 1.0.0, 1.1.0 and 1.2.0 results. The correction is a
specification fix motivated by a diagnosed flaw, not by the direction of a result;
it is nonetheless not outcome-blind.
