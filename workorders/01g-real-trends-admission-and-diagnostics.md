# Codex Workorder — Task 01G: Real Trends Admission and First Econometric Diagnostics

Repository: `sayac007/Agentic-Analytics-Studio`

## Goal
Admit one authentic Google Trends Germany Tesla monthly export for **private retrospective analysis**, then perform an explicitly exploratory, reproducible comparison with the verified KBA Tesla monthly registrations. Do not claim causal advertising effects, historical real-time forecast availability, or a valid marketing ROI.

## 0. Branch and prerequisites
1. Verify PR #9 is merged into `main` (merge commit `9013913bbca7f60efe7226ad797e15d16d9d90ae`). Read `AGENTS.md`, the Trends importer documentation, KBA provenance/admission rules, statistical contracts, and current tests.
2. Create `research/task-01g-trends-econometrics` from updated `main`; open a Draft PR. Never merge automatically.
3. Do not change WKR, HypoForge, Kinderwelt, KBA observations, existing MMM Stage-A benchmark, or estimator isolation.

## 1. Authentic source and provenance: hard gate
- The user-provided original file is `multiTimeline.csv`, 274 monthly rows 2004-01 through 2026-10, SHA-256 `28e0b00b697ceb65833ca5bb2039d43c0ab4350d9a732e884edd3a44fe0da84e`, official Explore URL `https://trends.google.com/trends/explore?date=all&geo=DE&q=Tesla`, search term Tesla, Germany, Web Search, all categories. Verify these independently against actual bytes and the existing evidence. The file may need to be supplied separately to Codex; never substitute fixture values.
- The original download was reported on 2026-10-23 Europe/Berlin; **the exact clock time is unknown**. Do not fabricate it, backdate a later upload time, or claim it is proven. If the current strict importer requires an exact timestamp, ask for a new manually downloaded and accurately timestamped original export, or produce a documented `pending` outcome. Do not weaken the gate to force an import.
- Request explicit user confirmation of lawful private analytical use based on reviewed Google Terms and the applicable export conditions. An exporter checkbox, hash, or URL is not independent legal verification. Redistributing the values requires a separate review. If unresolved, stop the empirical analysis and deliver only the executable, tested analysis plan/fixtures.
- Preserve the entire original file privately, byte-for-byte, with raw hash, retrieval evidence, query, source-wide normalization, and all admission decisions. No real index values, raw CSV or normalized subset committed to public Git.
- Use the version 1.1 extended importer to derive 2018-01–2025-12 (96 months) and 2021-01–2025-12 (60 months) by row selection only. No re-normalization, interpolation, weekly conversion or splicing. Treat 2026-10 as incomplete at the reported download date. The retrospective subset is not a historical as-of vintage; full-window Google scaling may use observations after 2025.

## 2. Freeze the empirical protocol before examining relationships
- Create `docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md` **before** inspecting cross-series results. Record fixed sample 2018-01–2025-12, separately 2021-01–2025-12; units, exclusions, transformations, missing-value policy, candidate lags 0–3 (lags 4–6 sensitivity only), and outcomes/attention hypotheses.
- Tesla KBA registrations are counts of new registrations, not sales, orders or deliveries. Google Trends is a sampled 0–100 request-relative search-interest index, not absolute searches, reach, spend, or media exposure. The term Tesla may include non-automotive interest.
- Specify a parsimonious baseline using trend and calendar seasonality, with clear handling of known disruptions. Do not add controls or choose lag lengths after looking at significance. Consider quarter-end delivery patterns and the end of EV subsidies as potential confounders; use only documented evidence and pre-specified controls.
- Reserve 2025 as a *retrospective pseudo-holdout* for descriptive out-of-sample comparison, not a genuine historical real-time forecast: the Google Trends vintage was downloaded in 2026. Prevent leakage from fitting scalers, transformation parameters, or model selection on the holdout. If this cannot be defended, omit predictive claims and label it an in-sample descriptive analysis.

