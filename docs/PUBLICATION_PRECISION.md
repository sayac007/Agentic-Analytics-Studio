# Task 01B.1 — publication precision and admission v0.2.1

This is a **generator-provenance patch**, based on `main` merge
`8bb51c967f011df5db45be659001dce593a3045d` after confirming PR #4 merged.
It changes neither the MMM engine, estimator interface/isolation, synthetic example,
statistical calculations nor the previously agreed Stage-A results. No new data,
interpolation, simulation or model experiment is introduced.

## Five separate facts

| Fact | Representation | Meaning |
|---|---|---|
| Reporting period | release `period` (`YYYY-MM`) | The month measured; never a release date |
| Publication date | new `publication_date: {precision, value}`; legacy `published_on` | Documented publication date/month, or explicitly unknown |
| Retrieval | new `retrieved_at` | Own retrieval date or RFC3339 timestamp, preserving available precision |
| Vintage | existing `sha256` and `version` | Exact immutable source bytes plus the publisher/version description |
| Proven availability | new `available_as_of` | Nullable, separately evidenced availability of **those exact source bytes** |

KBA's existing `period`, `publication`, `retrieved_on`, `sha256` and `version`
remain unchanged in the source catalog. `kba.pipeline.release_record` maps them into
the release contract. Since existing retrieval metadata specify only a day,
`retrieved_at` accepts an ISO date as well as an offset-aware RFC3339 timestamp;
no midnight or other download time is fabricated. This patch does not promote
`retrieved_on` to historical availability.

`publication_date` permits exactly:

```json
{"precision": "day", "value": "2020-02-07"}
{"precision": "month", "value": "2025-02"}
{"precision": "unknown", "value": null}
```

These examples correspond to verified source metadata for January 2020, January
2025 and January 2018. No first/last-day proxy for a month is allowed. See
[`release-precision.json`](../contracts/examples/release-precision.json).
Missing publication information remains missing; raw hashes do not create dates.

## Versioning and backwards compatibility

`generator.schema.json` accepts **0.2.0 and 0.2.1**. New `release.schema.json`
factors release provenance into an offline-resolved schema. All estimator, truth,
result, comparison and evaluation component versions remain **0.2.0**; the patch
changes provenance only. Existing generated/synthetic artifacts are not migrated or
rewritten. Registry/path/numeric/provenance protections remain in force.

- A v0.2.0 generator still requires the original release record with `published_on`
  as a full ISO date. It cannot silently use new semantics or claim a new regime.
- A v0.2.1 generator requires `admission_regime`, exactly
  `retrospective_immutable_reference` or `historical_point_in_time`.
- v0.2.1 accepts either an unchanged legacy full-day record **or** the new record
  requiring `publication_date`, `retrieved_at` and nullable `available_as_of`.
  Supplying both publication representations is rejected. Old fixtures remain valid.
- The historical regime requires `as_of` as an offset-aware RFC3339 timestamp and
  `reference_kind=observed_kba`. The retrospective regime rejects `as_of`, preventing
  an irrelevant cutoff from being mistaken for a checked historical information set.
- A legacy accepted generator/record has **no implied Point-in-time admission**.
  To claim that regime, migrate the record explicitly and provide vintage-bound proof.

No `publication_date`, reference, availability evidence, regime, retrieval field or
truth parameter is added to the estimator manifest/CSV. Structural-break evidence
rules are unchanged: this patch is **not** permission to use undated events as controls.

## Two admission regimes

### Retrospective immutable reference

Missing exact publication days do not block a retrospective semi-synthetic reference
if the official reporting month/definition, observed counts, rights, immutable raw
and normalized hashes, unique source vintage and contiguous series are verified.
The existing >=48 training months, >=12 holdout months and >=20 training residual df
floors still apply. Actual estimator rank must be checked later; data admission is
not scientific validation, power or a claim about real marketing effects.

Unresolved duplicate vintages, raw/normalized hash drift, unknown layouts/definitions,
invalid provenance, rights conflicts, internal month gaps and insufficient coverage
still fail closed. The published label and parser profile must match the intended
all-powertrain versus BEV series. Table-only fixtures remain blocked in both regimes.
Annual-reconciliation conflicts also block both regimes. No observed data are padded,
dropped to hide an internal gap or reclassified synthetic to bypass a gate.

### Historical Point-in-time / as-of

A retrospective success says nothing about what was known historically. Day precision
alone does not prove the currently retrieved vintage existed on that day, especially
for revised statistics. A filename, URL `v=2`, publication month, source hash by itself
or a later download does not establish availability before a historical cutoff.

`available_as_of` is therefore null unless there is reviewed evidence. A non-null
record requires:

- `timestamp`: offset-aware RFC3339 availability witness;
- `source_sha256`: exactly the release's source hash;
- `evidence`: existing contained relative-path/SHA-256 artifact; actual bytes checked;
- `evidence_url`: HTTPS primary/archive evidence location;
- `scope: exact_source_vintage`.

