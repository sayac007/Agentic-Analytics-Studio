# Task 01G — first results: empirical analysis blocked

## What actually happened

PR #9 was verified merged at `9013913bbca7f60efe7226ad797e15d16d9d90ae` before
branching from updated main. The original user-uploaded file is still present
privately. Its SHA-256 matches
`28e0b00b697ceb65833ca5bb2039d43c0ab4350d9a732e884edd3a44fe0da84e`.
The previously inspected 274 monthly rows, source URL and screenshot evidence are
preserved; no index values or screenshot/personal UI details are published.

**No real Trends/KBA join, correlation, diagnostic test, regression or plot was run.**
The original download was reported on **2026-10-23 Europe/Berlin**, but the exact
clock time is unknown. Source-URL/filter evidence cannot manufacture it. Private-use
rights confirmation under reviewed Google Terms/export conditions was explicitly
requested and remains unconfirmed. No independent legal verification is claimed.

A real-input CLI attempt using the existing private sidecar was actually made and
**refused at the retrieval-timestamp gate**, before KBA values were joined or any
diagnostics were calculated. The expected error was
`Timestamp needs an explicit timezone and exact day`; no results directory appeared.
The machine-readable [status](../data/organic_attention/task01g_status.json) records
pending admission, not empirical success. Existing importer rules were not weakened.

The [protocol](TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md) was committed separately
**before** implementing or running diagnostics (commit `24b3462`). Its hash is bound
to all executable outputs. All numerical exercises in this task used **clearly
synthetic software fixtures only**, not the real Trends file or actual KBA values.
No synthetic result is presented as evidence of Tesla attention effects, statistical
power, stationarity or model performance.

## Implemented, but not empirically executed

`python3 -m attention.econometrics` consumes a private extended-import bundle, raw
export, metadata, separate human admission record and verified KBA data. Before any
analysis it:

1. Revalidates the original bytes/provenance through importer 1.1.0, including its
   exact timestamp, private-use gate and completed-month rules.
2. Requires the frozen literal Tesla / DE / Web / all-category / full-history query,
   source/metadata/KBA/protocol hash bindings and a human source/terms review record.
   The human review cannot predate export. An unreviewed checkbox is insufficient;
   the tool records an actual human review statement, not its own legal judgment.
3. Re-derives full source and 96-/60-month subsets and byte-checks every imported
   artifact/hash. No new renormalization, splicing, filling or weekly conversion.
4. In real mode, requires the unchanged repository KBA file and runs its existing
   offline provenance/admission audit. Fixture mode requires fictional KBA source
   markers and cannot consume the actual KBA table.
5. Validates an exact ordered one-to-one monthly Tesla join; rejects duplicates,
   missing/censored/partial/nonfinite rows rather than silently imputing.

The fixed implementation provides private level/log1p/profile plots, ACF/PACF with
pointwise assumptions, fixed-specification ADF/KPSS with warnings, first-difference
single-lag associations 0–3 plus 4–6 sensitivity, three-lag HAC intervals, and Holm
adjustment across all 14 window-by-lag comparisons. It also computes the frozen
calendar baseline versus joint Trends-lags-0–3 retrospective conditional 2025
pseudo-holdout, using pre-2025 attention scaling/model fits only.

`diagnostics.json`, `associations.csv`, six standalone PNGs and `report.md` are private.
They carry conspicuous `SYNTHETIC_FIXTURE_ONLY` or
`PRIVATE_RETROSPECTIVE_EXPLORATORY` labels, input/protocol/implementation hashes,
versions, output inventory hashes and warnings. ACF/PACF figures display zero-centred pointwise reference
bands derived from the stored intervals. Stationarity assumptions and structural-break
limitations are explicit. No historical real-time forecasting claim follows.

The sample is 2018–2025 plus a separate 2021–2025 Tesla view; the latter is not an
invented BEV extension. Quarter ends are fixed controls. Subsidies, prices, launches
and supply remain explicitly unmodeled confounders absent independently reviewed
series; no residual/significance-driven dummies. 2022 is a descriptive window only,
without oil-price/war attribution. No 2026 registrations or Iran-war effect analyzed.
No opportunistic ARDL/VAR/model search, Monte Carlo, MMM change or causal ROI claim.

## Reproduction — software fixtures only

