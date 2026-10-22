# Codex Task 00 — Audit and contracts (one PR)

## Objective
Establish a verifiable foundation before coding the MMM engine. **Do not implement the MMM, UI or PPTX in this task.**

## Tasks
1. Inspect this repository and available WKR, HypoForge R/Python and Kinderwelt references. Report precise repository paths, versions, exported Hill/adstock APIs, licenses and test evidence. If a repository is inaccessible, say so and request a snapshot; do not guess.
2. Research **primary-source** Tesla Germany registration data (KBA), public campaign dates, promotions/price changes and Google Trends feasibility. Record source URL, time span, granularity, reuse rights, uncertainty and whether a dataset can be committed. Do not scrape gated content or invent a TV campaign.
3. Propose a minimal manifest and CSV/JSON contract for observed target, synthetic media, injected semi-synthetic target, transform parameters, model results and run comparisons. Specify train/test time split and missing-data policy.
4. Audit whether HypoForge Hill can be reused directly; if not, document a temporary adapter and parity tests for the next task.
5. Recommend whether R CLI or Python should host the initial reference regression, with reasons based on available tools and tested HypoForge APIs.

## Deliverables
- `docs/AUDIT.md`: verified facts vs unknowns.
- `docs/SOURCE_CATALOG.md`: source research, license/reuse decisions.
- `contracts/manifest.schema.json`: minimal JSON Schema with valid example.
- `docs/DECISIONS.md`: decisions and rejected alternatives.
- PR summary with actual verification commands and open questions.

## Acceptance criteria
No invented data or CI claims. Schemas parse; examples validate with a locally available validator or validation is explicitly pending. No unrelated feature implementation. Human approval required before Task 01.


## Task 00 evidence checklist (2026-10-22)

- [x] Architecture and reference inspection documented in `docs/AUDIT.md`.
- [x] Exact WKR/HypoForge revisions, API signatures, licenses and local test evidence recorded.
- [x] Kinderwelt exact revision, QA runner/evidence patterns and 16 local packaging checks audited.
- [x] Primary-source catalog records verified KBA data/license, Tesla financing offers, Trends semantics and access limits.
- [x] Verified source contents, dates, coverage and per-source rights distinguished from remaining unknowns.
- [x] Manifest + valid synthetic fixture, truth/result/comparison schemas and rejection checks.
- [x] Python-first recommendation, HypoForge reuse boundary and parity plan documented.
- [x] No MMM/UI/PPTX implementation; no external source data committed.
- [ ] Human approval before Task 01; this remains an audit/contract proposal.

Validation: 13 local contract tests passed; example manifest/CSV validated.
Reference suites: HypoForge Python 22 passed; WKR 5 passed; Kinderwelt packaging subset 16 passed; R not run (runtime absent).
CI: awaiting maintainer verification. Remaining limits: full KBA series, historical price/campaign evidence, Trends export, R parity and final human approval.