## 3. Econometric diagnostics
Only if the admission gate passes:
- Validate the month-level one-to-one join and both series' units and completeness; reject duplicates or missing months instead of silently filling them.
- Plot levels, log1p(Tesla registrations) as an explicitly separate sensitivity view, and Trends; seasonal month/quarter profiles; ACF/PACF of levels and suitably transformed series. Show confidence bands with clear assumptions.
- Conduct ADF and KPSS where sample length and specifications permit; document lag selection, deterministic terms, null hypotheses and low power under structural breaks. A slow-decaying ACF alone does not prove a unit root. Seasonal unit-root or break-robust tests are optional only if justified and adequately supported.
- Examine pre-specified contemporaneous and lagged associations 0–3 months, plus 4–6 as sensitivity, **after** controlling for deterministic trend/seasonality in a defensible way. Show sample sizes, coefficients and uncertainty; use HAC or another justified serial-dependence treatment. Account for multiple comparisons and refrain from choosing the most significant lag as a discovery.
- Compare a simple baseline with and without pre-specified Trends lags, clearly distinguishing descriptive association from pseudo-holdout prediction. Do not infer a marketing causal effect or ROI.
- Treat 2022 as a descriptive event window; without separately verified oil-price and policy series, do not attribute the patterns to the Ukraine-war oil shock. 2026 KBA data are not yet in the admitted monthly baseline; do not pretend to analyze 2026 registrations or an Iran-war effect.
- If diagnostics suggest nonstationarity, common trends or structural breaks, flag spurious-regression risk; do not report naive level regressions as causal evidence. Document an appropriate future model (differenced/ARDL/VAR/local projections) rather than fitting many models opportunistically.

## 4. Deliverables and tests
- `docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md` and `docs/TESLA_ATTENTION_FIRST_RESULTS.md` (English). Results must distinguish completed real analyses from blocked or fixture-only tests.
- A small, deterministic Python analysis CLI that consumes **private admitted** Trends subset and verified KBA data, writes private plots/tables/report, and refuses pending/unverified inputs. Keep private data and empirical outputs outside public Git unless separately authorized.
- Unit tests with synthetic fixtures: month alignment, lag direction, train/holdout separation, no normalization leakage, refusal of unadmitted data, reproducible diagnostic calculations, missingness and proper report labeling. No network calls in CI.
- Run existing test suite, lints and CI. Report actual outcomes, exact PR-head checks, and any unresolved source/legal/technical blockers.
- Keep engineering proportional to the research question. No new generic provenance framework, MCP server, UI, R port, Monte Carlo engine or Bayesian analysis.

## 5. Stop condition and PR
If exact retrieval-time evidence or private-use rights cannot be confirmed, **do not bypass the gate**: deliver a clear pending-admission report, analysis protocol, synthetic-fixture tests, and exact instructions for a newly timestamped official export. No empirical statistics on unadmitted data.

Create a Draft PR, do not merge. The acceptance criterion is either (a) a reproducible, honestly labeled private retrospective exploratory analysis with an admitted real Trends export, or (b) an explicit blocker and a fully tested path to that analysis, with no fabricated results.


## Execution record — 2026-10-24

- [x] Required PR #9 merge confirmed; current main used.
- [x] Protocol frozen first in commit `24b3462`; no real cross-series result inspected.
- [x] Actual original private bytes found and required raw SHA-256 independently verified.
- [x] Exact original download time remains unknown; lawful private-use confirmation was requested and remains unconfirmed. No permission or timestamp fabricated.
- [x] Real-input CLI attempt refused at timestamp validation before join/analysis; no result directory.
- [x] Deterministic private CLI, separate human-admission template, synthetic fixture generator/tests and English pending-results report delivered.
- [x] Full local suite: 187 passed (12 new), 37.124 s. Targeted new suite: 12 passed. Pinned installation, pip check, existing offline artifact checks, lints and whitespace checks passed.
- [x] No real raw/subset/result values, user screenshot or private legal-review records published.
- [x] KBA observations, Statistical Contracts, Stage-A results/engine, estimator isolation and upstream repositories unchanged.
- [ ] Actual exact-timestamp export evidence and human private-use/source/terms review remain prerequisites.
- [ ] Exact-head CI outcomes and run URLs are maintained in the Draft PR after completion.

Initial duplicate-outside-window negative-test failure and fixture import-placement
lint warning were corrected. Fixture results are software evidence only. No automatic merge.
