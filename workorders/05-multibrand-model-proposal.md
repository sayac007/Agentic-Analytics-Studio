# Work order 05 (proposal) — joint multi-brand model and brand price index

Status: **design B executed on 2026-11-07** at the owner's request, as protocol
[`multibrand-bvarx/1.0.0`](../docs/MULTIBRAND_BVAR_PROTOCOL.md)
([results](../results/multibrand/README.md)), with these differences to the
proposal below: fuel price endogenous, incentive programmes and HICP prices
exogenous (owner's specification); no Chinese group, because several Chinese
brands are only inside KBA `SONSTIGE` (they stay in Rest); no SMART question.
Design A (state-space extension) and the price index (section 5) remain proposals.
Prerequisite reading: `docs/SIDE_BRANCH_ASSESSMENT.md`, `docs/REGIME_STATE_SPACE_PROTOCOL.md`.

## 1. Question

Task 04 models the BEV market plus two brand ratios (Tesla/Rest, VW/Rest).
It cannot say **where Tesla's lost share went**, whether brand groups react to each
other's quarter-end waves, or whether a brand-specific shock is really a market
shock. A joint model of the largest brand groups answers these questions using
data that is already complete (every reported brand, every month), without new
external covariates.

## 2. Candidate brand groups (from the 2026-11 KBA vintage, BEV 2021-01 – 2026-10)

Largest single brands by cumulative BEV registrations: VW 15.4 %, Tesla 9.3 %,
BMW 7.8 %, Mercedes 6.6 %, Škoda 6.4 %, Audi 6.1 %, Hyundai 5.2 %, Opel 4.2 %,
Seat 4.0 %, Renault 3.9 % (top 6 = 51.7 %, top 12 = 75.5 %). All have 70/70
non-missing months.

Brands of one group share platforms, pricing and delivery logistics, so single
brands are not independent units. Proposed grouping (to be fixed in the protocol):

| Group | KBA brands | Rationale |
|---|---|---|
| Tesla | TESLA | Study target |
| VW Group | VW, AUDI, SKODA, SEAT (KBA reports CUPRA models under SEAT), PORSCHE | Shared MEB/PPE platforms, joint pricing |
| BMW Group | BMW, MINI | |
| Mercedes | MERCEDES | |
| Hyundai-Kia | HYUNDAI, KIA | Shared E-GMP platform |
| Chinese-owned brands | BYD, MG ROEWE, POLESTAR, XPENG, NIO, LEAPMOTOR, ZEEKR, LYNK & CO, … (exact list frozen with ownership evidence) | Hypothesis H-C; brands hidden in `SONSTIGE` remain unclassified and are reported, not imputed. SMART (Mercedes-Geely joint venture) is ambiguous: assign once in the protocol and run the other assignment as the single sensitivity |
| Rest | official BEV total minus all groups above | Accounting remainder, never labelled "China" |

## 3. Why not a classical (unrestricted) VAR

With K groups in additive log-ratio form (K−1 ratios against Rest) plus the log
market, a VAR(p) has per equation K·p lag coefficients plus intercept, 4 calendar
terms and, for the market, 6 policy terms.

| Specification | Variables | Coefficients per equation | Total coefficients incl. covariance | Observations per equation |
|---|---|---|---|---|
| VAR(1), 7 groups | 7 | 7 + 5 (+6 market) = 12–18 | ≈ 118 | 69 |
| VAR(2), 7 groups | 7 | 14 + 5 (+6) = 19–25 | ≈ 167 | 68 |
| VAR(3), 7 groups | 7 | 21 + 5 (+6) = 26–32 | ≈ 216 | 67 |

Unrestricted OLS would be technically estimable for VAR(1) but has two to four
observations per coefficient, will over-fit the extreme Tesla quarter-end swings
(e.g. 367 in July 2026 versus 12,552 in September 2026) and gives unstable impulse
responses. Contemporaneous registrations of competitors are themselves outcomes,
so Cholesky-ordered impulse responses would rest on an arbitrary ordering.
**An unrestricted VAR is therefore not recommended.**

## 4. Recommended designs (in this order)

**A. Primary — extend the frozen Task 04 state-space system to K groups.**
Market equation unchanged (calendar + policy, optional single fuel term from
Stage 2); one log-ratio equation per group against Rest with local level/slope,
annual seasonality, **group-specific quarter-end term** and a correlated innovation
covariance (LKJ prior as in Task 04). Re-uses `regimes/kalman.py` and the
verification tooling; the K = 3 case must reproduce Task 04 exactly as a
regression test. Cross-group effects appear through the innovation correlation,
which is descriptive ("who loses when Tesla gains"), not causal.

**B. Secondary — Bayesian VAR(1) on the same log-ratios** with a Minnesota prior
(own-lag mean 0.9 to respect persistence, cross-lag shrinkage fixed in advance,
no hyperparameter tuning on holdout errors), exogenous calendar, group-specific
quarter-end and policy dummies. Used for forecast comparison and generalised
(ordering-free) forecast-error variance decompositions only. Lag order fixed at 1;
p = 2 as a single pre-named sensitivity.

**Evaluation (both):** identical rolling-origin windows as Task 04 (≥ 48 training
months, h = 1 and h = 3, target years 2025 and 2026 incl. October), against
seasonal-naive and the frozen M0/M2. Metrics per group and for Tesla in
registrations, plus the aggregate share error. A group model is "useful" only if
it beats M2 for Tesla in both years at both horizons; otherwise the result is
reported as open.

## 5. Brand price index ("price per 100 km of range") — data design

No public source publishes average transaction prices by brand. The proposal
builds a **registration-weighted list-price index** instead:

1. **Weights:** KBA FZ10 model-series registrations (BEV column), previous
   calendar year as fixed weights (Laspeyres) so current sales do not enter their
   own price regressor. Monthly model rows with a BEV column already exist in
   sheet `FZ 10.1` of the workbooks pinned in
   `data/competition_vintage_2026_11/kba_sources.json` (e.g. October 2026:
   TESLA MODEL Y 2,534, MODEL 3 397); the current parser keeps model rows only
   from December files, so a monthly model extract is a small parser extension.
2. **Prices:** dated gross list price of the cheapest BEV variant per model series
   and its WLTP range, from primary or archived sources:
   - manufacturer price lists (PDF) and configurator snapshots in the Internet
     Archive (exact capture timestamp as vintage);
   - BAFA list of eligible vehicles under the former environmental bonus
     (2020-2023; expected to state the net list price of the base model —
     **not yet verified**, check columns and archived versions first);
   - documented manufacturer price-change announcements (e.g. Tesla price cuts),
     only as dated observations, never as interpolated paths.
   Rights must be checked per source; aggregated index values can be published,
   raw snapshots stay outside Git, as for the existing offer observations.
3. **Coverage target:** models covering ≥ 80 % of each group's BEV registrations
   per year. A price is carried forward only as an explicitly flagged
   "last observed" value for at most 6 months; beyond that the cell is missing.
4. **Outputs per group and month:** index of list price, index of list price
   per 100 km WLTP range (`price / (range_km / 100)`), coverage share, number of
   price points, maximum price age.
5. **Net-of-subsidy variant:** subtract the published standard subsidy amount of
   the regime in force (`data/task04_regimes/policy_chronology.json`); income-
   dependent 2026 amounts are flagged as approximations.
6. **Operating-cost companion:** cost per 100 km = Euro-super 95 price
   (privately generated, see `data/fuel_prices_de/README.md`) × fixed reference consumption versus
   household electricity price × fixed reference consumption. The electricity
   series still has to be acquired (candidate: Eurostat household electricity
   prices for Germany, semi-annual; rights and frequency to be verified);
   public-charging tariffs have no official series and must not be invented.

The existing 130 offer observations in `data/competition/price_observations.json`
are the seed; realistic effort is roughly 40 model series × quarterly snapshots.

## 6. Acceptance criteria

- [ ] Protocol `docs/MULTIBRAND_PROTOCOL.md` committed alone, with group
      definitions, priors, lags, windows and decision rules, **before** any fit on
      real data; hash bound by the runner.
- [ ] K = 3 (Tesla, VW, Rest) reproduces Task 04 M2 coefficients within Monte
      Carlo tolerance (regression test).
- [ ] All group series built from `data/competition_vintage_2026_11/` with an
      exact accounting check: groups + Rest = official BEV total every month.
- [ ] Price-index coverage table published before the index enters any model;
      the index enters a model only if coverage ≥ 80 % in every model year.
- [ ] Every result row labelled supported / weakened / open, including null and
      negative findings; no causal language for cross-group correlations.
