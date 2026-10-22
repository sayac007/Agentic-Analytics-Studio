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
