# Task 01F.1 — extended Google Trends import

## Status: file received, empirical admission pending

PR #8 was verified merged at `66abaddd7b736792230a1d325fb498a74f8f3810` before
branching from updated main. The user-uploaded `multiTimeline.csv` actually exists
outside this checkout. Its original **2,947 bytes** match SHA-256:

`28e0b00b697ceb65833ca5bb2039d43c0ab4350d9a732e884edd3a44fe0da84e`.

Structural inspection found **274 unique ordered monthly rows**, January 2004 through
October 2026, with the native German Tesla/Germany header and all-category label.
The user confirms choosing the full available history. The later user screenshot confirms
`https://trends.google.com/trends/explore?date=all&geo=DE&q=Tesla`, the search term,
Germany, all categories and Web Search. The user reports downloading "today and now"
on 2026-10-23 (Europe/Berlin). This is **not a recorded exact download timestamp**;
no seconds or offset-aware instant were invented. Exact time and private-use rights
review remain pending; UI evidence is not proof of Google authorship or publication
permission. The screenshot itself, which contains unrelated personal UI details,
is not redistributed.
No real index values or derived real-value CSVs are committed or published.

The current private run is `--inspect-pending`: it emits only a structural report,
source hash, unresolved fields and `empirical_admission=false`; no normalized source
or subset CSVs. It does not fabricate a successful real-data import. The generalized
admitted path was exercised with explicitly synthetic fixtures only. Task 01F's old
empty indicators and historical blocked-coverage record remain unchanged.

## Windows and normalization

Metadata **1.1.0** adds two fields without changing legacy **1.0.0** behavior:

- `source_window`: explicit first/last monthly buckets, e.g. 2004-01–2026-10.
- `analysis_windows`: required 2018-01–2025-12 (`analysis_2018_2025`), optionally
  2021-01–2025-12 (`common_2021_2025`). Each must lie inside the source domain.

`request_window` and `normalization.window` continue to describe the **original
single request**, never a narrower analysis subset. They accept either explicit
attested dates or, in 1.1.0, `{"selection":"all_available_history"}` with an actual
Explore URL containing `date=all`. The latter avoids inventing a request end-day for
an all-history export. Its source buckets still have explicit monthly extent; the
actual retrieval timestamp is separately mandatory before admission. Explicit date
requests must begin on a month boundary; a truncated last month remains partial even
if retrieved later. Query/geography/category/property, source extent, normalization
and URL must agree. Version 1.1 supports the actually evidenced URL omitting `cat`
(default 0), while still requiring explicit category 0 in the sidecar; omitted
`gprop` denotes default web search. This does not infer missing sidecar settings. Do not manufacture an exact URL from a plausible example.

The 96- and 60-month subsets retain **exactly the original per-month index values**.
No max-to-100 rescaling, annual splicing, interpolation, averaging or weekly conversion
occurs. A full-window index remains labeled as such after selection. A subset is not
a fresh native Google request normalized on 2018–2025. Missing buckets are explicitly
missing rows, not implied zeros; duplicate/disordered/malformed periods are rejected.

### Completeness and value status

The full admitted source output carries independent columns:

- `value_status`: `observed_index`, `censored_below_one`, `missing_in_export` or
  `not_in_export`; numeric zero is retained and `<1` is never replaced by 0/0.5.
- `period_completeness`: `completed_calendar_month` for past full calendar buckets,
  or `partial_or_unverified_period` for the retrieval month or truncated request end.

The partial final source value is retained unchanged; it is excluded from eligible
completed-month observation lists and never used as a completed historical month.
Calendar completion does not prove exhaustive search measurement, stable vintage or
causal relevance. With the current file and unknown actual export time, October 2026
remains explicitly **partial or unverified**. The pending inspection labels source
observations unverified; it cannot admit historical rows merely because they parse.

Admitted output consists of a full-source CSV and 96-/optional 60-month CSVs, all
private. Each output has its hash, source raw hash, bucket window and counts in
`coverage.json`; the report retains the original metadata, normalization and derivation.
Source counts distinguish numeric, censored, blank, absent and partial periods.
Synthetic reports always list no real observation months. Legacy Task 01F outputs
keep their three-column format and stricter complete-month request rules.

## Private handoff

Copy `data/organic_attention/trends_extended_metadata.template.json` to a private
sidecar **outside Git**. The template is intentionally incomplete and cannot pass
admission. Fill only actual, user-attested facts:

1. Exact original Explore URL and offset-aware download timestamp/timezone, not
   upload/inspection time. The task's date is not an invented retrieval instant.
2. Actual search property and category. Header labels alone do not establish UI filters.
   The admitted interface remains DE / category 0 / Web Search; other settings fail.
