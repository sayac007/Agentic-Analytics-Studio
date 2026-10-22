# Task 01 readiness after Task 01a

The user authorized the synthetic Stage-A implementation after merging PR #2.
Task 01a now implements generation, isolated OLS/HAC, comparison, evaluation and a
deterministic Markdown report under the unchanged v0.2.0 contracts. See
[execution instructions](RUN_SYNTHETIC_MMM.md). The explicit subtask excludes the
MCP server in the broader walking-skeleton work order; it is not claimed delivered.

The synthetic reference has 72 months, fixed seed/streams, predeclared settings and
separate immutable reference/truth artifacts. Two same-data models differ only by
quarter-end control. The estimator receives only its manifest/CSV in a fresh process
and workspace. Failure paths, stream history, uncertainty arithmetic and full artifact
integrity are tested. Runtime dependencies and HypoForge commit provenance are pinned.

The first checked results show poor recovery, including negative estimated media
coefficients despite a positive injected effect. Results are retained without tuning;
confidence coverage and power have not been established. A missing engineering flag
does not establish causal/statistical identification.

Remaining work is scientific or expressly outside Task 01a:

- No complete observed KBA series has been admitted: verified source evidence still
  covers January 2025 only. Real-data experiments need the full length, provenance,
  vintage/rights and extraction checks required by the statistical contract.
- Stage B needs predeclared search bounds/inner validation and selection uncertainty.
- Stage C needs a reviewed replication/scenario protocol, recovery tolerance,
  calibrated error/power targets and Monte Carlo precision. No detection limit is
  calibrated; the corresponding field remains null/not_calibrated.
- Bayesian/geo-test, UI and MCP are not implemented. No WKR/HypoForge/Kinderwelt source
  changes were needed.

Exact local counts, sample hashes and actual remote CI evidence are reported in the
implementation PR. Green CI proves tested execution/integrity, not model effectiveness,
empirical power or real Tesla ROI. The PR stays Draft and is not automatically merged.
