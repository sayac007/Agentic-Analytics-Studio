# Codex Workorder — Task 01I: Real Fuel, Oil & FX Acquisition

Repository: `sayac007/Agentic-Analytics-Studio`  
Language: English for all repository content and deliverables.

## Objective
Acquire, verify, and prepare real historical energy-price observations for Germany, with reproducible refresh paths where genuinely supported. Target 2018-01 through the latest completed month in 2026, keeping 2018–2025 as a separate frozen comparison window. This is a **data acquisition and QA task**, not an econometric modeling task.

## 0. Preconditions and branch
1. Inspect current `main`, `AGENTS.md`, existing source/provenance contracts, Task 01G and 01H-M documents, and open PRs. Do not build on unmerged changes.
2. Create `data/task-01i-fuel-oil-fx` from current `main`; open a Draft PR; do not merge.
3. Use Claude's handoff files if available: `fetch_fuel_oil.py`, `GERMAN_FUEL_OIL_SOURCE_REVIEW.md`, `FUEL_OIL_API_ACCESS_LOG.md`, and `DATA_SOURCES_FUEL_OIL.md`. Treat URLs and licence interpretations as **candidates**, not verified results. If files are not present, state that and work from primary sources.
4. Do not change existing KBA, Google Trends, MMM, or frozen statistical protocols.

## 1. Data priorities

**A. German diesel pump price:** European Commission Weekly Oil Bulletin, Germany, automotive gas oil, with taxes, original weekly values (typically EUR/1,000 litres). Confirm units, exact column, dates, and revisions from the actual file. Verify official history file linked from https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en. The historical XLSX may be refreshed/replaced, so retain retrieval metadata and raw hash.

**B. Brent:** US EIA Europe Brent spot price `RBRTE` in USD/barrel, using the official EIA API v2 petroleum spot dataset. Verify API route, exact facet, native frequency, key requirements, paging and complete observations. Do not silently truncate at 5,000 rows.

**C. EUR/USD:** ECB EXR `D.USD.EUR.SP00.A` and/or `M.USD.EUR.SP00.A`, **USD per EUR**. Official API: `https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?startPeriod=2018-01&format=csvdata`. Check exact returned metadata and monthly definition.

**D. German E10:** Research ADAC, MTS-K, Tankerkönig and other rights-cleared providers, but do not claim a verified nationwide E10 history without evidence. **Never relabel EC Euro-super 95 as E10.** If E10 remains blocked, document it and keep it out of the admitted dataset.

## 2. Actual access before implementation
For each source make one minimal lawful test request. Log exact URL (secrets redacted), timestamp, HTTP status or exception, content type, response bytes, and whether the response contains a real numeric observation. A successful documentation fetch or HTTP 200 HTML page is not a successful data retrieval.

If network access fails, do not create empty pseudo-observations. Supply a tested **offline fixture** plus precise manual export instructions and stop empirical admission. Do not retry 429 aggressively or bypass access controls.

## 3. Secure, minimal fetcher
Review and improve Claude's candidate `fetch_fuel_oil.py` rather than creating a new general ingestion framework.
- No secrets in code, logs, exceptions, manifest URLs, Git, or CI artifacts; redact API keys in all error paths.
- Validate HTTP content type, parseability, expected series key, units and observation count; reject error payloads and mismatched data.
- EIA pagination or explicit completeness checks; record total count and page coverage.
- Timeout, bounded retry for transient errors, no retries on unauthorized/rate-limited responses without explicit backoff policy.
- Save immutable raw bytes plus SHA-256, exact UTC retrieval time, endpoint, parameters, source revision/vintage if available, licence-review status.
- Offline deterministic tests, no live API dependencies in CI.

## 4. Frequency and measurement contracts
- Keep native weekly/daily/monthly observations separately.
- For EU weekly pump prices, document the measurement date. If deriving monthly values, specify a defensible calendar-day overlap convention and label it a **derived approximation**, not an official monthly mean. Do not claim a Monday observation was measured on every following day.
- Require adequate temporal coverage; never silently interpolate missing days/weeks/months.
- For Brent use official monthly observations where verified; alternatively derive from daily trading observations with a declared calendar rule.
- For Brent EUR/barrel, align Brent USD/barrel and ECB USD/EUR on matched dates before division; a ratio of monthly averages is not generally the mean of daily ratios. If insufficient matched days, mark missing.
- Preserve tax inclusion, grade, currency, original units and transformations in metadata. Explicitly mark partial 2026 months.
- Separate current retrospectively downloaded vintage from historical point-in-time availability.

## 5. Licensing and attribution
Read the **actual primary** licence and dataset notices for EC, EIA, ECB and any E10 provider. Distinguish private analysis, raw redistribution and transformed-value redistribution. Do not assume a third-party licence applies to a government-hosted dataset. If public redistribution is not verified, keep raw/derived values private and commit only non-sensitive metadata and fixtures. Prepare copy-ready English attributions with source URLs and change notices where required.

## 6. QA and tests
Test wrong grade (E5 vs E10), wrong country, tax variant, unit conversion, FX quote direction, duplicate/revised observations, missing weeks/days, calendar month edges, partial months, wrong API payloads, secret redaction, EIA pagination, source hash, rights gate and deterministic regeneration. Retain existing test suite and CI. Report exact counts actually run.

## 7. Deliverables
- `docs/GERMAN_FUEL_OIL_ACQUISITION.md`: evidence, sources, definitions, coverage, licence decisions and blockers.
- `data/fuel_oil/sources.json`, `coverage.json`, and redacted access log.
- A small verified fetcher/parser with offline synthetic fixtures and tests.
- Where permitted, real raw source files and derived monthly data with SHA-256 manifest; otherwise a **private handoff** with no real values committed.
- A short English attribution section in data-source documentation.
- Draft PR with actual access results, CI status, and a table for diesel, Brent, EUR/USD and E10 showing observed months, missing months, admitted/not admitted and why.

## 8. Acceptance
A successful empirical result requires at least one **actually retrieved and verified numeric source observation**, not merely an endpoint proposal. If all providers are blocked, deliver a clearly labelled blocked acquisition with tested local/manual handoff, without claiming empirical completion. Do not estimate oil-shock effects, run Tesla regressions, change Task 01G, or automatically merge.

## Execution record — 2026-10-24

- [x] Current main including merged PR #14; independent Task 01I branch.
- [x] All five handoff files read; code and licence claims independently reviewed.
- [x] Ten primary access attempts; all proxy CONNECT 403; EIA key absent.
- [x] Candidate fetcher replaced with credential-safe requests, validation, paging, immutable snapshots and synthetic tests.
- [x] Separate native-frequency/derivation contracts, E10 exclusion, blocked coverage and manual/private handoff.
- [x] No existing KBA/Trends/Macro/MMM/contracts/frozen protocol or other repositories changed.
- [ ] Empirical acquisition: blocked, no verified numeric primary observation.
- [ ] Source-specific WOB native layout, metadata and primary legal notices require actual access.
- [x] Local full suite 257 passed (40.237 s); 24 new targeted tests passed; validators/audits/report/lint checks passed.
- [ ] Exact-head remote CI maintained in Draft PR after observed completion.

No numeric real values published and no automatic merge.
