# Verified macro/energy acquisition — package 3

Acquisition and QA only: **no outcome join, correlation or model**. Window for the
coverage report is 2018-01..2025-12 (96 calendar months). The public data manifest is
`data/verified_sources/manifest.json`; raw responses and normalized observations
remain in the private archive, not Git or public CI. This preserves earlier
source-specific public-redistribution and human-admission limitations.

| Series | Verified primary identity/unit | Available / expected | Reuse / admission limits |
|---|---|---:|---|
| Consumer credit DE | ECB MIR.M.DE.B.A2B.A.R.A.2250.EUR.N; monthly new-business consumption loans; AAR/NDER, percent/year; total fixation | 96/96 | ESCB reuse policy personally accessed; credit source, preserve native statistics/metadata, third-party exception. No new modeling permit. **R, not APRC C**. |
| National CPI DE | Destatis 61111-0002; PREIS1$QMU, 2020=100; national CPI, not HICP | 96/96 | Personally accessed GENESIS-specific dl-de/by-2-0 notice; source credit required. No index rebasing or substitution with change rates. |
| Diesel DE | Commission Weekly Oil Bulletin, with taxes, German automotive gas oil; EUR/1000 L → EUR/L | 83/96 | Existing qualified private-only decision preserved; embedded credit/modification notices and member-state/third-party limits remain. Monthly series is **derived overlap approximation**, not official monthly observations. |
| EUR/USD | ECB EXR.M.USD.EUR.SP00.A, USD per EUR, monthly average | 96/96 | Earlier private retrospective acceptance retained; no new public raw/derived redistribution approval. Native UNIT=USD and UNIT_MULT=0 verified; UNIT_INDEX_BASE is not the unit. |
| Brent | EIA RBRTE, underlying source Refinitiv/LSEG | 0/96 admitted to this package | EIA general reuse is not source-specific third-party permission. **not_verified** rights retained; no data request or unconditional permit. Previously uploaded private Brent files remain untouched. |

E10 and EURIBOR are excluded. Euro-super 95 is not substituted for E10. No API key
is printed, committed or passed in a logged URL; Brent remains blocked even if a
key is available, because the rights gate precedes an API call.

## Actual primary retrieval and errors

On 2026-10-24 the ECB reuse policy, exact MIR/EXR portal metadata and native SDMX
CSV, Commission legal notice/Oil Bulletin and EIA policy/spot-source notes were
personally accessed successfully. This is new evidence; earlier proxy failures
and external-human evidence records remain unchanged and historically accurate.

The old Destatis copyright URL returned **404**. The verified current notice is
https://www.destatis.de/DE/Service/Impressum/copyright-genesis-online.html.
The old `/genesisWS/rest/2020` request returned **HTTP 200 HTML**, redirecting to an
announcement, not observations. Root `/api/rest` attempts returned **404**. None
was counted as data or replaced with invented observations. The official current
client/environment identified the base `https://genesis.destatis.de/genesis`:

- `/api/rest/tables/61111-0002/information`
- `/api/rest/tables/61111-0002/structure`
- `/api/rest/tables/61111-0002/data`
- `/api/rest/tables/61111-0002/qualitySigns`

The native JSON-stat dimensions explicitly select Germany / national CPI / QMU;
structure identifies QMU as 2020=100. The other two measures are percentage changes
and are not used. Source quality sign `e` means **final value**, not estimated.
Replacing-value signs (including source placeholder zero with '-') remain missing.
The source's December-2024 classification/quality note is retained in raw metadata;
it is not turned into a post-hoc model control.

The new direct Oil Bulletin download has exactly the previously reviewed SHA-256
`7e019a27fe2df6f324ec7a7c551b98142713fbee32aa7a030906101ffc22b2fd`.
Raw weekly source, BD country/product/tax mapping, official unit evidence and all
13 missing months are retained. Each Monday value approximates its following seven
calendar days, weighted by monthly overlap. Incomplete calendar coverage remains
null; no interpolation, implicit absent-week fill or forward-fill.

Missing diesel months: 2018-04, 2018-12, 2019-01, 2019-04, 2019-12, 2020-01,
2020-04, 2020-12, 2021-01, 2021-04, 2021-12, 2022-01, 2022-04.

## Reproduce without weakening gates

Python 3.12 with requirements-attention.lock:

```sh
python -m source_acquisition.fetch_sources --output NEW_PRIVATE_DIRECTORY --acquire-reviewed
```

HTTPS primary endpoints only. Policy evidence is retrieved/revalidated before
numerical requests; changed/missing policy text stops acquisition for fresh review.
Raw responses are exclusive, unchanged snapshots, each with requested/final URL,
actual UTC request/completion times, bytes and SHA-256. Failed attempts retain a
request timestamp and error, without inventing access timestamps or source hashes.
Normalization checks exact source fields, units, calendar uniqueness and raw hashes;
changed diesel bytes require review. Replaying QA may verify identical outputs but
never overwrite changed observations. Old raw uploads, policy decisions, permits,
Task01G/01I.3 protocols/results and original acquisition catalogs remain unchanged.

No historical real-time availability or complete revision history is established.
The package archives four usable series privately; Brent clearance remains a
concrete blocker. Public raw/derived publication and later modeling are not newly
admitted by a successful data-quality check.
