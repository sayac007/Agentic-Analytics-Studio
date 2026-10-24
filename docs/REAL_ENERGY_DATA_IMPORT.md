# Task 01I.1 — real uploaded energy files: structural import, not admission

Based on `main` `a99d0d3` after confirming PR #15 merged. Three originals were
explicitly transferred into this execution workspace and inspected **before** numeric
extraction. They are real user-supplied exports, not fixtures and not successful live
API downloads. No raw/derived real observation is published in this PR or CI.
No outcome joins, regressions, correlations or causal/ROI estimates were performed.

## Verified source inventory

| Original | Bytes / SHA-256 | Actual identified layout | Native coverage |
|---|---|---|---|
| `ECB Data Portal_20261024135113.csv` | 10,745 / `26a92c9b9a24414e864a03bd4f7ba7c4a482793845594121e9745c606017355b` | Portal export, 3 columns: `DATE`, `TIME PERIOD`, named EXR series | 333 monthly rows, 1999-01–2026-09 |
| `RBRTEm.xls` | 55,296 / `5881bc058aa7d641dc41ef254f6991e101c952e112284f0eb5a994514b401cb7` | Native OLE/BIFF XLS; `Contents` 15×6, `Data 1` 476×2 | 473 monthly rows, 1987-05–2026-09 |
| `Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx` | 4,491,517 / `7e019a27fe2df6f324ec7a7c551b98142713fbee32aa7a030906101ffc22b2fd` | Genuine XLSX, seven sheets; selected `Prices with taxes` 1117×226 | 1,089 weekly rows, 2005-01-03–2026-10-19 |

Machine catalog: [`real_sources.json`](../data/fuel_oil/real_sources.json).
The public [QA/coverage summary](../data/fuel_oil/real_coverage.json) records all
sheet names/dimensions, source-identifying headers, source locations, hashes,
unknown download times and rights decisions. Filenames are not source identity.
Inputs are bound to filename, bytes and expected SHA-256 before parsing; changed
exports require a reviewed new catalog, never silently replace the snapshot.

### ECB monthly EUR/USD

The header explicitly identifies `EXR.M.USD.EUR.SP00.A` and “US dollar/Euro ECB
reference exchange rate”. Retain **USD per EUR** without inversion. ISO month-end
`DATE` must agree with `TIME PERIOD` (e.g. year + English month abbreviation).
There are no supplied observation-status, revision, multiplier or collection-method
columns. Do not fabricate SDMX `A` flags or infer no revisions. Header verifies the
monthly reference-series identity; a precise monthly averaging/collection definition
still needs primary metadata. This adapter handles the **actual portal shape**,
separately from Task 01I's SDMX-core parser.

### EIA monthly Brent

The file has the native OLE signature and is parsed using already pinned
`xlrd==2.0.2`; it is never renamed to XLSX. `Contents!B3/C7/E7` identify Europe Brent
Spot Price FOB, Dollars per Barrel, Monthly. `Data 1!B2=RBRTE`, row 3 identifies date
and price. Native date-typed Excel cells are converted using the workbook date mode;
footnotes/annual totals, wrong key/units, duplicate months or invalid values fail.
Retain source-native monthly USD/barrel, not a daily reaggregation.

`Contents!F15` contains a workbook timestamp. It is retained as publisher text with
unknown timezone/meaning, **not** a proven publication or download instant. No source
status/revision flags are supplied. No daily Brent-EUR series is generated: dividing
these monthly Brent and FX means would not produce the mean of matched daily ratios.

### EC Germany diesel: independently mapped column and cited official unit convention

Actual selection:

- `Prices with taxes!A1`: consumer prices inclusive of duties and taxes; `A3=Date`.
- `BB` country cells are `DE_` throughout all 1,089 date rows.
- `BD1=DE_price_with_tax_diesel`; `BD2` identifies automotive gas oil/Dieselkraftstoff;
  `BD3=1000 l`. Neighbor `BC` is Euro-super 95 and **is not used**.
