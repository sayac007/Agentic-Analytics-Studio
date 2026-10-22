# Task 01 readiness — after Task 00.5 proposal

**Stage A has a concrete synthetic-development specification for human review;
Task 01 has not started and is not automatically authorized.** v0.2.0 resolves the
baseline-regressor and missing initial Stability-contract blockers. See
[Statistical contracts](STATISTICAL_CONTRACTS.md) for the normative design.

## Resolved in the proposal

- Generator/evaluator-only reference and truth; estimator header is exactly period,
  synthetic_media, semi_synthetic_outcome. Extra reference/coefficient fields rejected.
- Fixed calendar controls and evidence/predeclaration requirements for breaks.
- Coefficient uncertainty, holdout contribution/units, pointwise curves on common
  training spend support, same-data comparisons and declared sensitivity diagnostics.
- Oracle Stage A versus future train-only search/misspecification and replicated
  scientific scenario evaluation. No unjustified MDE threshold/flag.
- Strict version 0.2.0, shared offline schemas, artifact/hash/identity validation,
  retained traversal/numeric/provenance/split checks and new isolation tests.
- Explicit synthetic 72-month reference/DGP proposal, 60/12 split; six-row shape
  fixtures cannot pass the benchmark gate. Admission floors are not power guarantees.

## Before starting Task 01

1. Human review/merge of the design PR, then explicit Task 01 authorization.
2. Adopt/freeze the documented synthetic-development protocol (seed, source version,
   transformations, fractions, controls and predeclared diagnostic/stability choices),
   or admit an equivalent real reference. Pin implementation dependencies and archive
   manifests before inspecting fit/recovery. No fitting or generator exists yet.
3. Implement runtime separation: the estimator entry point receives only its manifest
   and CSV, without private data mounts, parent-directory discovery or truth-dependent
   preprocessing. The present tests prove file-interface separation, not OS isolation.
4. Follow the updated `workorders/01-walking-skeleton.md`: same-data include/omit-
   quarter-end comparison, Stage A only, declared condition diagnostic and no
   detection-limit flag. This is a planning update, not Task 01 execution. A future
   MCP tool/report remains Task 01 work, not delivered or authorized by this PR.

## Real-data blocker and bounded scientific questions

Only **January 2025** is verified for KBA Tesla in the committed evidence; retained
workbook period, license and SHA-256 were checked again. No adequate multi-year
observed series has been admitted. Real Tesla recovery remains blocked on >=48
training + >=12 holdout contiguous verified months, provenance/licensing/vintage and
extraction reconciliation. Additional brands/BEV totals need the same checks; none
is claimed available as a ready benchmark. The proposed fully synthetic development
path avoids claiming observed Tesla performance while these requirements are unmet.

Stage B still needs search bounds, inner rolling split/budget/selection rule and
post-selection uncertainty. Stage C needs predeclared recovery tolerance, calibrated
false-positive/coverage and power targets, replication precision and failure
accounting. No MDE numbers or real-marketing causal claims are justified by this PR.
These questions do not block implementing a separately approved **synthetic Stage A**;
they do block calling the full research benchmark or detection-limit analysis specified.

## Verification boundaries

Local and actual remote CI results are reported in the PR for its exact commit.
CI runs the estimator fixture validator, generator fixture validator and full unittest
suite with Python 3.12/jsonschema 4.26.0. No model recovery, confidence coverage,
external source download or reference-project tests are claimed by this CI.

No MMM engine, UI, MCP server or changes to WKR/HypoForge/Kinderwelt were made.