This is the earliest availability witness supported by the supplied reviewed evidence,
**not a claim to know the first-ever publication instant**. It is a witness that the
exact snapshot existed by that time, not an invented conversion of month/day precision
into an instant. This minimal v0.2.1 historical gate conservatively requires **both day-precision
publication and separate exact-vintage availability evidence**. Unknown/month publication
dates remain blocked even if a separate witness is supplied; broader interval-based
information-set reasoning needs a separately reviewed policy. Conversely, a precise
publication date without vintage-specific evidence also fails. No missing publication
day is inferred from an availability witness.

The validator checks evidence hash/path, vintage binding, plausible chronology and
availability no later than the declared `as_of`. It rejects evidence predating known
publication dates or postdating the recorded retrieval (using its stated precision).
It does not automatically verify the historical meaning of arbitrary evidence text;
primary-source review remains required. A broader multi-vintage backtesting platform
or per-origin release selection is not implemented by this patch.

## Deterministic KBA reassessment

[`coverage.json`](../data/kba/derived/coverage.json) now includes baseline ID/definition,
actual checked window, length/split/df, publication precision counts, provenance/vintage
status, source-catalog and normalized-data hashes, and explicit independent regime
statuses/reasons. `status` remains a convenience alias with an explicit
`status_regime=retrospective_immutable_reference`; consumers must read the named
historical result for historical use. Do not interpret an unqualified `admitted` as
universal approval. The known historical report has `as_of=null` and is blocked:
no historical cutoff is requested and no exact-vintage availability evidence exists
in the already verified catalog. Supplying a cutoff alone does not fix that.

| Baseline | Verified window | Months | Longest-window train/holdout | Publication day/month/unknown | Retrospective | Historical as-of |
|---|---|---:|---|---|---|---|
| Tesla, all powertrains | 2018-01–2025-12 | 96 | 84 / 12 | 14 / 58 / 24 | admitted | blocked |
| Toyota, all powertrains | 2018-01–2025-12 | 96 | 84 / 12 | 14 / 58 / 24 | admitted | blocked |
| VW, all powertrains | 2018-01–2025-12 | 96 | 84 / 12 | 14 / 58 / 24 | admitted | blocked |
| BEV market, BEV only | 2021-01–2025-12 | 60 | 48 / 12 | 10 / 50 / 0 | admitted | blocked |

The common future recovery window remains 2021–2025 (48/12); longer brand-only
windows are not silently substituted into paired comparisons. The BEV series has
not been extended to 2018. The source catalog, 4,944 observed rows, exact extraction
locations, selection, descriptions and annual checks remain byte-for-byte unchanged.
Only the admission report and its inventory binding were regenerated.

Reproduce the report **offline from existing data**, with the unchanged pinned KBA
runtime, using the existing normalized-data audit. For raw-to-report regeneration,
use the previously acquired cache; do not refresh sources for this task:

```sh
.venv/bin/python -m kba audit
.venv/bin/python -m kba extract --raw-dir EXISTING_RAW_CACHE --output NEW_DIRECTORY
.venv/bin/python -m kba verify --raw-dir EXISTING_RAW_CACHE --output NEW_DIRECTORY
.venv/bin/python contracts/validate.py
.venv/bin/python contracts/validate.py contracts/examples/generator.json --kind generator
.venv/bin/python -m unittest discover -s tests -v
```

`audit` recomputes decisions and their hash bindings; raw verification still requires
the raw cache. No new live downloads are required or performed. The existing CI audit
and fixture re-extraction steps exercise the new decisions offline.

Remaining constraints: observed references still need explicit generator manifests,
immutable two-column exports and a separately authorized execution task before model
use. Historical exact-vintage availability is not verified. Absolute-effect calibration,
Stage-C aggregate contracts, simulation precision/recovery thresholds and operating
characteristics remain separate scientific decisions. Retrospective admission does
not resolve them or authorize additional model work.

## Executed checks (2026-10-23)

Python 3.12.14, existing pinned `/tmp/task01b-ci-venv` with requirements-kba.lock:

- Both original example validator commands passed, including the unchanged v0.2.0
  synthetic generator fixture.
- `python -m unittest discover -s tests -v`: **115 tests passed** (99 existing,
  16 new provenance/admission tests), 30.369 seconds in the final local run.
- Full cached-source `kba verify` re-extracted all 96 workbooks and reproduced the
  committed report/data bytes; `kba audit` passed without network access.
- Offline fixture extraction and re-extraction verification passed; existing full-suite
  tests also verify deterministic extraction and that fixtures remain blocked.
- `git diff --check` and Ruff unused-import checks passed on the touched KBA/test code.
- `studio/`, `config/`, `examples/task-01a/`, dependency locks, source catalog, observed
  CSV, extraction locations and descriptive/selection/reconciliation outputs have
  no changes. Existing numerical/end-to-end regression tests ran as part of the
  required suite; no new model experiment, benchmark fit or live acquisition was run.

The first suite identified the schema-inventory test's expected seven-schema list;
it now includes the new release schema while still checking all schemas. When the
historical rule was made explicitly day-precision-only, two rejection-message checks
needed updating to recognize that earlier failure reason. The final run above passes.
An attempted report rebuild under system Python correctly refused unpinned parser
versions; rebuilding under the pinned environment succeeded without changing inputs.
Remote Actions evidence belongs to the exact PR head and is recorded in the Draft PR;
local success alone is not remote CI evidence. Do not merge automatically.
