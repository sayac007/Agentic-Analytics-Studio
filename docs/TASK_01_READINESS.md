# Task 01 readiness assessment — Task 00 hardening

**The current contracts validate as a Task 00 proposal. They do not yet authorize or
fully specify the revised Task 01 benchmark.** Keep PR #1 Draft until CI is green
and the maintainer has explicitly approved merging. A green contract workflow proves
schema/validator behavior, not statistical adequacy or approval to start Task 01.

## Concrete blockers before Task 01

1. **Remove the observed baseline from estimation inputs.** The current manifest
   still lists `observed_registrations` as a predictor and includes it in estimator
   CSVs. That is the earlier conditional/oracle-baseline proposal, now rejected by
   review. Separate generator-only baseline/truth artifacts from the estimator payload;
   agree on trend, annual seasonality, quarter-end and evidenced structural-break
   controls without leaking observed baseline values or truth. Update the manifest,
   CSV contract, examples, tests and decisions together in the statistical contract
   revision. The current fixture must not become the estimator implementation spec.
2. **Specify the initial stability output.** Existing result/comparison contracts
   contain point coefficients, MAE/RMSE and coefficient/RMSE deltas, but no uncertainty,
   media contribution or response curves. Agree on the uncertainty method, interval
   interpretation, contribution period/units and identical curve grid/support before
   implementing those outputs. A coefficient delta alone is inadequate when
   transformations differ. `effect_below_detection_limit` needs a calibrated simulation
   protocol; a single nonsignificant estimate cannot establish MDE.
3. **Keep the statistical stages distinct.** Task 01 is pipeline + OLS with explicitly
   oracle transformations. Train-only transform search/misspecification follows;
   the effect × noise × confounding grid with replication, interval coverage and
   detection rates is the scientific core. MDE is conditional on the tested grid,
   baseline and error/detection criteria. Multiple baseline series and later Bayesian/
   simulated-geo-test calibration need their own reviewed protocols. Do not prebuild
   their schemas or run them as part of this technical hardening.
4. **Select admissible baseline data and a sufficient window.** Only one KBA monthly
   release has been reconciled so far. Verify multi-month coverage, vintage, rights,
   missing-data handling and sample adequacy, or explicitly approve a synthetic-only
   pipeline fixture. The six-row hand-authored fixture validates file contracts; it
   is neither a generated recovery dataset nor sufficient for the proposed richer
   baseline model. Structural-break dates/proxy inputs need primary evidence and
   availability rules. Compare additional baselines only after source/grain checks;
   do not select a “quiet” series based on desired recovery results.

## Runtime and validation boundaries

Python remains the selected runtime; R parity is not a requested gate. The prior
R discussion is audit history, not an extra Task 01 requirement.

This change hardens the four existing schemas and validator without adding generator,
experiment or recovery schemas. The paused, unfinished statistical edits were archived
outside the checkout before restoring the reviewed PR contracts. Nothing was copied
from or changed in WKR, HypoForge or Kinderwelt.

All 16 existing regex fields are exercised directly against valid/invalid values:
4 months, 5 relative paths, 6 SHA-256 hashes and 1 Git SHA. Schema syntax checks alone
would not have caught permissive end anchors, Unicode digits or dot/empty path
segments. Paths now use canonical relative POSIX-style components; `.`/`..`, empty
components, absolute/Windows/encoded paths and trailing control characters are rejected.
Resolved input/output paths must remain inside the project root, including symlink
parents. This is validation-time containment, not a guarantee against concurrent
symlink replacement in a future writer; that writer still needs safe file handling.

The CSV parser validates the same bytes whose hash it checks. It rejects blank
records/fields, malformed quoting, wrong column counts/headers, invalid decimal or
nonfinite numbers, duplicate/out-of-order/missing months, fractional reference counts,
noncontiguous/reversed/out-of-range splits and inconsistent provenance. Decimal
reference validation avoids rounding a large fractional count into an integer.
Normal quoted fields, CRLF and scientific decimal notation remain supported.

Output/truth/comparison schemas validate structure only. Their cross-file hashes,
run identity, comparator support and numerical arithmetic, estimation isolation,
response-curve consistency and failed-fit behavior remain runtime acceptance checks
for the later implementation; the current validator does not claim to execute them.

## Verification and CI

- `python3 contracts/validate.py`: valid manifest and CSV, 6 fixture rows.
- `python3 -m unittest discover -s tests -v`: local results are recorded in the PR.
- `.github/workflows/contracts.yml`: Python 3.12, `jsonschema==4.26.0`, the two exact
  commands above, triggered by both `push` and `pull_request`, read-only repository
  permissions. The previous workflows directory contained documentation only.
- Remote CI status must be checked for the pushed commit; workflow existence or a
  local passing suite is not a successful GitHub Actions run. The PR stays Draft
  regardless of test results until maintainer approval.
