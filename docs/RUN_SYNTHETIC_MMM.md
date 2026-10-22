# Task 01a — reproducible synthetic Stage A

Task 01a implements the approved v0.2.0 **synthetic-only** protocol. It does not add
real Tesla ingestion, search, scenario sweeps, Bayesian/geo-test calibration, UI or
MCP. The user explicitly excluded MCP from this subtask despite the broader Task 01
work order. Existing v0.2.0 schemas and validators remain unchanged.

## Install and run

From a clean checkout, with Python 3.12, Git and HTTPS package/GitHub access:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m studio run --output artifacts/task01a-run1
.venv/bin/python -m studio verify artifacts/task01a-run1
```

Use a **new output directory** for each run. Existing directories/results are refused,
not deleted, patched or overwritten. An interrupted run can leave partial diagnostic
artifacts but has no validated inventory/completion claim; diagnose it and choose a
new directory. `inventory.json` is written only after fitting, comparison and report
creation; `verify` checks all hashes, membership, contracts and prediction arithmetic.

For exact repetition in the same pinned runtime:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m studio run --output artifacts/task01a-run2
cmp artifacts/task01a-run1/inventory.json artifacts/task01a-run2/inventory.json
```

The tests verify byte-identical complete inventories in this runtime. Different
Python patch versions or CPU/BLAS platforms can change last-bit numerical results
and result hashes; do not claim cross-platform byte identity without checking it.
Data, model, result and source hashes allow differences to be diagnosed rather than
silently accepted. Pinning alone does not establish scientific correctness.

## Frozen protocol and implementation

`config/task-01a.json` is copied before any generation/fitting. It freezes the approved
72 months (2018-01..2023-12), 60/12 split, seed 42, independent media, effect .08,
noise .05, alpha .5/L=3/normalize=False, Hill k=100/n=1.5, HAC three lags and 21 grid
points. No parameter search or recovery-driven changes occur. The zero-confounding
case reduces the documented media equation to `100*exp(.3*z)`.

The numerical condition limit is 1e8. The relative response sensitivity limit .25
and scale floor 1 count-equivalent are explicitly frozen **engineering choices**,
not empirical detection/recovery thresholds. These defaults were selected from the
reviewed contract example before seeing the fit. They are not changed to improve
results. Structural-break/outlier components remain omitted from both models.

NumPy `SeedSequence(42).spawn(2)` assigns stream 0 to media and stream 1 to noise.
The reference CSV and generator provenance/hash are written and made read-only before
media injection. Scaling uses only the first 60 reference/response values; the second
PCG64 stream supplies noise. The named protocol access/specification date is the fixed
2026-10-22 recipe version, not a new external source download date on every rerun.

The complete runtime lock pins new direct/transitive dependencies. HypoForge is
installed from Git commit `c47f636d24a39a820574a13133d6af693134a180` (Apache-2.0),
not copied or replaced locally. `runtime.versions()` verifies installed versions and
PEP 610 commit provenance before generation/fitting. Missing/different dependencies
fail rather than selecting a fallback. No upstream files were modified.

`environment.json` records Python and installed locked versions. `implementation.json`
records hashes of executable project sources, contracts, lock and protocol. This
avoids a circular requirement to embed the commit hash of the example artifacts in
their own source commit. Use the PR commit plus these source hashes for provenance.

## Bundle layout

| Artifact | Role |
|---|---|
| `protocol.json`, `environment.json`, `implementation.json` | Frozen recipe, runtime and source identity |
| `private/reference.csv`, `private/generator.json` | Synthetic immutable reference, lineage and generation settings |
| `private/truth.json` | Planted coefficient, noise, noiseless contributions and true curve |
| `safe/data.csv` | Exactly period, synthetic_media, semi_synthetic_outcome |
| `safe/*.manifest.json` | Calendar-only estimator config; no private paths/coefficients |
| `safe/*.result.json` | v0.2.0 OLS/HAC, contributions, curves and diagnostics |
| `safe/*.result.predictions.csv` | Holdout-only period, target, prediction and residual |
| `safe/*.access.json` | Allowed estimator data-phase file reads |
| `evaluation/*.json`, `comparison.json`, `report.md` | Truth recovery, same-data sensitivity and deterministic explanation |
| `inventory.json` | SHA-256 of every other bundle artifact, including prediction/access sidecars |