- Every actual source date is Monday. All selected cells are numeric; there are no
  duplicated dates. Header/location/country drift fails rather than changing selection.
- Footer notes identify pump prices, describe Member State weighted-average reporting
  and warn about cross-country comparisons. The preliminary-weight note refers to
  EU/EUR aggregates; it does not prove German observations are unrevised.

The selected header/cell format does not itself state currency. The user supplied
[Decision 1999/566/EC, Annex](https://eur-lex.europa.eu/eli/dec/1999/566/oj/eng/pdf),
section “Definition of prices net of duties and taxes in force each Monday”, as the
official Oil Bulletin unit convention (fuel pump prices per 1,000 litres, national
currencies and euros), and specified EUR/1,000 litres for this independently verified
German diesel column. The catalog records this as **user-attested official convention
plus independently verified workbook mapping**. The direct PDF request also failed
with proxy CONNECT 403: the primary text was not independently read here. Do not
claim the decision itself identifies column BD; that mapping comes from the file.

Accept the instructed source unit **EUR per 1,000 litres** for private QA, preserve
original values, and add `EUR/litre = original / 1000`. Without the explicit unit
evidence record the parser still refuses to infer EUR from the filename or country.
Unit evidence never overrides a wrong country/grade/tax/volume mapping.

The existing Monday–Sunday calendar-day overlap approximation now produces a separate
**private quarantined monthly series**, with every missing/partial month null. This
is not a statement that daily prices were measured as constant or an official monthly
mean. Derived-use review remains unresolved, so this is not final analytical or
redistribution admission. E10 remains excluded; no Euro-super/E5/E10 relabelling.

## Computed coverage and QA

| Source | 2018–2025 observed / missing | 2018–2026-09 observed / missing | Admitted months |
|---|---|---|---|
| ECB, source-native monthly | 96 / 0 | 105 / 0 | 0 / 0 |
| EIA, source-native monthly | 96 / 0 | 105 / 0 | 0 / 0 |
| EC diesel, complete temporal overlap only | 83 / 13 | 92 / 13 | 0 / 0 |

All counts were computed from the actual uploaded originals. For diesel “observed”
means enough source dates to calculate the declared monthly approximation,
**not** an official monthly mean or an admitted analytical observation. Missing intervals
are real gaps under that rule, not imputed holidays. The 13 incomplete months are
listed in the machine report; none are silently filled or removed.

Both completed windows have zero partial months and zero visible censored/missing
numeric-value months, but **revision counts are unknown (`null`)**, not zero, and
source-status flags are unknown for every month. Missing-week coverage is reported
separately from missing numeric cells. Raw-source duplicate/nonfinite checks passed.

October 2026 has three native diesel observations, explicitly flagged as belonging
to a partial calendar month. ECB and Brent contain no October row. October is not
folded into the 105 completed-month window or extrapolated. All 96/105 months remain
blocked from analytical admission; observed coverage and admission are separate facts.

## Rights and provenance decisions

Five fresh official requests attempted the ECB ESCB reuse policy, EIA copyright,
EC WOB landing page, Commission legal notice and the user-cited EUR-Lex decision. All failed at the environment
proxy with CONNECT 403; exact UTC request instants/errors are recorded in the public
catalog. These are environment errors, not publisher denials or proof of absent terms.

- **ECB/EIA:** primary terms remain unread; private analysis, raw redistribution and
  derived redistribution are `not_verified`. Quarantined structural QA is not an
  assertion of an analytical or publication licence. Review those notices before use.
- **EC:** the actual workbook contains “Reproduction is authorised provided the source
  is acknowledged.” at `Prices with taxes!B1115/B1117`, with Commission/Communities
  attribution and a 2024 notice. This is direct dataset-specific evidence, replacing
  the prior third-party handoff claim. Private handling is supported by that notice;
  raw reuse is conditional on acknowledgement. Derived-use scope is not separately
  established here. In any case the workorder requires real values to remain private,
  and derived-use/admission review still blocks a ready analytical series.
- All actual download URLs/times are **unknown**. User upload, filename timestamp,
  own local ingestion time and workbook timestamp do not establish original download.
  Source-reference URLs are documented as references, not claimed retrieval evidence.
  These are provenance gaps; absent flags/time alone are not invented new hard gates.
- Current raw hashes bind the exact retrospective uploaded vintage. No historical
  as-of availability is established. The 2018–2025 window is not a historical vintage.

Conditional attribution: “Source: European Commission, Weekly Oil Bulletin,
Germany automotive gas oil, prices with taxes; source acknowledged under the
reproduction notice in the uploaded workbook.” Add exact snapshot hash and any
transformation/change notice after derived-use review. Existing
[ECB/EIA attribution candidates](DATA_SOURCES_FUEL_OIL.md) remain conditional.

## Implementation, private outputs and replay

`fuel_oil/import_energy.py` reuses the existing fuel/oil package; no new runtime
library or lock change. Source inventory precedes extraction. Actual files are
hash-bound to the public real catalog; explicitly synthetic fixtures have their own
catalog and `--fixture` scope. Synthetic inputs cannot pass real mode.

Use the existing Python 3.12 pinned environment (`requirements-attention.lock`):

```sh
python -m fuel_oil.import_energy --check-metadata
python -m unittest discover -s tests -p test_energy_import.py -v
python -m fuel_oil.import_energy \
  --ecb '/PRIVATE/ECB Data Portal_20261024135113.csv' \
  --brent /PRIVATE/RBRTEm.xls \
  --diesel /PRIVATE/Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx \
  --rights-log /PRIVATE/rights_requests.json --as-of 2026-10-24 \
  --output /PRIVATE/new-energy-run
```

The rights request log is the `rights_review_requests` list in the public real-source
catalog, saved as a separate JSON file; it documents failures, **not permissions**.
Choose a fresh output directory **outside the repository**; repository/symlink targets
and overwrite are refused. Missing/mutated files, wrong provenance, bad header/layout
or failed numeric validation produce no completed output. Raw copies are immutable.

Private output contains three unchanged raw copies, three
`*.quarantined.json` native series, a separate diesel monthly-approximation quarantine, `summary.json`, a source-to-normalized SHA-256
`inventory.json`, and a separate `local_ingestion.json`. Normalized files contain
source locations, original dates/units/status, exact raw hash, unknown vintage/time
and `NOT_ADMITTED` quarantine status. No ready admitted dataset is generated; the private diesel approximation remains
explicitly quarantined with source/unit evidence and transformation labels. Local ingestion time is labelled solely as own handling.

Actual reprocessing was executed twice: **nine** raw/normalized/summary/inventory
artifacts reproduced byte-for-byte. Own ingestion timestamps are intentionally separate.
Private files are accessible only in the execution workspace through its terminal or
an authorised workspace file-transfer/export facility. A workspace pathname is **not
a downloadable ChatGPT attachment**. Keep export private and subject to rights review;
no raw-value artifact is attached to this public PR or uploaded by CI.

The legacy Task 01I catalog/coverage remain an immutable record of blocked **live**
acquisition. The new real-upload catalog/report describe this later file handoff;
neither rewrites old access evidence nor claims a successful API connection.
KBA, Trends, Macro admission, MMM/Stage A and frozen protocols are unchanged.

## Actually executed checks

Python 3.12.14, existing pinned dependencies:

- Final full suite after unit-evidence integration: **274 passed**, 45.258 s
  (257 existing + 17 source-layout/unit tests).
- Final targeted suite: **17 passed**, 0.164 s, synthetic fixtures only.
- Both contract validators, KBA audit, unchanged old fuel/oil blocked report check,
  new metadata-only check, Ruff import/format and whitespace checks passed.
- Two final real-input runs: **nine** raw/normalized/monthly-QA/summary/inventory
  artifacts byte-identical; own ingestion-clock file separate. Raw files unchanged.
- No KBA/Trends/Macro/MMM/contracts/frozen-protocol changes. No outcome fitting.

Exact-head remote Actions results are maintained in the Draft PR after observed
completion. No real uploaded raw/normalized file is required by CI.
