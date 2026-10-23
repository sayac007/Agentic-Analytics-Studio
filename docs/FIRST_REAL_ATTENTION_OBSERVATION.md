# Task 01F — first real attention observation: acquisition blocked

## Actual result

**No real historical observation was acquired.** The legitimate Google Trends
Explore request returned **HTTP 429** on 2026-10-23 at **17:21:29 Europe/Berlin**
(15:21:29 UTC). Empirical acquisition stopped; no retry, alternate data endpoint,
CAPTCHA workaround or unofficial scraping client was used. No browser/UI-export
capability or authorized official Trends API is available in this tool environment.
Google's export/measurement help was separately readable (HTTP 200), but contains
instructions, **not a Tesla dataset**.

[PR #7](https://github.com/sayac007/Agentic-Analytics-Studio/pull/7) was verified merged
at the required `dda2cef6badec65e9e87f2ef795edf0180ffa745`; this task branches from
that current main as `data/task-01f-first-real-attention`.

- Real monthly observations: **0**; actual returned frequency: **not observed**.
- 2018-01–2025-12: **0/96 observed**, **96 unknown**.
- Common Tesla/BEV window 2021-01–2025-12: **0/60 observed**, **60 unknown**.
- No observed monthly CSV is added. Existing empty empirical indicators/summary,
  observations and synthetic-only adapter remain unchanged.
- No independent repeat exports or alternative-query observations exist; sampling
  stability and query sensitivity cannot be measured in this task.

[Access evidence](../data/organic_attention/task01f_access.json) records exact URLs,
UTC request timestamps, status and response hashes; raw responses remain outside Git.
[Real-data coverage](../data/organic_attention/real_data_coverage.json) is reproducible
from that log and explicitly says `not_empirically_populated`, not zero attention.

### YouTube fallback preflight

The named `YOUTUBE_API_KEY` and `GOOGLE_API_KEY` variables are absent. A general
`GOOGLE_APPLICATION_CREDENTIALS` binding/file exists, but its checked type metadata
did not establish YouTube authorization; it was not repurposed or sent to a service.
No tokens, account identities or scopes were extracted. No verified YouTube
owner/API access or resolved channel-ID set was available. Consequently no
fallback inventory was collected, no synthetic ID was invented, and no comments or
personal data were requested. This is **not_tested_no_authorized_access**, not a claim
that YouTube has no historical content. A later authorized fallback must freeze actual
IDs and inclusion rules first, separate Owned/independent creator/editorial channels,
review sponsorship, paginate fully and report surviving-content/deletion limitations.
German language remains distinct from German audience reach; today's views cannot be
historical monthly views.

## Exact manual handoff

A user with legitimate access can supply a native export. If the browser also reports
429, authentication restrictions or CAPTCHA, respect the platform instructions; do not
bypass them. There is no requirement to manufacture a successful download.

1. Open [this exact Explore request](https://trends.google.com/trends/explore?hl=de&date=2018-01-01%202025-12-31&geo=DE&cat=0&q=Tesla).
2. Explicitly select **Tesla — search term**, not a suggested person/company topic.
   Set **Germany (DE)**, **All categories (0)**, **Web Search**, custom dates
   **2018-01-01 through 2025-12-31**. Keep this one query alone, not a comparison
   chart with other terms. No query/window choice uses KBA registrations or outcomes.
3. In **Interest over time / Interesse im zeitlichen Verlauf**, use the official
   chart **Download CSV** action documented by
   [Google](https://support.google.com/trends/answer/4365538). Download the time chart,
   not regions, related topics or a screenshot. Record displayed settings and the
   final exact Explore URL; do not assume the returned granularity.
4. Preserve the downloaded bytes unchanged in a private directory **outside this
   repository**, for example `/workspace/private-attention/raw/`. Renaming a file
   is fine; do not open/save it through a spreadsheet or edit the raw contents.
   Filename convention:
   `google-trends_DE_Tesla-term_web_cat0_20180101-20251231_retrieved-YYYYMMDDTHHMMSSZ_export-01.csv`.
   Substitute the **actual** retrieval instant; do not use the example as evidence.
5. Inspect the header/date grain without changing the file. Supported native forms:
   `Month,Tesla: (Germany)` or `Monat,Tesla: (Deutschland)`, optionally preceded by
   the corresponding `Category: All categories` / `Kategorie: Alle Kategorien`
   line and blank lines. UTF-8 with/without BOM and CRLF/LF are supported.
   Record the actual locale. **`Week`/`Woche` or full date rows are rejected**;
   keep such a raw export and report the grain for a reviewed follow-up. Do not
   rename weeks into months or edit unexpected headers to force acceptance.
6. Copy [the metadata template](../data/organic_attention/trends_import_metadata.template.json)
   to a private sidecar, e.g. the same basename plus `.metadata.json`. It is
   intentionally **invalid until completed**. Set `retrieved_at` to the actual
   offset-aware timestamp (`+02:00` only when applicable), fill `raw_sha256`,
   `csv_locale`, the exact `source_url`, and the rights-review note. Only after
   confirming actual source and lawful private use set `export_attestation` and
   `rights.private_analysis_confirmed` to `true`. Leave redistribution `not_verified`
   unless its permission and evidence have actually been reviewed.
7. Compute the unchanged-file SHA-256, then import to a **new private output directory**:

```sh
# Repository root, Python 3.12; actual filenames must replace these placeholders.
sha256sum /workspace/private-attention/raw/EXPORT.csv
python3 -m attention.import_trends \
  --csv /workspace/private-attention/raw/EXPORT.csv \
  --metadata /workspace/private-attention/raw/EXPORT.metadata.json \
  --output-dir /workspace/private-attention/imports/EXPORT-01
```

The importer reads the original bytes without rewriting/copying over the raw export.
It records raw and sidecar SHA-256, the original retrieval timestamp/timezone and
full provenance, plus the generated monthly CSV hash. Existing output directories
and outputs inside this checkout are rejected. The result remains private by default;
do not commit any raw or normalized values until permission has been reviewed.
A valid populated import creates `observed_monthly.csv` plus `coverage.json`; a valid
all-missing export produces coverage only. This describes a future handoff, **not an
import already completed with real data**.

### Alternative queries and repeatability

The literal term can include Nikola Tesla or unrelated intent. A separately defined
company topic is a sensitivity series, not an automatic correction. If the official
UI offers a suitable company topic, record its **actual label and topic ID from the
URL**, retain its official evidence URL, and set `query.kind=topic`. The importer
accepts explicit `/m/...` or `/g/...` IDs but does not verify their semantic meaning.
No real topic ID has been confirmed here; the fake ID in tests is clearly synthetic.
Use separate raw files, metadata, series names and output directories for every
term/topic variant. Do not select the better-looking query using registrations.

If two independent authorized exports of the **same full request** can be obtained,
retain each with its own retrieval timestamp/hash and compare month coverage, censoring
and numeric differences. Report discrepancies; do not silently average or choose an
export because it predicts registrations better. None could be obtained here.
Never concatenate separately normalized yearly/window exports onto a common scale.

## Import contract and measurement rules

This is a single-source native-monthly importer, not a live collector or general data
platform. Its sidecar requires `origin=observed` for user exports and
`measure_role=attention_proxy`: the published index is an **observed search measure**,
its use as attention is a **proxy**. `export_method=official_ui_manual_csv`, an explicit
exporter attestation, actual retrieval timestamp, exact raw hash, query, DE geography,
category 0, web property, whole-month request window, monthly frequency and UTC buckets
are mandatory. This bounded importer does not implement a general official API client.

The normalization object must declare a **single request-relative 0–100 scale** with
exactly the same geography/window, no rescaling and no combined exports. Source URL,
CSV header and sidecar are cross-checked; mismatches, extra provenance fields, duplicate
or unordered months, out-of-window rows, malformed UTF-8/CSV/numbers, nonfinite or
out-of-range indices and unsupported frequencies fail. Historical request months must
be complete by retrieval; current/future months are not admitted as full observations.
Two independent request scales cannot be shown equivalent by matching one endpoint.

- Index `0` is preserved as an observed index zero, **not zero absolute searches**.
- `<1` remains a **censored `[0,1)` observation**, with empty numeric index and
  `censored_below_one` status, never converted to 0 or 0.5.
- An empty value is `missing_in_export`; an absent month is `not_in_export`.
  Both stay missing; the calendar is completed with labeled missing rows only.
- No interpolation, smoothing, splicing, averaging, week conversion or renormalization.
- Native monthly buckets use UTC under Google's long-window guidance. The retrieval
  timestamp's offset does not move a monthly bucket to another calendar month.
- A weekly response would need independently established week start/end and timezone,
  coverage/completeness rules and a declared day-overlap aggregation before any
  conversion. A weighted mean of weekly indices would still not become a native
  Google monthly index or absolute search count. That conversion is **not implemented**.

A checksum and exporter declaration establish binding and accountability, **not a
cryptographic proof of Google origin, true query relevance or legal rights**. Review
actual source/export evidence before scientific admission. Known repository fixture
bytes and repository CSV inputs cannot enter the observed CLI path. Arbitrarily
relabelled fabricated data cannot be detected universally by a CSV validator.

## Rights and limitations

Google's current [export/citation help](https://support.google.com/trends/answer/4365538)
was actually read: it documents CSV download and use/citation subject to
[Google Terms](https://policies.google.com/terms). It is not an unconditional open-data
license or proof of redistribution permission for a particular export. No real data
were supplied, so source-specific rights are **not verified**. The CC-BY license of
Google's separate public GitHub archive is **not applied to these UI exports**.
Only own factual access metadata and clearly synthetic test fixtures are distributed.
A future user must review private-use and sharing conditions; the tool records their
explicit review statement and never changes it to `permitted` automatically.
Even `permitted` in a sidecar does not by itself authorize publication by this task.

Search interest is sampled and normalized to the selected request/window; repeated
exports can vary. Germany is provider search-origin geography, not German citizenship,
Tesla purchasers or creator audience. Term ambiguity and news-driven interest remain.
Late reconstructed historical indices have **no verified historical as-of availability**;
existing KBA Point-in-time restrictions stay untouched. No data/term/window selection
uses KBA outcomes. No correlation, regression, lag optimization, significance test,
ROI, MMM modification or new simulation is performed.

## Offline reproduction

```sh
python3 -m attention.import_trends --check-blocked
python3 -m attention.transform --check
python3 -m unittest discover -s tests -p test_trends_import.py -v

# Fictional CSV software test only, never an empirical observation:
task01f_tmp=$(mktemp -d)
python3 -m attention.import_trends \
  --csv tests/fixtures/trends/SYNTHETIC_monthly.csv \
  --metadata tests/fixtures/trends/SYNTHETIC_metadata.json \
  --fixture --output-dir "$task01f_tmp/example"
```

The fixture produces `fixture_monthly.csv`, never `observed_monthly.csv`; its report
lists **no real observation months**. There are no new runtime dependencies or live
queries in CI. Existing empty attention artifacts remain byte-for-byte unchanged.

## Executed checks

Local validation, Python 3.12.14, 2026-10-23:

- `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s tests -v`: **164 tests passed**, including **17 new Trends-import tests**, 32.391 seconds.
- New tests cover native en/de CSV/BOM/CRLF, zeros/censoring/missingness, duplicates/order, malformed dates/rows/numbers, bounds/frequency/normalization conflicts, source URL/header binding, synthetic-versus-observed separation, deterministic private fixture CLI and blocked-report evidence.
- `python3 -m attention.import_trends --check-blocked`, existing empty-attention and campaign checks: passed; original empirical artifacts remain unchanged.
- Existing estimator/generator example validators and `python3 -m kba audit`: passed.
- Ruff check for new Python/test files and `git diff --check`: passed. Initial unused test imports flagged by Ruff were removed; final checks pass.

These validate software contracts on explicitly synthetic fixtures, not the origin
of a real export. Remote CI is reported separately in the Draft PR only after
successful completion for the exact commit. A blocked acquisition is not described as a successful empirical dataset.
The next scientific step is the lawful manual export and private validation above,
followed by rights/source/coverage admission; outcome analysis is outside this task.
