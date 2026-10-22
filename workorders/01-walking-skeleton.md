# Codex Task 01 — Working MMM vertical slice (one PR after Task 00)

## Objective
Deliver a reproducible end-to-end **semi-synthetic benchmark**, not a generic MMM framework. Reconcile details with the approved Task 00 contracts.

## Required implementation
1. Read a documented observed monthly registrations series (or a clearly labeled small fixture if licensing/access prevents download); retain the observed series untouched.
2. Generate synthetic media with deterministic seed and explicit true adstock/Hill parameters. Inject its known effect into a **separate semi-synthetic outcome**, with realistic noise and documented effect magnitude. Preserve true parameters in a private-for-estimation truth artifact for recovery evaluation.
3. Fit an ordinary least squares baseline with predeclared transforms and a time-aware holdout. Limit hyperparameter search; prevent leakage from future data. If HypoForge API is validated, use it; otherwise implement a temporary parity-tested adapter.
4. Produce two model runs with different documented settings or data windows. Save manifests, coefficients, fit/holdout diagnostics and comparable response curves. Provide one stability flag, e.g. `weak_identification` or `effect_below_detection_limit`, with an explicit, defensible rule. Do not claim a universal MDE from a single fitted coefficient.
5. Expose **one read-only MCP tool** to retrieve a validated run comparison. Never permit arbitrary code execution via tool arguments.
6. Generate a deterministic Markdown report from saved results, clearly separating observed market data, synthetic interventions and recovered effects.
7. Provide one command or short sequence to regenerate the whole demo from clean checkout, with tests for deterministic generation, transform behavior, schema validation, temporal leakage, output contract and no false causal labeling.

## Acceptance criteria
- Fresh-run instructions work in a documented environment, or exact blocker is recorded.
- All claimed tests actually executed; CI state distinguished from local state.
- Two saved runs, one comparison, one MCP tool, one report, and meaningful tests.
- Synthetic injection and true effects never described as real Tesla media impact.
- No UI, PPTX, enterprise connector or VAR/SVAR implementation in this task.

## Follow-on research (not part of this PR)
Run power/MDE experiments with multiple seeds and effect sizes (e.g., 3% and 15% only as illustrative scenarios), experiment-based calibration, and a separate VAR/SVAR model family.