3. Exact query kind, value/ID and CSV label. A search term `Tesla` is not automatically
   the automotive company topic. Topic evidence must be separately reviewed.
4. Unchanged raw-file SHA-256 and locale; preserve full request and source windows.
5. Explicit exporter attestation and lawful private-use review with evidence/note.
   `rights.redistribution` remains `not_verified` until separately reviewed.

No raw/derived real values may be copied into the public repository without a
**separate verified rights and publication decision**. Even a sidecar marked permitted
does not authorize publication by this task. All CLI output directories must be new
and outside the checkout. The original upload is read, never rewritten; generated
outputs are separate. Keep the raw bytes and private sidecar safely for reproducibility.

```sh
# Structural inspection only: no admission or value CSVs.
python3 -m attention.import_trends \
  --csv /PRIVATE/multiTimeline.csv \
  --metadata /PRIVATE/pending_metadata.json \
  --output-dir /PRIVATE/new-inspection --inspect-pending

# Only after source/timestamp/settings/private-use evidence is complete:
python3 -m attention.import_trends \
  --csv /PRIVATE/multiTimeline.csv \
  --metadata /PRIVATE/attested_metadata.json \
  --output-dir /PRIVATE/new-admitted-import
```

Actual local inspection artifacts are at
`/workspace/private-attention/task01f1/inspection-with-ui-evidence/pending.json`; the incomplete sidecar
is next to that directory. They are not in Git. No authenticated Google acquisition
or model experiment is part of this task. A checksum identifies bytes, not authorship
or legal entitlement; fabricated provenance cannot be universally detected by parsing.

## Scientific limits and later KBA handoff

Google Trends is sampled and request-relative. Independent exports may differ;
retain separate hashes/retrievals and report differences rather than silently averaging
or selecting an export using registrations. No repeated authorized exports were
obtained here. Do not splice independently normalized requests. Literal `Tesla` may
include Nikola Tesla, political/news interest or unrelated intent; a company-topic
sensitivity series requires a separately frozen query/export, not favorable-outcome
selection. German search origin is not citizenship, buyers or creator audience.

A normalized search-interest index is neither absolute search volume, media spend,
impressions, favorability nor causal advertising exposure. The full export extends
beyond 2025; its scale may use later observations. Do not represent its subsets as
historically available forecasts. Retrospective selection does not establish as-of
availability, and the existing KBA Point-in-time restrictions remain untouched.

Before any later join with Tesla registrations: verify the original source/settings,
actual retrieval and rights, admit the source vintage, review all quality/missingness
flags, freeze the subset/hash and original scale, align complete monthly buckets, and
explicitly label retrospective use. The optional BEV window remains 2021–2025; no BEV
history is invented. Pre-specify transformations and holdout rules before looking at
outcomes, including availability/later-window normalization caveats. No correlations,
lag selection, regressions, significance tests, ROI, causal effects, MMM changes or
new simulations are performed in this PR.

## Reproduction and validation

```sh
# Positive example is wholly synthetic, not the uploaded values:
task01f1_tmp=$(mktemp -d)
python3 -m attention.import_trends \
  --csv tests/fixtures/trends/SYNTHETIC_extended.csv \
  --metadata tests/fixtures/trends/SYNTHETIC_extended_metadata.json \
  --fixture --output-dir "$task01f1_tmp/import"
python3 -m unittest discover -s tests -p 'test_trends*.py' -v
```

No new dependencies or live CI calls. Targeted tests exercise 274 individual periods,
unchanged 96/60-month subsets, both native headers/BOM/line endings, source hashes,
value statuses, partial months and legacy/private-output protections. Exact local
full-suite and remote CI evidence is reported in the workorder and Draft PR.

## Executed validation (local)

Python 3.12.14, existing pinned environment, 2026-10-23:

- Full suite: **175 tests passed**, including 11 new extended-import tests (32.958 seconds). All 17 existing Trends-import tests remain green.
- The original 17 Trends-import tests and 11 extended-import tests pass.
- Both example contract validators; blocked/empty-attention and campaign artifact checks; KBA audit and fixture extraction/re-extraction verification: passed.
- Existing deterministic Stage-A smoke run and bundle verification passed in a temporary directory, without changing configurations/results or running an observed-data analysis.
- Ruff for touched Python files and `git diff --check`: passed.
- Protected KBA/Statistical Contracts/MMM/example/estimator and old empty empirical artifacts are unchanged. Original uploaded raw hash still matches.

Remote CI evidence belongs to the exact Draft PR commit and is recorded there after
completion. Local success and synthetic coverage do not imply empirical admission.