Individual predictions are an **additive sidecar**, because v0.2.0 has no prediction
field. No existing schema was silently extended. Sidecars are hash-bound in the
inventory and their periods, targets, residuals, MAE/RMSE are verified against the
safe data/result. Units are count-equivalent, not monetary return. Private files in
the committed example are deliberately synthetic and shareable; they are still
excluded from estimator execution.

## Execution separation and failures

Each fit runs in a fresh temporary directory and a separate `python -I -B` process.
The launcher copies only estimator modules (not generator/evaluator/pipeline), public
schemas/validator, dependency lock, one manifest and safe data. No `private` directory
is copied; no repository PYTHONPATH, credentials or generator variables are inherited.
Only minimal PATH/locale variables and explicit BLAS/OpenMP limits are passed.

After trusted dependency/schema bootstrap, a CPython audit hook denies Python file
opens outside that workspace and runtime/library prefixes. The access record covers
the estimator data phase and lists only its safe manifest and CSV. Tests execute the
fit with private files absent and separately demonstrate that opening the original
external reference raises PermissionError. This is process/directory separation plus
a Python guard, **not** a kernel sandbox against adversarial native extensions.

`studio.estimate.main` is the safe-manifest entry point; use the orchestrator's staging
rather than running it on a complete private bundle. It performs the benchmark gate,
versions/checksums, strict schema/CSV validation and training-rank checks, computes
all statistics, validates the result in memory, then publishes new files atomically
without clobbering existing paths. Rank deficiency, nonfinite inputs/outputs, missing
months/dependencies or bad hashes produce no new successful result. Holdout y never
enters coefficient or HAC estimation; only causal training history reaches holdout.

## Numerical evidence and tests

```sh
.venv/bin/python contracts/validate.py
.venv/bin/python contracts/validate.py contracts/examples/generator.json --kind generator
# Task 01B adds offline parser tests; install their pinned dependencies for the full suite.
.venv/bin/python -m pip install -r requirements-kba.lock
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m unittest discover -s tests -v
```

The original 49 contract tests are retained. New tests cover deterministic generation
and complete bundle repetition; stream separation and training-only scaling; actual
HypoForge API values and full-history carryover; independent OLS and exact HAC examples;
contribution/curve/prediction arithmetic; real process isolation; rank failure,
missing dependencies, invalid data and inventory tampering. No assertion requires
recovery to be good. No Monte Carlo/scenario grid is run.

Hand-checkable HAC reference: x=(-2,-1,0,1,2), y=(1,0,2,4,3), intercept included.
OLS=(2,.8), residuals=(3,-6,0,6,-3)/5. For three Bartlett lags, score meat is
`diag(18/25,36/25)`, X'X=`diag(5,10)`; with correction 5/3, covariance is
`diag(6/125,3/125)`. Another test verifies lag-zero covariance, and an independent
QR nuisance projection verifies the actual dataset's media coefficient.

GitHub Actions installs the same lock, runs both fixture validators and all tests,
then generates/verifies one deterministic smoke bundle. Remote status is reported
for the actual PR head, separately from these local results.

## Observed example and scientific limits

The full generated example is under `examples/task-01a/`; see its `report.md` and
`inventory.json`. The first checked run recovered **negative** media coefficients
although the planted coefficient is positive. This is retained, not tuned away.
Wide conditional intervals containing truth on this one realization do not establish
95% coverage; low numerical condition numbers do not prove statistical identification.

Known transforms leave baseline misspecification: the planted level shift/outlier are
unmodelled, there are only 60 training observations and spend varies over a limited
range. The experiment says nothing about real Tesla ROI, empirical power, calibrated
MDE or the effectiveness of actual advertising. Detection-limit status stays
`not_calibrated` and `effect_below_detection_limit` stays `null`. Real reference
admission and the scientific choices for B/C remain outside this implementation.


## Executed local verification

Executed in a second fresh Python 3.12.14 virtual environment installed solely from
`requirements.lock`: both original fixture validators passed; the complete suite
ran **73 tests, all passed**. The actual example generation and `studio verify`
commands passed. `git diff --check` passed. The original 49 contract tests remain
unchanged; 24 numerical/runtime tests were added. No upstream test suites were
rerun, no real source download occurred and no scientific target was tuned.

The SHA-256 of the checked-in example inventory is recorded below. The inventory
binds report, predictions, access logs, runtime/source identity and all v0.2.0 files.
Remote CI is reported separately in the PR only after actual completion.

`inventory.json`: `60841c09165fe806bbaad99395f7709b62144b15ed799d423b995ce44176de28`
