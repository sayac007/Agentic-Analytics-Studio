# Task 01I — German fuel, Brent and EUR/USD acquisition

## Actual result: blocked, not empirically complete

2026-10-24 UTC; independent branch from `main` `dfcb42e` including merged PR #14.
All five user handoff files were read, including the candidate Python fetcher.
Their endpoint and licence interpretations are **candidates**, not verified evidence.
No real primary numeric observation was retrieved. No raw/derived real values are
committed, no model or outcome association ran, and existing KBA/Trends/MMM/contracts,
Macro coverage and frozen Task 01G remain unchanged.

| Target | Primary candidate / definition | Observed / missing-or-unverified months 2018–2025 | 2018–2026-09 | Admission |
|---|---|---|---|---|
| Germany diesel | EC Weekly Oil Bulletin; automotive gas oil, with taxes, intended EUR/1,000 litres, native Monday weekly observations | 0 / 96 | 0 / 105 | Blocked; actual workbook layout/units/dates/tax column and rights unverified |
| Brent USD | EIA petroleum spot API v2, `RBRTE`; intended monthly and daily USD/barrel | 0 / 96 | 0 / 105 | Blocked; no EIA key present; route/facet/monthly definition not independently verified |
| EUR/USD | ECB `EXR.M.USD.EUR.SP00.A` and daily counterpart; **USD per EUR** | 0 / 96 | 0 / 105 | Blocked; returned metadata/coverage and rights unverified |
| Germany E10 | ADAC / MTS-K / Tankerkönig research candidates | 0 / 96 | 0 / 105 | No verified national historical series; excluded |

These are **retrieved-and-verified** coverage counts, not proof of absent publisher
history. As of October 24 the latest completed month is September 2026. October is
partial and excluded; no nonexistent future observations are created. The frozen
2018–2025 comparison remains separate. Machine artifacts: [`sources.json`](../../../data/fuel_oil/sources.json),
[`coverage.json`](../../../data/fuel_oil/coverage.json), [`access_log.json`](../../../data/fuel_oil/access_log.json).
Coverage binds exact catalog bytes. No empty pseudo-observation CSV is produced.

## Access evidence and authoritative verification still needed

One minimal lawful attempt per endpoint, logged with exact redacted URL, UTC request
time, HTTP status/exception, content type, response bytes and numeric-verification flag:

- [EC Weekly Oil Bulletin landing page](https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en)
  and the handoff's candidate history XLSX UUID: both proxy **CONNECT 403**. The
  current official history link could not be inspected. Do not describe the UUID
  or native column mapping as verified.
