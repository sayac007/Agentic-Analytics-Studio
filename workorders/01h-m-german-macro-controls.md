# Codex Addendum — Task 01H-M: German Financing, Purchasing Power and Inflation Data

Repository: `sayac007/Agentic-Analytics-Studio`

## Purpose
Extend the Tesla Product, Availability & Recall evidence work with a **separate, independently reviewable macroeconomic data workstream**. The objective is to prepare trustworthy German monthly explanatory series for financing costs, household purchasing power, inflation and inflation expectations. This is data engineering and documentation only: **do not fit models or select variables using Tesla registrations or Google Trends outcomes**.

## Branch and boundaries
1. Read `AGENTS.md`, the current Task 01H workorder, KBA provenance/admission rules, frozen Task 01G statistical protocol, and current repository status.
2. If Task 01H is already underway, do not modify its branch or PR. Start a separate branch from the latest `main`, e.g. `data/task-01h-macro-controls`, and open a Draft PR. If an integration dependency is missing, document it; do not silently rebase onto unmerged work.
3. Preserve existing KBA, Trends, MMM, contracts and frozen analyses. Do not change coefficients, sample windows, holdouts or model specifications. No automatic merge.

## Candidate series and authoritative sources
Investigate and identify **exact series IDs**, frequencies, units, definitions, vintages and legal reuse conditions before downloading:

- **Consumer borrowing rates:** Bundesbank/ECB MFI interest rates for new business in loans to households for consumption, preferably effective annual rates and clearly defined fixation/aggregation. This is the primary financing-cost candidate, not a direct Tesla loan/lease APR.
- **Policy rate:** ECB deposit facility rate; distinguish event-based rate changes from any monthly end-of-period or monthly-average aggregation.
- **Market rate:** 3-month EURIBOR (or another justified reference), clearly distinguished from actual consumer credit rates.
- **Inflation:** Destatis German CPI, all-items index and YoY inflation; optionally HICP for comparability, but never silently substitute it for CPI.
- **Real earnings/purchasing power:** Destatis real/nominal earnings index or other official German income indicator **at its native frequency**. Explicitly test whether the requested monthly 2018–2025 series exists; if only quarterly, keep quarterly and label `not_monthly_available` for the monthly candidate. Do not fabricate monthly observations by interpolation.
- **Inflation expectations:** Bundesbank household expectations surveys and ECB Consumer Expectations Survey where Germany-specific, historic, consistently defined monthly results can actually be verified. Document coverage, survey horizon (12 months vs longer), statistic (median/mean), survey population and breaks. Do not conflate euro-area with Germany-specific results.
- **Optional household confidence/purchase intentions:** add only if access, geography, definitions and rights are verified. Do not imply a paid data source is open.

Prefer official Bundesbank, ECB and Destatis APIs/downloads. Document exact dataset/series IDs and canonical links rather than generic homepages. Cross-check overlapping interest-rate measures where appropriate; do not average conceptually different series. Never claim that two different definitions are independent corroboration of the same statistic.

## Provenance and extraction
For each series provide: `series_id`, `provider`, `definition`, `country`, `frequency`, `unit`, `seasonal_adjustment`, `observation_period`, `value`, `release_or_vintage`, `retrieved_at`, `source_url`, `raw_sha256`, `transformation`, `rights`, and missingness/quality status. Keep raw downloads unchanged and hash them. Document data revisions and publication lags; never infer historical as-of availability from today's downloads.

Implement a small reproducible extractor/normalizer with offline fixtures. Retain original native-frequency observations and create a monthly table **only** for genuinely monthly variables. If transforming daily policy/market rates to monthly, predeclare the rule (e.g. monthly average vs month-end), implement deterministic calendar logic and label derived values. No forward filling or synthetic monthly earnings values. If some APIs are blocked, produce a source-specific blocked report and tested adapter without invented observations.

## Economic design, without fitting
Prepare a pre-specified modeling note separating:
- Levels versus changes (rates in percentage points, inflation in percent YoY, real income growth) and possible nonstationarity;
- Financing rate versus policy rate and EURIBOR, including collinearity;
- Possible delays from financing conditions to orders and from orders to registrations;
- Inflation versus real earnings and the risk of mechanically overlapping deflators;
- Macroeconomic common shocks and simultaneity; coefficients would initially describe associations, not causal effects;
- Data availability at decision time versus retrospective descriptive use.

Propose parsimonious candidate sets and lag horizons **before** seeing cross-series correlations. With only 96 Tesla months, avoid an unrestricted regression with many highly correlated macro controls. The existing frozen Task 01G analysis must remain unchanged; any expanded model requires a separately approved protocol/version.

## Tests and deliverables
Add offline tests for frequency, units, period alignment, duplicate/revised observations, series ID stability, rate aggregation, missingness, CPI YoY computation (if derived), no monthly fabrication from quarterly data, hashes, and fail-closed provenance. Do not require live API calls in CI.

Deliver:
1. `docs/GERMAN_MACRO_CONTROLS.md` with a source/definition/coverage matrix and economic interpretation.
2. Machine-readable source catalog and data-quality/coverage report for 2018–2025, with 2021–2025 separately summarized.
3. Reproducible download/extraction code and small offline fixtures.
4. A candidate variable/lag protocol **without estimated coefficients or post-hoc selection**.
5. Draft PR with actual tests, CI evidence, legal/reuse caveats and unresolved blockers.

**Acceptance criterion:** We know which German monthly macroeconomic controls are genuinely available and comparable, and which are not. No invented data, empirical estimates, or retrospective point-in-time claims.

## Execution record — 2026-10-24

- [x] Independent branch from latest main including merged Task 01H PR #13.
- [x] Source-specific request evidence, honest blocked catalog and 96/60-month coverage report.
- [x] Native-frequency core adapter, immutable download/provenance path and synthetic offline fixtures.
- [x] Pre-specified sparse candidate sets/lags; no outcome relationships or fitted coefficients.
- [x] No KBA/Trends/product ledger/MMM/contracts/frozen protocol changes.
- [ ] Real metadata, series-specific rights, exact selected keys and measured coverage (proxy CONNECT 403).
- [ ] Actual-format Destatis/Bundesbank parsers after official sample export review.
- [x] Full local suite: 233 passed (40.014 s); 23 macro tests passed; validators/audit/smoke/lint passed.
- [ ] Exact-head remote CI evidence: maintained in Draft PR after observed completion.

Monthly earnings availability remains not_verified: indexed official metadata lists
a monthly table, so a blanket quarterly-only claim would be unsupported.
No new dependencies, empirical estimates, publication of real values or automatic merge.
