# Codex Workorder 01I.1 — Real Energy Data Integration

Repository: `sayac007/Agentic-Analytics-Studio`. All repository contents and PR communication in English.

## Goal and starting conditions

Start from the current `main` only after checking whether PR #15 is merged. If not merged, stop and report the blocker; do not build on a draft branch. Read `AGENTS.md`, `docs/GERMAN_FUEL_OIL_ACQUISITION.md`, `docs/DATA_SOURCES_FUEL_OIL.md`, `data/fuel_oil/sources.json`, and the current fuel/oil code and tests. Create `data/task-01i1-real-energy-integration`. Open a draft PR; do not merge.

The user has supplied **three actual original files**, which must be explicitly transferred to the Codex workspace; they are not automatically available merely because they were uploaded in another ChatGPT conversation:

1. `ECB Data Portal_20261024135113.csv` — candidate ECB monthly EUR/USD.
2. `RBRTEm.xls` — candidate EIA monthly Brent workbook.
3. `Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx` — European Commission fuel-price history workbook.

If any original is missing, report exactly which and do not claim that its observations were acquired. Never substitute fixtures for empirical files. Keep raw inputs and derived outputs private pending dataset-specific reuse review. No raw/derived real observations in public PR or CI artifacts.

## Step 1 — Source inventory and validation (must precede extraction)

- Record raw filename, byte count, SHA-256, local retrieval evidence if actually known, actual workbook sheet names, dimensions, source-identifying headers, and provenance gaps. Do not invent exact download times.
- For ECB: validate exact `EXR.M.USD.EUR.SP00.A`, frequency M, quote USD per EUR, observation status, units, missing/revised flags, 2018–2025 completeness, and 2026 coverage. Do not infer series identity from filename alone.
- For EIA: inspect the actual `.xls` container and native worksheet layout; confirm it is the Europe Brent spot price monthly series, USD/barrel, distinguish month labels from footnotes and annual summaries, and report gaps. Avoid silently renaming or treating `.xls` as `.xlsx`. Use the smallest justified parsing dependency and pin it if needed.
- For European Commission: inspect the actual historical XLSX workbook, find Germany + **automotive gas oil/diesel** in **prices with taxes**. Verify date column, units, sheet/column labels, footnotes, changes in structure, country mapping, and time coverage. Never substitute Euro-super 95 for E10. If layout is ambiguous, stop diesel admission and request human confirmation with a minimal non-sensitive screenshot or exact cell coordinates.
- Verify applicable official licensing and required attribution using the specific dataset's notice where possible. Distinguish permission for private analysis, raw redistribution, and derived redistribution. Unverified rights remain blocked, not assumed granted.

## Step 2 — Small source-specific adapters

- Reuse `fuel_oil` architecture where appropriate; do not create another general ingestion framework.
- Implement source-specific parsers for the **actual** CSV/XLS/XLSX layouts. Add focused fixture tests reflecting the verified structural shapes, with synthetic values; no actual data in fixtures.
- Retain immutable raw bytes and hashes. Generate separate private normalized observations with original date, source series key, units, observation-status fields and vintage information where available.
- Monthly EIA Brent: prefer verified source-native monthly values rather than deriving from daily data without reason.
- ECB monthly EUR/USD: retain source-native monthly reference series, no inverted quotation.
- EC weekly diesel: retain native weekly observations; derive a monthly approximation only with an explicit and reviewed calendar-day overlap convention, complete coverage checks, and a clear label that it is **not an official monthly mean**. A Monday observation does not prove constant actual prices through the week.
- Keep partial October 2026 distinct from completed September 2026; no filling, extrapolation, or silent re-scaling.
- Do not treat the 2018–2025 analysis window as a historical as-of vintage.

## Step 3 — Coverage and QA

For each of diesel, Brent and EUR/USD report verified observed, missing, censored/revised, partial and blocked months for 2018-01..2025-12 (96 months) and 2018-01..2026-09 (105 months). These counts must be computed from the parsed real files, not presumed. E10 remains excluded unless independently verified evidence is supplied.

Produce a private source-to-derived hash inventory and a public metadata-only summary. Test malformed formats, wrong currency/units, wrong fuel grade/tax status, duplicate periods, missing weeks, partial months, provenance failures, and non-public output isolation. Verify deterministic reprocessing of the same raw files. Do not expose personal local paths or credentials.

## Step 4 — Deliverables and stop conditions

Deliver: source adapters, offline synthetic tests, a metadata-only `docs/REAL_ENERGY_DATA_IMPORT.md`, reviewed source/rights catalog updates, machine-readable coverage and QA summary, and a **private** output directory containing actual derived series if admitted. Explain how the user can access that private directory or export it securely; never pretend a Codex workspace path is downloadable in ChatGPT.

Do not modify KBA observations, the frozen Task 01G protocol, MMM/Stage A results, or other repositories. No regressions, correlations, ROI, or causal estimates in this PR.

Run the existing full test suite and relevant lint/CI. Report actual commands, outcomes, exact head SHA and links. Draft PR only; no automatic merge. A successful importer test does not mean a real source has been admitted. If rights or layout checks fail, keep that series blocked and report precisely why.

## Execution record — 2026-10-24

- [x] PR #15 confirmed merged; current main used.
- [x] Three original uploads transferred, metadata inspected, hashes recorded before extraction.
- [x] Actual-format adapters, synthetic fixtures, private quarantine and metadata-only coverage.
- [x] ECB/EIA 96/105 complete native months; diesel 83/92 temporally covered months with 13 unfilled gaps.
- [x] Embedded EC reproduction notice reviewed; new primary requests recorded as proxy blocked.
- [x] Real replay of eight artifacts byte-identical; own ingestion time separate from unknown download time.
- [ ] Analytical admission: blocked by ECB/EIA rights and EC currency/derived-use review.
- [x] Local full suite 273 passed (40.751 s); 16 targeted tests passed; validators/audit/metadata/lint passed.
- [ ] Exact-head remote CI recorded in Draft PR after observed completion.

No raw/derived real values published, no ready admitted dataset, no model or automatic merge.
