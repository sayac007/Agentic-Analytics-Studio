# Statistical file contracts v0.2.0

Breaking replacement for v0.1.0: **observed registrations are no longer estimator
inputs/regressors**. See [Statistical decisions](../docs/STATISTICAL_CONTRACTS.md)
and [Task 01 readiness](../docs/TASK_01_READINESS.md). The Task 01a implementation now consumes these unchanged contracts; see
[execution instructions](../docs/RUN_SYNTHETIC_MMM.md).

| Schema | Boundary |
|---|---|
| `common.schema.json` | Shared security patterns, lineage, intervals, transforms, grids and split types |
| `generator.schema.json` | Generator/evaluator-only reference, provenance, vintage, monthly source ledger, seed and DGP settings |
| `manifest.schema.json` | Estimator-safe CSV/config: calendar controls, oracle transforms, fixed uncertainty, common grid |
| `truth.schema.json` | Evaluator-only dataset truth and hash bindings; shared across different estimator run IDs |
| `result.schema.json` | Estimated coefficients/intervals, holdout contributions, response curve, diagnostics |
| `comparison.schema.json` | Two same-data/holdout/grid results, signed differences and sensitivity flags |
| `evaluation.schema.json` | Result versus private truth: recovery errors, interval coverage and detection outcomes |

Draft 2020-12 schemas use local references registered offline by `validate.py`. The
`.invalid` schema IDs are identifiers, never download endpoints. All structured objects
reject unknown fields. Numeric values must be finite; months are ASCII YYYY-MM, years
0001–9999. Paths are canonical relative POSIX paths without dot/parent/empty segments,
absolute paths, backslashes, encodings or control characters. Existing symlink parents
must resolve within the project; writes still need safe handling against concurrent
changes. Hashes cover exactly the bytes parsed by the validator.

## CSV separation

Estimator header, exact order:

```csv
period,synthetic_media,semi_synthetic_outcome
```

Generator-only reference header:

```csv
period,observed_registrations
```

The reference column's class is `observed` for admitted KBA data and `synthetic` for
an explicitly synthetic development reference. Media and outcome are always synthetic.
Every column retains full lineage. The estimator accepts no reference/truth paths,
planted beta, noise/effect design fractions, arbitrary CSV columns or regressor hooks.
Calendar controls derive from period; breaks require dated evidence and predeclaration.

Numbers use finite ASCII decimal/scientific notation without whitespace/underscores;
reference counts must be nonnegative integers, media nonnegative, outcome continuous
and potentially negative. Blank records/fields, missing/duplicate/out-of-order months
and nonadjacent/out-of-range splits are rejected; quoted fields and CRLF are supported.

`purpose=contract_fixture` is for schema examples only. `development_benchmark`
requires >=48 training and >=12 holdout months and >=20 residual df. The latter is an
admission rule, not a power guarantee. Task 01 must use `--require-benchmark` before
model execution. The six-row examples are not a DGP run, fitted model or recovery claim.

## Validation

From repository root, Python 3.12, `jsonschema==4.26.0` (including its referencing dependency):

```sh
python3 contracts/validate.py
python3 contracts/validate.py contracts/examples/generator.json --kind generator
python3 -m unittest discover -s tests -v
```

For future benchmark artifacts:

```sh
python3 contracts/validate.py path/to/manifest.json --require-benchmark
python3 contracts/validate.py path/to/result.json --kind result
python3 contracts/validate.py path/to/comparison.json --kind comparison
python3 contracts/validate.py path/to/evaluation.json --kind evaluation
```

Result validation opens only the estimator manifest/data; comparison opens its hashed
results. Only generator/truth/evaluation validation reads the reference. Validators
check linkage, intervals, counts, contribution sums, common grids, signed deltas,
coverage/detection booleans and diagnostic rules. They **do not** fit a model, compute
transforms or certify confidence coverage, historical provenance or process isolation.
No detection limit is calibrated: `effect_below_detection_limit` must remain `null`.
The scientific document states conditions required before enabling that flag.

Stage A alone is executable in these contracts. B (train-only search/misspecification)
and C (replicated scenario evaluation) are documented protocols to review before their
own implementation. Per-run intervals are pointwise/conditional; no independent-fit
interval is fabricated for a difference on shared data. No field represents real
causal Tesla marketing ROI.