Python 3.12, repository root; new numerical/plotting dependencies and their transitive
requirements are pinned in `requirements-attention.lock` over the existing runtime:

```sh
python3 -m pip install -r requirements-attention.lock

task01g_tmp=$(mktemp -d)
python3 tests/fixtures/econometrics/generate.py --output "$task01g_tmp/fixture"
python3 -m attention.econometrics --fixture \
  --raw tests/fixtures/trends/SYNTHETIC_extended.csv \
  --metadata tests/fixtures/trends/SYNTHETIC_extended_metadata.json \
  --import-dir "$task01g_tmp/fixture/import" \
  --admission "$task01g_tmp/fixture/SYNTHETIC_admission.json" \
  --kba "$task01g_tmp/fixture/SYNTHETIC_kba.csv" \
  --output-dir "$task01g_tmp/results"

OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python3 -m unittest discover -s tests -v
```

The fixture generator uses one fixed analytic formula, not real KBA values, an
estimated relationship, a Monte Carlo experiment or recovery benchmark. Its positive
execution checks only software and labels. No data/API request or credentials in CI;
the added smoke step uses only the committed synthetic Trends fixture and temporary
fictional KBA data. Plots/tables stay outside public Git.

## Required next handoff

Do **not** fill an invented clock time into the old file's metadata or use a later
upload timestamp as the old download time. If exact original retrieval evidence is
unrecoverable, obtain a **new official manual export** with the same frozen request:
`https://trends.google.com/trends/explore?date=all&geo=DE&q=Tesla`.
Use the native Interest-over-time CSV, DE, Web Search, all categories, search term
Tesla. Respect any platform 429/CAPTCHA/authentication restriction.

At the actual new export, accurately record the download-completion instant with
its timezone and precision, preserve the original bytes, and calculate SHA-256.
A new download event needs its own evidence even if its content happens to match
an older file. Keep both originals separate; no timestamp backdating or silent
replacement. Confirm lawful private analytical use **after reviewing** Google Terms
and applicable export conditions; value redistribution needs a separate decision.

Complete the existing extended importer sidecar privately with actual facts, then
run the importer without fixture mode to a new private directory. Keep 2026's current
month partial and preserve the full-request scale, including its post-2025 vintage
caveat. Make a private copy of
[`econometric_admission.template.json`](../data/organic_attention/econometric_admission.template.json),
fill actual raw/metadata/KBA/protocol hashes, review time and review evidence, and
only after human review change its status to `admitted_private_retrospective` and
confirm source/terms review. The template is pending, not a pre-granted approval.

```sh
python3 -m attention.econometrics \
  --raw /PRIVATE/new-original.csv --metadata /PRIVATE/new-metadata.json \
  --import-dir /PRIVATE/new-admitted-import \
  --admission /PRIVATE/actual-human-admission.json \
  --kba data/kba/derived/observations.csv --output-dir /PRIVATE/new-diagnostics
```

The historical KBA as-of gate remains blocked. Any eventual comparison is private,
retrospective and exploratory; late Trends scaling/availability and reverse causality
prevent real-time or causal advertising interpretation. Transformations, lags and
holdout were fixed before results. No empirical result is owed or fabricated while
source/legal gates are unresolved.

## Validation record

Executed local and exact-commit CI evidence is recorded in the workorder/Draft PR.
The first targeted negative test exposed a duplicate outside the analysis window
being ignored; all source-period uniqueness/order is now checked before selection.
Ruff's fixture-script import-placement warning was also corrected. Final test results
are distinguished from these initial failures; empirical admission remains blocked.

### Final local checks (2026-10-24)

- Python 3.12.14 with `requirements-attention.lock`; `pip check`: no broken requirements.
- Full suite: **187 tests passed**, including **12 new econometric-path tests**, 37.124 seconds.
- Targeted new suite: 12 passed; repeated fixture CLI execution produced identical numerical JSON, six labeled plots and hash-checked private output inventories.
- Both existing example validators, KBA audit, blocked/empty-attention and campaign artifact checks: passed.
- Ruff on new Python/test files, whitespace checks and protected-artifact diffs: passed.
- Real private CLI attempt: **expected refusal**, no output directory, no empirical analysis.

Remote checks are reported only after the exact PR head's GitHub Actions runs finish.
