# Codex Workorder – Task 01F: First Real Attention Observation

Repository: `sayac007/Agentic-Analytics-Studio`

## Goal
Obtain and validate **at least one genuinely observed, legally usable, dated historical Tesla-attention series for Germany**, preferably Google Trends, without inventing missing observations. This task is data acquisition and quality assessment only; no correlations, regressions, causal claims, or MMM modifications.

## 0. Preconditions and scope
1. Verify PR #7 is merged into `main` (merge commit `dda2cef6badec65e9e87f2ef795edf0180ffa745`). Pull the current `main` and create `data/task-01f-first-real-attention`.
2. Read `AGENTS.md`, `docs/ORGANIC_ATTENTION_FEASIBILITY.md`, `data/organic_attention/{README.md,sources.json,access_log.json}`, and relevant KBA provenance documents.
3. Do not modify KBA observations, statistical contracts, Stage-A MMM results, estimator isolation, or upstream repositories.
4. Create a Draft PR; do not merge.

## 1. Primary route: Google Trends Germany
1. Attempt a **legitimate, documented export** of Tesla search interest for Germany, ideally monthly 2018-01 through 2025-12. Use the official Google Trends UI/export or an explicitly authorized official API. Do not bypass 429, rate limits, CAPTCHA, authentication or platform restrictions.
2. If the environment cannot export data, **stop the empirical acquisition and document a precise manual handoff**: exact UI settings (search term vs topic, geography DE, category, search property, time window, export format), filename convention, and a local import command accepting a user-supplied CSV. Do not claim a dataset exists.
3. Preserve the original downloaded CSV unchanged outside generated outputs, recording file SHA-256, retrieval timestamp/time zone, source URL, export method, exact query/topic, geography, frequency, and any resampling or normalization. Document applicable use/redistribution conditions; if unclear, retain raw export privately and provide a reproducible importer rather than committing raw values.
4. Check whether the selected period produces monthly or weekly data; do not assume monthly. If weekly, document the date semantics and aggregation rule before converting. Never fabricate observations, zeros, or exact absolute search volumes.
5. Note that the 0–100 index is relative to the chosen request/window and may vary across repeated exports. Never splice separately normalized exports as though they shared a common scale. If feasible, use two independent authorized exports to measure reproducibility and report any discrepancies; never average them silently.
6. If the query is ambiguous (Tesla as a person, company, brand or topic), document and test alternative query definitions as **separate series**, without choosing based on KBA correlations.

## 2. Fallback: YouTube publication inventory
Only if Trends is blocked, test a small, pre-registered set of public Tesla-related channels and their video publication timestamps via an authorized YouTube Data API or other compliant access. Freeze channel IDs and selection criteria before collection. Distinguish owned, independent creator and editorial channels; distinguish German-language content from German audience reach. Current cumulative views must not become historical monthly views. Deleted/private videos and incomplete pagination imply unknown coverage. Do not collect or redistribute personal comment content.

## 3. Minimal implementation
1. Build a small importer/validator for **real user-provided Trends CSVs**, with explicit `observed` provenance, or a compliant YouTube publication-date inventory if actually retrieved. Keep synthetic fixtures in separate test paths.
2. Keep unknown months missing. Validate month uniqueness, date ordering, finite index values, 0–100 bounds when applicable, coverage, geography and query metadata. Fail on conflicting frequency, scale or provenance.
3. Produce `data/organic_attention/real_data_coverage.json` and, **only if genuine observations were obtained**, a clearly labeled monthly observed CSV with documented redistribution permission. Otherwise preserve the existing empty empirical indicators and report `not_empirically_populated`.
4. Implement offline tests for CSV parsing, normalization metadata, duplicate months, malformed rows, missingness, inconsistent scales, and source-vs-synthetic separation. CI must not require internet or credentials.

## 4. Scientific guardrails
- Search interest is a proxy for attention, not impressions, spend, brand favorability, or causal media impact.
- Reconstructed historical search indices are not necessarily historical point-in-time available vintages. Respect existing as-of restrictions.
- Do not use Tesla registrations or any model outcome to choose query terms, time windows, channels, scaling, or filtering.
- No correlation with KBA, no lag optimization, no significance tests, no regression, no ROI estimates in this task.
- Do not fabricate success to meet the deliverable; a blocked acquisition with a working manual-import pathway is acceptable.

## 5. Deliverables
- `docs/FIRST_REAL_ATTENTION_OBSERVATION.md`: access attempts, exact export configuration, provenance, license/rights status, actual observed coverage, limitations and reproduction steps.
- Minimal import/validation code and focused offline tests.
- Machine-readable coverage report; observed data artifact only if truly acquired and legally shareable.
- Updated README with a concise, accurate status (observed or still blocked).
- Draft PR describing changed files, actual test commands/results, CI status, and next recommended scientific step.

## Acceptance criteria
A reader can verify whether at least one real monthly historical attention observation exists, where it came from, what it measures, and whether its dates and normalization are trustworthy. If access fails, the repository remains honest and offers a small, tested manual import workflow. No invented data or causal inference. No automatic merge.


## Execution and acceptance record — 2026-10-23

- [x] Verified PR #7 merged at the required `dda2cef6badec65e9e87f2ef795edf0180ffa745`; branch `data/task-01f-first-real-attention` starts from current main.
- [x] Official Explore request returned HTTP 429 at 17:21:29 Europe/Berlin; empirical acquisition stopped without retry/bypass. Documentation requests returned 200.
- [x] YouTube fallback preflight: no named API key or verified owner authorization/channel IDs; general ADC presence does not prove YouTube access and was not used. No inventory or comments collected.
- [x] Exact manual-export handoff, incomplete sidecar template, bounded private offline monthly-CSV importer and synthetic-only fixtures delivered.
- [x] Raw/metadata/output hash binding; native month/frequency/query/geo/scale validation; zero/missing/censoring separation; no splicing or weekly conversion. Known fixture bytes cannot enter the observed CLI path.
- [x] No real data acquired: `not_empirically_populated`, 96/96 and 60/60 unknown; no observed CSV committed. Existing empirical artifacts unchanged.
- [x] Local full suite 164 passed (17 new); offline artifact checks, example validators, KBA audit, Ruff and whitespace checks passed. Reproduction/limitations documented.
- [x] No KBA observations, Statistical Contracts, MMM engine/results, estimator isolation, outcome analysis or external repositories changed.
- [ ] Current-commit GitHub Actions: actual status and run links maintained in the Draft PR after completion.
- [ ] Empirical prerequisite remains: lawful user export, actual-source/rights review and import/coverage verification. This is acknowledged incomplete empirical acquisition, not fabricated success.

Create Draft PR; no automatic merge.
