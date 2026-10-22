# Proposed file contracts v0.1.0

Task 00 proposal; no model implementation or generated benchmark outputs.
**Statistical review blockers:** the baseline-as-regressor proposal is rejected and
stability outputs remain underspecified. These four contracts are technically tested,
not yet sufficient for the revised Task 01. See [Task 01 readiness](../docs/TASK_01_READINESS.md).
JSON Schema dialect: Draft 2020-12, unknown fields rejected. All paths are canonical POSIX-style paths relative
to repository root: no dot/parent/empty components, absolute paths, Windows separators,
URL encodings or control characters; hidden components such as `.cache` are allowed.
Months are ASCII YYYY-MM, years 0001–9999. Hashes are lowercase SHA-256. All numeric values must be finite.
The estimator must reject failures without leaving a successful result file.

| File | Producer -> consumer | Meaning |
|---|---|---|
| `manifest.schema.json` | orchestration -> estimator | Data checksum, exhaustive column lineage, temporal split, fixed transform/OLS settings; no truth path |
| `truth.schema.json` | generator -> evaluator only | Seed/RNG, generator version, DGP parameters/coefficients/noise and data binding |
| `result.schema.json` | estimator -> evaluator/report | Coefficients, train/holdout diagnostics, software and input identities |
| `comparison.schema.json` | comparator -> report/future read-only MCP | Two hashed results on identical evaluation support and explicitly signed deltas |

## CSV input

UTF-8, comma delimiter, decimal point, header in this exact order:

| Column | Type/unit | Rule |
|---|---|---|
| `period` | YYYY-MM | Unique, sorted, complete monthly index |
| `observed_registrations` | nonnegative integer count | Immutable observed Tesla DE reference **or explicitly synthetic fixture stand-in** |
| `synthetic_media` | nonnegative finite number, synthetic currency units | Seeded exposure in later DGP, never claimed observed spend |
| `semi_synthetic_outcome` | finite continuous target, count-equivalent units | Separate injected outcome, never overwrites reference; can be negative under additive noise |

Each column has class, publisher, source/generator, access date, geography, grain,
unit, rights, redistribution status, transformations and limitations. For real observed
sources include exact vintage/revisions, source/license URL and known gaps in those
fields; retain original source bytes and checksum separately in the data admission
record. `input_kind` prevents calling a fixture's reference column observed.
Do not infer public-data redistribution permission from schema validity.

`examples/fixture.csv` and `examples/manifest.json` are a six-row hand-authored
contract example, **not** Tesla data or output of the proposed DGP. There is no
truth file for those manually authored values and no claim they follow the equation.
Truth/result/comparison shapes are exercised with explicitly fabricated in-memory
objects in tests, never saved or presented as model results.

## Validation

From repository root, with Python >=3.11 and `jsonschema==4.26.0` installed:

```sh
python3 contracts/validate.py contracts/examples/manifest.json
python3 -m unittest discover -s tests -v
```

For an isolated install when needed:

```sh
python3 -m venv /tmp/aas-contracts-venv
/tmp/aas-contracts-venv/bin/python -m pip install jsonschema==4.26.0
/tmp/aas-contracts-venv/bin/python contracts/validate.py
/tmp/aas-contracts-venv/bin/python -m unittest discover -s tests -v
```

`validate.py` validates manifest shape, formats, resolved input/output containment
(including symlink parents), CSV hash/content from the same bytes, finite JSON/CSV values,
integer/nonnegative reference, exposures, complete month index and temporal split.
Empty/whitespace fields and blank records are rejected rather than silently skipped.
Numbers use ASCII decimal/scientific notation without whitespace or underscores;
quoted fields and CRLF are accepted. The final continuous outcome may be negative.
For the other schemas, use `Draft202012Validator` with `FormatChecker`.
JSON Schema validates shapes/ranges, **not** provenance truth, file existence,
recovery, identical holdout support, result arithmetic, process isolation, statistical
adequacy or numeric finiteness in arbitrary nonstandard JSON loaders. Those semantic
checks are required in Task 01 before reporting outputs. See `docs/DECISIONS.md`.
