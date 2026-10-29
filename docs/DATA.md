# Data — identities, provenance and permitted use

This is the active reading guide. Source catalogs, frozen admission decisions
and immutable hashes remain authoritative; this guide expands no rights.
Publicly viewable does not mean openly licensed.

## Required record for every variable

Record name, `observed` / `proxy` / `synthetic` class, original publisher,
primary URL, access date/time and actual precision, geography, frequency,
unit, definition, source version/revisions, hash, transformations, known gaps
and permitted private/public distribution. Failed requests get error records,
not invented source hashes or successful access timestamps. Missingness stays
missing; no silent interpolation, zero substitution, time compression or
unlabelled carry-forward.

Registrations are observed administrative registrations, not manufacturer
sales or demand decisions. Advertised prices, search attention and reported
campaign timing are proxies, not measured transactions or media spend.
Synthetic benchmark columns stay explicitly separate from observed targets.

## Current public Stage 1

Kraftfahrt-Bundesamt FZ10 monthly BEV/Pkw totals and Tesla/VW counts, January
2021–September 2026, 69 complete months. The official market is not the sum of
individually reported brands. Rest = official BEV minus Tesla minus VW.
VW is the brand, not the group. Nothing in this analysis uses confidential
corporate data. [Source catalog](../data/competition/kba_sources.json),
[checks](../data/competition/kba_checks.json),
[bound audit](../data/task04_regimes/data_audit.json).

Attribution: Kraftfahrt-Bundesamt, Flensburg, FZ10, own calculation,
Datenlizenz Deutschland – Namensnennung – Version 2.0. Preserve source and
modification notices. The current-vintage extraction does not establish
historical publication/revision availability. Month/year reference dates are
not automatically day-precise release dates.

The C17 China basket is unresolved in 66 of 69 months; lower/upper totals do not
identify missing brands. No full China point series is invented. The
[competition data guide](../data/competition/README.md) documents annual/model
registrations, source hashes and 23/80 annual top-ten model-years with exact
prices. Advertised entry/top variants, WLTP ranges, VAT, battery and incentive
treatment require consistent matching; no complete monthly price index exists.
A first separate KBA row is not a model launch.

Calendar controls are deterministic national Fourier/quarter-end/weekday
features, not the internal WKR calendar. [Policy chronology](../data/task04_regimes/policy_chronology.json)
records BAFA/BMUKN primary evidence for 2023/2024/2026; exact older announcement
timestamps remain unknown. BAFA's source notice includes CC BY-ND 3.0 DE:
primary texts stay private, only source metadata and concise factual synthesis
are published. Effective eligibility, announcement and portal dates differ.

## Acquired macro/energy observations — separate private package

The following figures describe the existing **2018-01–2025-12** acquisition
audit, 96 expected months; they do not certify 2026 coverage or a new modeling
permit. Public metadata: [verified-source manifest](../data/verified_sources/manifest.json).
Raw responses and normalized observations remain private.

| Series | Exact source identity and unit | Available | Admission / distribution limit |
|---|---|---:|---|
| Consumer credit DE | ECB `MIR.M.DE.B.A2B.A.R.A.2250.EUR.N`; monthly new-business consumer lending, AAR/NDER, percent/year, total fixation | 96/96 | ESCB policy, native metadata and third-party exceptions; R is not APRC C; no new model permit |
| National CPI DE | Destatis `61111-0002`, `PREIS1$QMU`, Germany national CPI 2020=100, not HICP | 96/96 | Source-specific GENESIS dl-de/by-2-0 credit; no substitution with change rates or unlabelled rebasing |
| Diesel DE | EC Weekly Oil Bulletin, German automotive gas oil, with taxes; EUR/1,000 L divided by 1,000 to EUR/L | 83/96 | Existing qualified private-only decision; embedded attribution, modification and member-state/third-party limits retained |
| EUR/USD | ECB `EXR.M.USD.EUR.SP00.A`, USD per EUR, monthly average | 96/96 | Existing private retrospective acceptance only; no newly approved public raw/derived redistribution |
| Brent | EIA `RBRTE`; underlying Refinitiv/LSEG data | 0/96 admitted | `not_verified` source-specific third-party rights; no unconditional permit or numeric API acquisition |