- [EIA test endpoint](https://api.eia.gov/v2/petroleum/pri/spt/data/?frequency=monthly&data%5B0%5D=value&facets%5Bseries%5D%5B%5D=RBRTE&start=2018-01&end=2018-01&length=1):
  one monthly-row request, no key because `EIA_API_KEY` was absent; proxy CONNECT
  403 before any provider response. No claim about authenticated API behavior.
- [ECB one-month CSV request](https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?startPeriod=2018-01&endPeriod=2018-01&format=csvdata):
  proxy CONNECT 403. Neither an HTML page nor HTTP success alone counts as data.
- Primary EC/EIA/ECB legal notices and MTS-K, Tankerkönig and ADAC pages: same proxy
  failure. Ten attempts total; none returned provider headers/body or observations.
  Status/content type are null and bytes zero where no provider response exists.

The environment proxy rejected the tunnel; these are not provider HTTP 403 results,
API outages or evidence of paywalls. No 429 retries, alternate control bypasses or
secondary-value substitutions. User handoff failure logs are not our execution log.
No secondary licence, footer quotation or government-domain assumption is promoted
to reviewed dataset rights.

## Small fetcher: changes to the handoff

[`fuel_oil/fetch_fuel_oil.py`](../../../fuel_oil/fetch_fuel_oil.py) is a reviewed replacement
of the attached `fetch_fuel_oil.py`; its original hash is recorded in the catalog.
No general ingestion framework or new dependency is added. Use Python 3.12 and the
existing `requirements-attention.lock` (includes pinned openpyxl).

- Explicit source/frequency selection; no requests at import time and no global key.
  Key comes only from `EIA_API_KEY`, never command arguments or checked-in URLs.
- Redact keys in URL queries, exception text and CLI failures; refuse raw responses
  echoing a known secret. Do not persist error bodies, headers or auth credentials.
- HTTPS, no credential-bearing URL authority, no automatic redirects; 30 s timeout,
  20 MiB response cap; at most one retry for HTTP 500/502/503/504 with 0.25 s delay.
  No automatic retry for 401, 403, 429, DNS/proxy failures or schema failures.
- Strict content type and parseability checks. FX validates exact pair/direction,
  series/frequency/unit/multiplier/status and positive finite observations. EIA
  validates JSON response, frequency, `RBRTE`, USD/barrel and finite values.
- EIA requests `offset` and `length`, checks all totals/offsets, rejects duplicates,
  incomplete pages and changing totals. A 100-page safety limit **fails**, never
  truncates silently. Tests include **5,001** observations across the 5,000 boundary.
  A stable total does not prove the provider held every value fixed during paging;
  preserve pages and flag revision risk, rather than claim a transactional snapshot.
- Immutable raw files use exclusive creation and SHA-256 sidecars with requested
  endpoint/parameters, UTC retrieval completion, status/content type, byte count,
  unknown publisher revision, rights status and `historical_as_of=not_established`.
  Retrieval and raw hash do not establish historical point-in-time availability.
- A valid EC XLSX container is **quarantined**, not counted as numeric observations:
  no genuine workbook was available to verify sheet/header/country/tax mappings.
  The source-specific native WOB extractor remains blocked. No fake native parser
  or claim that the synthetic handoff matches the workbook is made.
- Failed paging/parsing creates no successful result; already validated raw pages
  remain private and inspectable. A saved private snapshot status is **not** data
  admission. Public catalog coverage is not auto-promoted by a local download.

Offline reproduction (no live requests):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-attention.lock
.venv/bin/python -m fuel_oil.fetch_fuel_oil --check
.venv/bin/python -m unittest discover -s tests -p test_fuel_oil.py -v
```

For a later permitted access environment, use a **new private directory outside Git**:

```sh
.venv/bin/python -m fuel_oil.fetch_fuel_oil --source fx --frequency monthly --output /PRIVATE/new-fx
.venv/bin/python -m fuel_oil.fetch_fuel_oil --source eia --frequency daily --output /PRIVATE/new-brent
.venv/bin/python -m fuel_oil.fetch_fuel_oil --source wob --output /PRIVATE/new-wob
```

Set the EIA key through your secret manager/environment; do not paste it in the
shell command, issue, log or manifest. Commands refuse existing output directories.
Future/current-month source rows may remain in private native snapshots, with
monthly coverage explicitly flagging partial/future months. No partial month is
admitted as a completed monthly comparison. No live API dependencies in CI.

## Manual export / private handoff when API access is blocked

1. **EC:** open the official landing page in a permitted browser; follow its *current*
   historical prices download. Save unchanged XLSX, exact download URL and actual
   UTC download instant; save any actual revision label and dataset/rights notices.
   Inspect sheet and header cells for **Germany, automotive gas oil, with taxes,
   EUR/1,000 litres**, and actual measurement dates. Record cell mapping and notes
   on revisions, tax changes, methods and date conventions. Do not assume filename
   or handoff prose proves them. Retain the original SHA-256.
2. For a reviewed manual extract only, create a separate CSV with the exact header
   `measurement_date,country,grade,taxes,unit,value`. Require `DE`,
   `automotive_gas_oil`, `with_taxes`, `EUR_per_1000_litres`, ISO Monday dates and
   finite positive values. Preserve a mapping record (original raw hash, sheet,
   columns/cells, method, reviewer and handoff hash). `parse_diesel_handoff` tests
   this shape; it does **not** verify correspondence with a missing native workbook.
   Real admission is blocked until that source-to-handoff mapping is reviewed.
3. **Brent:** use EIA's official route/metadata to confirm facet and monthly definition.
   Request native monthly and daily separately with a real lawful key. Retain every
   raw page, offsets, total and full returned metadata. Alternatively use an official
   export with documented series/frequency/units and a newly reviewed adapter; do
   not turn an arbitrary secondary export into an EIA API result.
4. **FX:** use the official EXR endpoint or export with exact daily/monthly keys;
   verify `USD per EUR`, multiplier zero, returned metadata and monthly collection
   convention. Preserve raw bytes rather than manually swapping pair labels.
5. Bind each file to actual UTC retrieval evidence, raw hash, official endpoint,
   vintage description and separately reviewed rights. `check_snapshot` fails on
   missing/mismatched hashes, retrieval precision, vintage or fixture/real boundary.
   Rights attestations are reviewed human records, not automated legal verification.
   `rights_gate` requires private permission; `redistribution_gate` separately checks
   raw or derived permission. Current sources have **none** of these approvals.
6. Keep files/normalized values private until those gates and source-specific mapping
   are resolved. Never borrow the earlier macro uploads' provenance for these files.
   Then produce measured coverage under a separately reviewed real snapshot; this
   task's blocked report cannot itself authorize empirical use.

## Measurement and derivation conventions, fixed before outcomes

Native weekly, daily and monthly records remain separate. The helper functions are
exercised only with explicitly **synthetic** test observations.

- Diesel conversion: original `EUR/1,000 litres / 1000 = EUR/litre`.
  Conditional on confirming Monday measurements, allocate each observed price to
  a seven-day Monday–Sunday interval **as a modeling approximation**, then weight by
  overlap calendar days. This does **not** assert seven measured daily prices.
  Require every day of a completed month covered, including prior-month boundary
  weeks. Missing weeks remain uncovered; no extension of an old week, interpolation
  or default zero. Incomplete/partial monthly values are null. A future native-file
  convention conflict blocks this rule pending review, rather than silently changing it.
- Brent USD: prefer verified official monthly values. Monthly definition remains
  unresolved; do not claim an EIA trading-day-mean formula from secondary prose.
  This task implements no unverified daily-to-monthly USD aggregation as a substitute.
- Derived EUR Brent: align actual daily Brent and USD-per-EUR FX by exact date,
  divide **before** averaging. Never divide two monthly averages and label it the
  mean daily EUR price. The handoff's >=15 matched-day rule is adopted prospectively
  as a **QA floor**, not statistical calibration; additionally require no unmatched
  dates between the supplied series and a completed month. Otherwise null. A day
  missing from **both** sources cannot be detected by matching: source/page/calendar
  completeness must still be independently established. Trading holidays/calendar
  mismatches may therefore leave a month missing; no fill to manufacture coverage.
- E10: EC Euro-super 95 must never be relabelled E10, including periods with unknown
  ethanol composition. MTS-K station notifications are not themselves a national
  average. Tankerkönig's own licence/history/coverage and aggregation would need
  verification; station means without sales weights are derived unweighted proxies.
  No verified ADAC historical API/terms were obtained. E10 remains excluded.

No Tesla oil-shock effect, exogeneity, causal coefficient, lag search or 2026 outcome
analysis is introduced. The earlier [frozen protocol](../../TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md)
and [Macro source report](GERMAN_MACRO_CONTROLS.md) remain unchanged.

## Rights and copy-ready attribution candidates

Actual primary pages attempted: [EC legal notice](https://commission.europa.eu/legal-notice_en),
[EIA copyright/reuse](https://www.eia.gov/about/copyrights_reuse.php),
[ESCB reuse policy](https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html).
All blocked. Public visibility/government hosting and Claude's claimed verified
wording do not establish series-specific permission. See
[attribution candidates](DATA_SOURCES_FUEL_OIL.md); apply only after notice/originator,
private-use and separate raw/derived redistribution review. No numeric republication.

## Open acceptance blockers

Restore permitted official access or supply lawful immutable source exports plus
metadata/rights evidence. Confirm WOB current history URL/native sheet mapping,
measurement convention/taxes/grade/unit; EIA authenticated route/metadata/definition
and complete paging; ECB returned metadata/monthly convention; dataset-specific
rights; and any national E10 history. Then rerun real QA and measure coverage.
**Empirical acceptance is not met:** no actual verified numeric primary observation.
The explicit all-providers-blocked fallback is delivered without claiming completion.

## Executed local verification

Python 3.12.14 with the existing pinned `requirements-attention.lock` environment:

- Full suite: **257 tests passed**, 40.237 s (233 existing + 24 new).
- Targeted fuel/oil tests: **24 passed**, 0.142 s; all synthetic/offline.
- Both contract validator examples, offline KBA audit, unchanged Macro report check
  and new fuel/oil blocked report check passed.
- Ruff unused-import and formatting checks, whitespace and protected-path diff passed.
- Existing synthetic engine tests ran solely as regression verification. No new
  observed-outcome fit or relationship inspection was performed.

Remote Actions evidence is maintained in the Draft PR for its exact head after
observed completion. No local pass is represented as remote CI success.
