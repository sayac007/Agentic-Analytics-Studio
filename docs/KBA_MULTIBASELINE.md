# Verified KBA acquisition — Task 01B with Task 01B.1 admission update

Basis: `main` at merge commit `188b5cb` after PR #3 was confirmed MERGED
(2026-10-22 14:24:44 UTC). No unmerged feature branch was used. This task does not
change the synthetic MMM engine, its configuration or results. Task 01B.1 adds only
the backwards-compatible v0.2.1 provenance patch described in PUBLICATION_PRECISION.md.

## Sources and what was actually checked

Datenquelle: **Kraftfahrt-Bundesamt, FZ 10**, monthly German passenger-car new
registrations, Abruf **2026-10-22**; [dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0);
**eigene Berechnung/eigene Darstellung** (table extraction and normalization).
Every dataset URI is in [`sources.json`](../data/kba/sources.json). This attribution
and the catalog accompany the derived CSV; do not redistribute the CSV without them.

Primary discovery: [KBA monthly archive](https://www.kba.de/DE/Statistik/Fahrzeuge/Neuzulassungen/MonatlicheNeuzulassungen/monatl_neuzulassungen_node.html).
Year/month filter pages for January 2018, December 2018, January 2019 and January
2020 established historical filename families. Older files use `_xls.xls` or
`_xlsx.xlsx`; newer files use `.xlsx`. Initial guesses returned 404, some 503/timeouts
were retried; these are request outcomes, not observations. We directly downloaded
and parsed **96 actual workbooks**, January 2018–December 2025. No month was admitted
on archive listings/search results alone. The request/discovery ledger is
[`acquisition-evidence.json`](../data/kba/acquisition-evidence.json); cached request
reuse and retries are distinguished from verification of workbook content.

The normalized release catalog records primary URL, retrieved raw filename/format,
byte count, SHA-256, access date, reporting month, exact sheet, reviewed parser profile,
publication value **and precision**, revision notice, license evidence and exclusions.
[`locations.json`](../data/kba/derived/locations.json) identifies the exact cell for
every observation, including December cumulative cells used for reconciliation.
[`quality.json`](../data/kba/derived/quality.json) binds catalog/plan and normalized CSV
hashes and column lineage; [`inventory.json`](../data/kba/derived/inventory.json) binds
all derived outputs. A raw workbook hash is not the normalized-data hash.

FZ 10 is sufficient for the four candidates within the verified windows below.
Modern FZ 10 explicitly labels `mit Elektroantrieb (BEV)`; legacy files only say
`mit Elektroantrieb`. We **do not assume these labels are definitionally identical**.
BEV before 2021 remains unverified in this acquisition. A longer BEV series would
need KBA glossary/methodological evidence or another primary statistical product with
its own provenance/license checks. No third-party series or unverified FZ 8/FZ 11
figures are substituted. Registrations are not sales, deliveries, orders or spend.

## Coverage and admission

| Candidate | Definition | Verified contiguous window | Months | Retrospective / historical |
|---|---|---|---:|---|
| A Tesla | Exact TESLA brand total; **all powertrains** | 2018-01–2025-12 | 96 | admitted / blocked |
| B BEV market | All-brand passenger-car total, explicit **BEV only** | 2021-01–2025-12 | 60 | admitted / blocked |
| C Toyota | Exact TOYOTA brand total; **all powertrains** | 2018-01–2025-12 | 96 | admitted / blocked |
| D VW | Exact VW brand total; **all powertrains** | 2018-01–2025-12 | 96 | admitted / blocked |

No internal gaps occur in those windows. The 36 earlier months listed as missing for
B are **not verified under the BEV definition**, not observed zeros. No synthetic
extension, interpolation, forward-fill or implicit symbol-to-zero conversion occurs.
4,944 numeric monthly observations across all extracted exact brand-total rows and
the BEV total support the selection audit; these are not 4,944 independent benchmark
replications. Small/single-model brands lacking an explicit `ZUSAMMEN` total are outside
this parser's eligible pool, rather than inferred from model rows.

All four meet the length floor in their longest contiguous windows. The shared
2021–2025 window would provide 48 training/12 holdout months and 42 residual df for
the six-column quarter-end specification (43 without quarter-end), conditional on
full design rank. No fit or actual rank/identification assessment was performed.
The coverage report's longest-window split is an engineering candidate, not an
executed experiment or an instruction to replace the common protocol window.

**Task 01B.1 resolves the retrospective publication-precision conflict:** generator
v0.2.1 explicitly preserves day/month/unknown precision, distinguishes retrieval from
publication and requires a named admission regime. All four references are now
`admitted` for retrospective immutable-reference use. Hash/rights/definition,
continuity, residual-df and competing-vintage gates remain unchanged or stricter.

**Historical Point-in-time remains blocked:** neither a publication day nor the
2026-10-22 download proves that the current source hash existed before a historical
cutoff. The catalog has no reviewed exact-vintage availability witness. The admission
report separately records `historical_point_in_time=blocked`, `as_of=null` and explicit
reasons. Supplying a cutoff alone cannot resolve missing evidence. No date was invented.
See [the normative provenance patch](PUBLICATION_PRECISION.md) for fields and backwards
compatibility; estimator/result schemas, synthetic artifacts and statistics are unchanged.

`admitted`, `insufficient_coverage`, `blocked` are data gates, not validation of recovery
or causal identification. Admission checks residual-df engineering floors, not empirical
power; actual rank/finiteness checks remain mandatory at fit time. Missing release
rights or unresolved conflicting vintages are blocking, even if coverage is long.

## Versions, rights and source irregularities

The KBA [license PDF](https://www.kba.de/DE/Service/Hinweise/Datenlizenz/datenlizenz_pdf.pdf?__blob=publicationFile&v=6)
(SHA-256 `7d2235cbbf83fe3107dcd678e39831abd60f22212c0587ec3989f99aa8cdbabe`)
explicitly covers publicly supplied KBA data/statistics and permits copying,
transformation and redistribution with provider, license link, dataset URI and marking
changes. This supports legacy numeric tables without an embedded license; modern
imprints also name dl-de/by-2-0. Source evidence is retained in the catalog and the
PDF is committed. This data license is not used to assert rights to cover photographs
or all other embedded assets. Accordingly full image-bearing workbooks remain in the
external raw cache; committed XLSX parser fixtures have media/drawings removed, retain
unchanged table cells, and record **original and transformed hashes** separately.
They are explicitly test fixtures and barred from benchmark admission/live fetching.
The image-free legacy XLS snapshot is original. No image license is inferred.

Each reporting month uses one pinned retrieved snapshot; no historical as-of availability
is claimed. URL `v=2` is a transport/version parameter, not a complete revision ledger.
The June 2025 workbook explicitly says initial publication **2025-07-07**, corrected
version **2025-07-21**; both are retained. Earlier versions were not retrieved, so
revision history remains `not_verified`, including that known correction. A different
hash on re-download fails instead of replacing a vintage; duplicate reporting months
with different hashes fail until resolved in a reviewed catalog update.

Reviewed anomalies are explicit in the parser and catalog:

- June/July 2018 use `Marken` instead of `Marke`; sheet aliases vary in legacy files.
- August 2019 omits the FZ10.1 prefix in its otherwise matching B6 title.
- November/December 2020 include the reporting month in B5; November has its own sheet name.
- August 2020 Honda total D117 has a conflicting `H-1 STAREX` model label in C117;
  exclude that Honda observation rather than reinterpret it. This excludes Honda
  from complete-history brand selection and does not affect A–D.
- May 2022 imprint dates are Excel dates **displayed as months**, not evidence of a
  publication on day 1. The parser retains month precision.
- August 2024 headers occupy rows 9/10 rather than 8/9; separate profile required.
- June 2025 revision row shifts frequency/publisher/license imprint positions.
- Symbolic monthly brand totals (`-`, `.`, `/`, `X`) are explicitly excluded and logged;
  symbolic annual cumulative values skip that reconciliation check and are logged.

The annual report compares complete numeric monthly sums with the same series'
December published cumulative total. No value is changed to force reconciliation.
Unknown layouts, noninteger/negative/boolean/nonfinite counts, formula-valued XLSX
extraction cells, missing/duplicate totals or incompatible dates fail closed.
XLS uses cached numeric BIFF cells; raw SHA binding is essential and it is not an
adversarial spreadsheet formula sandbox. Only pinned public sources are supported.

## Brand selection and characterization

[`acquisition-plan.initial.json`](../data/kba/acquisition-plan.initial.json) preserves
the initial plan. Availability-only revision 1.1 chooses common 2021–2025, since the
explicit BEV series begins 2021 and a 2024 holdout would leave only 36 common training
months. This revision precedes all real-baseline recovery. The **original selection
window 2018–2023 and all selection criteria remain unchanged**.

Eligible pool: complete exact all-powertrain brand totals over those 72 months,
mean >=1,000/month, excluding Tesla and aggregate/model rows. C minimizes sample
CV; D maximizes volume among remaining eligible brands; lexical ties. The full
25-brand eligible ranking is retained in `selection.json`. Toyota's selection-window
CV is 0.168148; VW's selection-window mean is 46,203.694/month. Selection used no MMM
outcomes. These are deterministic descriptive choices, not a representative sample.

Computed descriptions use the same **60 months, 2021–2025**, for all four:

| Series | Mean/month | Sample SD | CV | Linear slope count/month |
|---|---:|---:|---:|---:|
| Tesla | 3,838.77 | 3,281.61 | 0.854861 | -39.69 |
| BEV market | 37,941.50 | 14,848.47 | 0.391352 | 281.23 |
| Toyota | 6,808.45 | 1,274.90 | 0.187253 | 37.34 |
| VW | 43,128.37 | 6,854.01 | 0.158921 | 129.37 |

VW being quieter than Toyota in this later window does not trigger reselection.
`characterization.json` also contains calendar-month means, quarter-end versus other
means, median/MAD, robust outliers using abs(0.67448975*(y-median)/MAD)>3.5 and the
largest adjacent 12-month mean shift. Zero MAD is explicitly undefined for that outlier
rule. Trend is the descriptive OLS slope against integer time; annualized slope is
12*slope/mean. These summaries include the prospective benchmark holdout as **data
descriptions only**; they must not be used to add controls or retune a future fit.
Season means are not detrended causal season estimates. Shift scans are explorative,
with no tested breakpoint, causal attribution or multiplicity-adjusted inference.
No subsidy, supply-wave or price-change cause is asserted from these summaries.

## Reproduce and verify

Python 3.12, Git, TLS-verified network for acquisition only:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-kba.lock
.venv/bin/python -m kba fetch --raw-dir artifacts/kba-raw
.venv/bin/python -m kba extract --raw-dir artifacts/kba-raw --output artifacts/kba-derived
.venv/bin/python -m kba verify --raw-dir artifacts/kba-raw --output artifacts/kba-derived
```

`fetch` uses only pinned official URLs, checks exact bytes and refuses hash drift or
cache overwrites. Mutable sources can disappear/change: stop and resolve a new vintage,
never silently refresh the catalog hash. Raw files are unchanged in the cache. Repeat
extraction into a **new** directory; outputs must be byte-identical. No random streams
or engine execution are involved. `verify` re-extracts raw workbooks and compares exact
output bytes and membership, not only stored hash declarations.

Without network, audit the committed derived artifacts and run the parser smoke test:

```sh
.venv/bin/python -m kba audit
.venv/bin/python -m kba extract --catalog tests/fixtures/kba/sources.json --raw-dir tests/fixtures/kba --output artifacts/kba-fixture-smoke
.venv/bin/python -m kba verify --catalog tests/fixtures/kba/sources.json --raw-dir tests/fixtures/kba --output artifacts/kba-fixture-smoke
.venv/bin/python -m unittest discover -s tests -v
```

`audit` recomputes coverage/selection/descriptions/reconciliation and output hashes from
the normalized data and catalog; it **cannot prove original workbook content without
the raw cache**. CI uses the committed table fixtures for raw parser checks and never
requires live downloads. Rebuild those transformed fixtures with
`python -m kba.fixtures --raw-dir artifacts/kba-raw --output NEW_FIXTURE_DIRECTORY`.
The seven selected months exercise layouts/date precision/revision/cumulative columns;
they are not a continuous benchmark. See their separate provenance catalog and README.

Parser dependencies are pinned separately in `requirements-kba.lock` (openpyxl 3.1.5,
xlrd 2.0.2, et_xmlfile 2.0.0), including the unchanged base runtime lock. No dependency
or statistical convention in the MMM engine changed. Profiles `fz10-xls-2018-v1`,
`fz10-xlsx-legacy-v1`, `fz10-xlsx-bev-v1`, `fz10-xlsx-bev-202408-v1` enumerate formats,
exact allowed sheets, reviewed date domains and header rows; all source cells are
bound to raw hashes. Extending beyond these reviewed domains requires profile review.

## Next boundary

None of these references is currently passed to the generator or estimator. A separately
authorized execution task can export each retrospectively admitted series into its
own immutable two-column generator-only reference and v0.2.1 release ledger, with
`admission_regime=retrospective_immutable_reference`. Historical use needs separate
exact-vintage availability evidence and an explicit as-of cutoff.
Do not pass the six-column acquisition table to the estimator. Keep true registrations
and truth private, with the existing isolated estimator receiving only synthetic media
and the semi-synthetic target plus calendar controls. No observed-baseline recovery,
Monte Carlo grid, validated MDE, empirical coverage, real marketing ROI or causality
claim is delivered. The [future recovery protocol](MULTIBASELINE_RECOVERY_PROTOCOL.md)
also identifies absolute-calibration and aggregate-contract review decisions.

## Executed verification (local, 2026-10-22)

Fresh Python 3.12 environment `/tmp/task01b-ci-venv`, installed with
`python -m pip install -r requirements-kba.lock`:

- Both existing `contracts/validate.py` fixture commands passed.
- `python -m unittest discover -s tests -v`: **99 tests passed** (73 existing,
  26 KBA), 32.056 seconds in the recorded local run.
- Full-cache `python -m kba verify --raw-dir /tmp/task01b-raw --output data/kba/derived`
  re-extracted all 96 releases and matched every committed derived byte.
- `python -m kba audit` and offline fixture extraction/re-extraction verification passed.
- Existing `python -m studio run --output /tmp/task01b-synthetic-regression` and
  `python -m studio verify /tmp/task01b-synthetic-regression` passed unchanged.
- **376** complete series/year monthly-to-December-cumulative checks, **zero conflicts**.
  Publication precision across releases: **24 unknown, 58 month, 14 day**.
- `git diff --check` passed. Ruff 0.14.1 formatting and unused-import checks were run
  on new Python files only; Ruff is a development tool, not a runtime dependency.

Initial targeted checks exposed an overly narrow license-download URL allowlist and
incomplete removal of drawing relationships from table fixtures; both were corrected.
Adding cumulative reconciliation required regenerating stale derived outputs. The
final full suite above is green. No MMM settings/results were changed in response.
Remote CI is reported separately in the Draft PR for its exact commit; local results
alone are not evidence of a successful GitHub Actions run.
