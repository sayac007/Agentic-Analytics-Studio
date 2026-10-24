# Codex Workorder — Task 01I.2: Source Rights & Analytical Admission

Repository: `sayac007/Agentic-Analytics-Studio`

## Objective
Resolve the rights and provenance gates for private retrospective use of the real ECB EUR/USD, EIA Brent, and EC Germany diesel series. Do **not** estimate models, change the frozen Task 01G protocol, or publish real observations. Separate private analysis from public raw/derived redistribution.

## 0. Start
1. Pull current `main`; confirm PRs #16 and #17 are merged. Read `AGENTS.md`, `docs/REAL_ENERGY_DATA_IMPORT.md`, `data/fuel_oil/real_sources.json`, `real_coverage.json`, and Task 01J start criteria.
2. Branch `governance/task-01i2-energy-rights-admission`.
3. Locate the three original private files and verify existing SHA-256 bindings. If unavailable, document that blocker; never pretend to rerun the import. Do not commit private data, personal paths or screenshots.

## 1. Verify authoritative reuse conditions
Review the actual source policy and file-specific notices. Record policy title, URL, review timestamp, evidence type, relevant exceptions, and source-specific conclusion. If the network is blocked, treat URLs as leads, not independently read evidence; request a human-supplied copy or screenshot rather than granting automatic permission.

**ECB EUR/USD** — https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html

The published ESCB policy permits reuse of public ESCB statistics with source credit under conditions including unchanged statistics/metadata and exceptions for third-party data. Verify coverage of the exact `EXR.M.USD.EUR.SP00.A` series. Distinguish original observations from project-derived statistics.

**EIA Brent** — https://www.eia.gov/about/copyrights_reuse.php

The EIA policy generally allows use/distribution of US government data with acknowledgment, while warning about third-party protected materials. Verify that the actual `RBRTE` series has no applicable exception. Record the requested citation and source date.

**European Commission diesel** — https://european-union.europa.eu/legal-notice_en ; https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en ; https://eur-lex.europa.eu/eli/dec/1999/566/oj/eng/pdf

Check whether the Commission's general reuse terms and the workbook's embedded reproduction notice apply to the actual historical file and its **derived monthly approximations**. Verify required attribution and change notice. Keep EUR/1,000 L to EUR/L conversion distinct from the Monday-to-month calendar-overlap assumption. The unit convention was user-attested in PR #17, not independently read by Codex.

## 2. Explicit rights/admission matrix
Create `docs/ENERGY_RIGHTS_ADMISSION.md` and `data/fuel_oil/rights_admission.json` with separate decisions for each source:
- `private_analysis`: permitted / blocked / not_verified
- `public_raw_redistribution`: permitted / blocked / not_verified
- `public_derived_redistribution`: permitted / blocked / not_verified
- `source_definition_verified`, `unit_verified`, `raw_sha256_verified`
- `source_notice_url`, `reviewed_at`, `evidence_type`, `evidence_hash`, `limitations`
- `analytical_admission`: admitted / blocked, with reasons
- `historical_point_in_time`: not_established unless proven separately

No blanket approvals based on government domains or successful download. `not_verified` does not mean prohibited. If a separate human decision is required, stop and request it; do not set approval flags yourself.

## 3. Diesel missingness and independence
Verify actual coverage from the existing private QA: ECB and Brent 96/96 months (2018–2025), 105/105 (through 2026-09); diesel 83/96 and 92/105, with **13 unfilled months**. List exact missing months and counts by year. Determine whether gaps affect the 2022 episode without looking at outcomes. No interpolation, forward fill, or invented daily prices. Keep E10 excluded.

Admit sources **independently**: a diesel rights or missingness blocker must not prevent ECB/EIA admission if their own evidence and gates are sufficient. No 2026 Tesla/BEV outcome analysis without separately verified KBA 2026 data.

## 4. Execution, tests and CI
Where all source-specific evidence and existing gates are satisfied, create private hash-bound admission artifacts with existing tooling. Never weaken source identity, timing, rights or human review gates. Otherwise provide a concrete pending checklist and exact manual evidence needed.

Add focused offline tests for rights-state transitions, private/public distinction, independent admission, hash/series/unit binding, retention of all 13 diesel gaps, no leaks of real values/private paths, and backward compatibility. Run full tests, Ruff and CI; report only observed results.

## 5. Deliverables
Draft PR against `main`, no automatic merge:
1. Evidence-backed rights decision matrix and English attributions.
2. Explicit admitted/blocked status per series and unresolved evidence.
3. Diesel missing-month summary.
4. Tests and exact CI status.
5. A concise recommendation whether a **specified subset** can proceed to Task 01J, subject to its unchanged start criteria and separate human authorization.

**Do not run regressions, change frozen protocols, publish actual values, or claim a legal clearance beyond the verified evidence.** Scientific acceptance means documented real source decisions, not just additional green tests.

## Execution record — 2026-10-24

- [x] PRs #16/#17 merged; current main used; private raw/normalized hashes verified.
- [x] Five primary fetch attempts recorded as proxy blocked, not policy evidence.
- [x] Human-provided research handoff preserved byte-for-byte and labelled externally reviewed, not personally fetched/full legal copy.
- [x] Exact embedded EC reproduction notice separately reviewed and hash-bound.
- [x] Source-specific matrix, independent gates, conditional English credits and exact missingness (13 months; January/April 2022 affected).
- [x] Actual private check/writer: zero admissions, no admission directory created.
- [ ] Source-specific third-party/ownership/derived-scope review and explicit human private admission decisions pending.
- [x] Full local suite 292 passed (45.164 s); 18 targeted rights tests passed; validators/audit/metadata/lint passed.
- [ ] Exact-head remote CI maintained in Draft PR after observed completion.

No outcome relationships inspected, Task 01J executed, source flags self-approved,
real values published or automatic merge.