E10 and EURIBOR are excluded. Euro-super 95 is not E10; diesel is not petrol.
A price per 100 km of WLTP range is not a vehicle's operating cost.
ECB native `UNIT=USD` and `UNIT_MULT=0` identify the FX unit;
`UNIT_INDEX_BASE` does not. Native units/statistics must not be relabelled.

### Diesel missingness and derivation

The original weekly Oil Bulletin hash is
`7e019a27fe2df6f324ec7a7c551b98142713fbee32aa7a030906101ffc22b2fd`.
The workbook's `Prices with taxes!BD` German automotive diesel mapping,
EUR/1,000-litre evidence and the original weekly values stay preserved.
Each Monday price approximates its following seven calendar days, weighted by
monthly overlap. This is a **derived calendar-overlap monthly approximation**,
not an official monthly series. Incomplete months remain null.

All thirteen missing months remain: 2018-04, 2018-12, 2019-01, 2019-04, 2019-12,
2020-01, 2020-04, 2020-12, 2021-01, 2021-04, 2021-12, 2022-01, 2022-04.
The five 2021/2022 gaps affect any later matching analysis and lagged features.
Preserve the project-specific qualified acceptance, original attribution and
modification notices, unresolved third-party/member-state scope, and absence
of a public redistribution approval or legal guarantee.

### Original acquisition evidence and replay

The existing 24 October 2026 record reports successful primary-page/native-data
access for ECB, Commission and EIA policies. This is historical recorded evidence,
not a claim that a subsequent documentation editor accessed those sites.
Earlier failed access and externally reviewed evidence records remain intact.
EIA general reuse does not remove its Refinitiv-specific uncertainty.

Destatis's old copyright URL returned 404; the recorded replacement is
https://www.destatis.de/DE/Service/Impressum/copyright-genesis-online.html.
The previous `/genesisWS/rest/2020` returned HTTP 200 HTML, not observations;
root `/api/rest` attempts returned 404. The recorded working base is
`https://genesis.destatis.de/genesis` with
`/api/rest/tables/61111-0002/{information,structure,data,qualitySigns}`.
JSON-stat selects Germany/national CPI/QMU explicitly; other measures are
percentage changes. Quality sign `e` means final, not estimated.
Source replacement placeholders (including zero with `-`) remain missing.
The December-2024 classification/quality note is metadata, not a fitted control.

Existing acquisition CLI (not required to read the preserved results):

```sh
python -m source_acquisition.fetch_sources --output NEW_PRIVATE_DIRECTORY --acquire-reviewed
```

Use the pinned requirements-attention environment. Primary-policy validation
precedes numeric requests. Changed policy text or diesel bytes needs review;
successful QA does not create a new analytical/publication permit.
Snapshots retain requested/final URLs, actual UTC times, bytes and hashes.
Do not overwrite old uploads, source-specific permits or frozen protocols.

## Other research sources and frozen studies

[Source catalogs](archive/docs/SOURCE_CATALOG.md) and the retained data-folder
READMEs identify campaign, product/recall, Trends and macro packages. A recorded
campaign date is not measured media exposure; no evidence of advertising is
not proof of none. Google Trends requires exact query/topic, DE geography,
search type, categories, normalization window and snapshot vintage. A manually
exported relative 0–100 series is neither spend nor absolute search volume;
private admission does not automatically publish raw/derived observations.
Portal indices can change method (AutoScout24 AGPI, March 2025); differing values
for the same month can reflect measurement vintage, not buyer preference.

The frozen [Task 01G protocol](TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md),
[Task 01I.3 protocol](SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md), its
[hash-bound authorization](../workorders/01i3-scoped-energy-econometrics.md)
and source-specific decisions stay unchanged. No private study results,
raw datasets, permit files, credentials or signed access URLs are exposed by
this cleanup. Historical blocked snapshots are not silently rewritten as
current approvals. HypoForge/WKR/Kinderwelt are independent repositories.

The separate [Task 02 archive](../results/task02/report.md) contains explicitly
synthetic research, including its original truth/evaluation tables. It is not
an observed Tesla dataset. Data-source licenses do not supply a root software
license; no software-license choice is invented here.
