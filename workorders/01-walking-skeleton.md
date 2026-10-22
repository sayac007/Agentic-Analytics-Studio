# Codex Task 01 — Stage A walking skeleton (only after human approval)

## Objective

Implement the Stage A semi-synthetic recovery pipeline defined by the approved
[Task 00.5 statistical contracts](../docs/STATISTICAL_CONTRACTS.md), version 0.2.0.
This work order is a plan; its update does not start or authorize implementation.
Observed/reference baseline reconstruction must be imperfect: never use the reference
or its planted components as estimator regressors. No real Tesla media ROI claim.

## Required implementation

1. Freeze an admitted reference: a verified complete monthly KBA series with its
   vintage/release ledger, or the explicitly synthetic 72-month development protocol
   in STATISTICAL_CONTRACTS.md. The six-row contract fixture is not a benchmark.
   Enforce the benchmark admission gate and retain reference bytes/hash unchanged.
2. Implement deterministic generation with independently spawned media/noise RNG
   streams, predeclared oracle adstock/Hill and training-only effect/noise scaling.
   Write separate estimator CSV and evaluator-only truth. Record exact implementation
   and dependency versions. Do not expose reference, beta or truth paths to fitting.
3. Provide an estimator entry point taking only the safe manifest/CSV, with linear
   trend, annual Fourier order 1 and predeclared quarter-end/break controls. Use the
   audited/pinned HypoForge transforms and specified OLS/HAC uncertainty protocol.
   Carry causal history into holdout. No parameter search in Stage A; no test leakage.
4. Produce include/omit-quarter-end runs on the **same** dataset, transforms, holdout
   and serialized spend grid. Persist valid result files with coefficients/intervals,
   holdout contribution/units, pointwise response curves and diagnostics. Recompute
   the comparison's signed differences and predeclared sensitivity flags. Rank-deficient
   or invalid fits exit nonzero without a successful result artifact.
5. Evaluate each result against private truth only after fitting. Report planted-beta,
   contribution and curve errors, interval coverage and detection outcomes as one-run
   outcomes, never empirical power. Keep detection-limit status uncalibrated/null;
   `effect_below_detection_limit` is forbidden. A declared numerical-condition warning
   may satisfy the initial diagnostic requirement without inventing an MDE.
6. Expose one read-only MCP tool serving a saved, validated comparison and a
   deterministic Markdown report. Never allow arbitrary execution via tool arguments.
7. Supply a short clean-checkout regeneration sequence and meaningful tests for RNG
   determinism, transform behavior, calendar controls, causal holdout history, output
   contracts, exact reference preservation and no false real-ROI labeling. Include a
   runtime test that estimator execution succeeds without private reference/truth
   files or generator configuration mounted or discoverable.

## Acceptance criteria

- Human approval explicitly recorded before execution; this design PR is not approval.
- Synthetic versus observed data, benchmark effects and real-world claims stay distinct.
- Benchmark gate passes; no shape-only fixture is reported as a recovery experiment.
- Two runs, per-run evaluation, one comparison, one MCP tool and one report conform
  to v0.2.0 and the predeclared protocol. Metadata/hash validation is not a substitute
  for independent numerical regression and uncertainty checks in the implementation.
- Tests and actual remote CI status are documented separately; failures remain visible.
- No UI, PPTX, enterprise connectors, unrestricted execution, VAR/SVAR or upstream
  WKR/HypoForge/Kinderwelt changes.

## Later stages, outside Task 01

Stage B needs train-only rolling search/misspecification and selection uncertainty;
Stage C needs a frozen replicated effect/noise/confounding/baseline protocol,
recovery tolerances, calibrated error/power targets and Monte Carlo precision.
Bayesian priors and simulated geo-test calibration are later research. Do not treat
those still-open choices as implemented, and do not infer detection limits from one
successful fit or one planted coefficient.


## Task 01a execution scope

The user authorized the synthetic-only subset after PR #2 was merged: generator,
private truth, isolated oracle OLS/HAC, two model variants, contribution/response
outputs, comparison/evaluation, deterministic report, tests and CI smoke. **No MCP
server is in Task 01a**, overriding item 6 for this subtask; no such server is claimed.
No real ingestion, search, scenario grid or other research stage is implemented.
See `docs/RUN_SYNTHETIC_MMM.md` and the implementation PR for actual execution and
remaining scientific limits. This planning record does not authorize self-merging.
