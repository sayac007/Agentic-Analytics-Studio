# Side-branch assessment: which covariates can the main model carry?

Status 2026-11-07. Decision paper only: **no model was fitted** for this document
and no frozen protocol, result or hash-bound file was changed.

> **Follow-up the same day:** the repository owner decided to publish the fuel
> prices (with notice), to model the fuel price as an **endogenous** variable, and
> to add all incentive programmes as dummies and prices as exogenous variables.
> This was implemented as a separate joint model —
> [protocol](MULTIBRAND_BVAR_PROTOCOL.md), [results](../results/multibrand/README.md).
> The five incomplete calendar-day fuel months were resolved by using the complete
> "mean of bulletins dated in the month" definition, with the calendar-day
> definition as a pre-named sensitivity. The Task 04 state-space models were not changed.

## 1. The binding constraint is the sample, not the number of ideas

| Quantity | Value |
|---|---|
| Common monthly KBA brand/BEV months | 70 (2021-01 – 2026-10; Task 04 used 69) |
| Effective observations after a 12-month seasonal burn-in | ≈ 58 |
| Regressors already in the primary M2 market equation | 10 (4 calendar terms, 4 subsidy steps, 2 transition pulses) plus local level and slope |
| Regressors per brand-share equation | 4 calendar terms plus local level and slope |
| Policy/regime breaks inside the window | 2022 energy-price shock, 2023-01 subsidy cut, 2023-09 business exclusion, 2023-12 abrupt end, 2026 programme |

Rules of thumb for this sample (stated before any new fit):

1. At most **one** new substantive covariate per equation per stage, with a
   fixed lag set (0–2 months) named in advance; no lag search.
2. A covariate is admissible only if its series is **complete** for all model
   months (or the handling of gaps is fixed in the protocol before fitting) and
   comes from a primary source with a recorded rights decision. Unknown is never zero.
3. Covariates that move together with a policy break are flagged as
   **weakly identified** before fitting, so a null result is not over-read.
4. Each addition is judged on the same rolling-origin holdout against the
   unchanged M0/M1/M2 baselines; in-sample fit gains do not count.

## 2. Verdict per side branch

| Branch | Data actually available | Verdict for the main model | Reason |
|---|---|---|---|
| **Fuel prices** (`data/fuel_prices_de/`, new; values private) | Euro-super 95 and diesel, Germany, incl. taxes; complete calendar-day months 65/70 in 2021-01 – 2026-10 (missing 2021-01, 2021-04, 2021-12, 2022-01, 2022-04), none missing since May 2022 | **Candidate for Stage 2** as the single H-F covariate (Euro-super 95, log, nominal; fixed lags 0/1/2), **after two maintainer decisions**: (a) rights for using/publishing derived values, (b) how the five incomplete months are handled — either start the H-F comparison in 2022-05 (54 months, fewer than the 48+ training months plus holdout need) or pre-name an alternative monthly definition (mean of bulletins dated in the month) as the only fallback | Primary source, directly addresses the open hypothesis H-F. Weak identification warning: the 2022 price spike overlaps the end-2022 subsidy rush, and the 2026 price rise overlaps the 2026 programme. |
| Brent / EUR-USD / private diesel study (`fuel_oil/`, Task 01I.3) | Private uploads, rights partly unresolved | **Do not include; freeze** | Upstream of retail fuel prices, therefore redundant once the retail series is available; rights scope is private only. |
| Google Trends attention (`attention/`) | 0 admitted observations (`data/organic_attention/real_data_coverage.json`); private file blocked at timestamp gate | **Do not include; freeze** | No admitted data; Trends indices are re-scaled per download and strongly endogenous (search interest follows deliveries and news), so even complete data would be a mediator, not a driver. |
| Tesla campaigns (`campaigns/`) | 106/106 months unknown, 0 proven active or inactive months | **Do not include; archive** | No measured media series exists; an all-unknown column carries no information. |
| Product events / recalls (`product_events/`) | 7 months with verified dated records, 89 unknown | **Do not include as a series**; at most one pre-named event dummy as a documented sensitivity | Coverage is not exhaustive; a sparse lower-bound count would confound "no record" with "no event". |
| German macro controls (`macro_controls/`) | 0 acquired observations | **Not needed for brand shares; low priority for the market equation** | Macro conditions hit all brands alike and are absorbed by the market level/state; with ≈58 effective months a macro block would cost more degrees of freedom than it can explain. |
| Competitor list prices (`data/competition/`) | 23/80 annual top-10 model-years with any exact price; no monthly panel | **Not yet usable**; see the price-index design in `workorders/05-multibrand-model-proposal.md` | A relative-price regressor needs a monthly, registration-weighted panel. |
| BEV operating cost (electricity) | Not acquired | **Prerequisite for any cost-ratio regressor** | Fuel prices alone measure only the combustion side of the running-cost comparison. |

## 3. What this means in practice

- The main model stays small: calendar + policy (as frozen) + at most **one**
  fuel-price term in the next stage, once the two decisions above are made. Everything else is either missing data or would be an
  endogenous mediator.
- The most valuable new information is not another macro series but **more
  cross-sectional structure**: the KBA panel already contains every reported brand
  every month. A joint multi-brand model uses that structure without adding
  external series (see the proposal in `workorders/05-multibrand-model-proposal.md`).
- Frozen and archived branches keep their code, tests and evidence; they are
  simply not inputs to the Tesla study. Re-opening one requires new admitted data
  and its own work order.

## 4. Disclosure

While preparing this document, one descriptive statistic involving the outcome was
computed in chat (year-on-year correlation of log Euro-super 95 with the log BEV
share of passenger cars, 61 months). It is deliberately **not** reproduced here and
is not used for any choice above; the Stage 2 protocol therefore cannot claim to
be outcome-blind with respect to that statistic.
