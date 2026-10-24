# Task 01H-M — German macro controls: source feasibility and offline preparation

Research snapshot: 2026-10-24 UTC. Independent branch from `main` merge `fef646f`
(PR #13). **No real macro observations acquired or admitted.** This is a blocked
acquisition deliverable with a tested adapter, not an empirical dataset or model.
The existing KBA, Trends, product ledger, statistical contracts and frozen Task 01G
protocol are unchanged. No outcome correlations, coefficients or lag selection ran.

## Source, definition and coverage matrix

Identifiers below are **lookup candidates**, not verified executable series keys.
[`sources.json`](../data/german_macro/sources.json) intentionally has `series_id=null`,
`metadata_status=not_verified`, and unverified actual frequency/unit/adjustment for
all nine candidates. Intended definitions are separate from admitted metadata.
Table IDs do not resolve a unique measure, base, adjustment or vintage.

| Candidate | Official lookup / identifier lead | Intended definition and native frequency | Verified coverage / unresolved details |
|---|---|---|---|
| Consumer credit, primary financing proxy | [ECB MIR.M.DE.B.A2B.A.R.A.2250.EUR.N](https://data.ecb.europa.eu/data/datasets/MIR/MIR.M.DE.B.A2B.A.R.A.2250.EUR.N) | Germany, new household/NPISH consumption business, total initial fixation; monthly annualised agreed rate / narrowly defined effective rate (AAR/NDER) | Indirect indexed description supports key/concept; full official metadata and historical span unavailable. AAR/NDER is **not APRC including all charges**, nor Tesla financing/lease APR. Verify volume weighting, instrument exclusions and adjustment. |
| Deposit facility | [FM.D.U2.EUR.4F.KR.DFR.LEV](https://data.ecb.europa.eu/data/datasets/FM/FM.D.U2.EUR.4F.KR.DFR.LEV); [official change table](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html) | Euro-area policy reference applicable to Germany; daily level if that key is confirmed | Key is an unverified lookup hypothesis. Change events, daily values, month-end levels and monthly means are distinct. No event-to-daily carry-forward. |
| 3-month EURIBOR | [FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA](https://data.ecb.europa.eu/data/datasets/FM/FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA) | Monthly market reference in annual percentage-rate units, not consumer borrowing cost | Key/average convention/eligible days not verified. Verify EMMI originator and third-party licensing; ECB hosting alone does not grant reuse. |
| German CPI all-items index | [GENESIS 61111-0002](https://genesis.destatis.de/datenbank/online/statistic/61111/table/61111-0002) | National CPI, monthly, documented common index base, intended unadjusted | Indexed official table title supports Germany/months. Exact selection, base, history, revisions and December 2024 classification footnotes require inspection. Never replace national CPI with HICP. |
| CPI YoY inflation | Same CPI table or explicit derivation from that index | Monthly percent change from **same calendar month one year ago** | No inputs acquired. Full 2018 YoY needs 2017 index observations too. Missing denominator is missing inflation, not zero. |
| Real earnings index | [62361-0001 monthly lead](https://www-genesis.destatis.de/datenbank/online/statistic/62361/table/62361-0001); [62361-0010 quarterly alternative](https://www-genesis.destatis.de/datenbank/online/statistic/62361/table/62361-0010) | Retain actual native frequency/base/adjustment | Official-statistic search result lists a **monthly** table. Do not assert that monthly earnings do not exist. Its span and comparability over 2018–2025 are **not verified**. Quarterly lead mentions 2007–2026; not a checked data span. |
| Nominal earnings index | Same two earnings table leads | Separate nominal measure, not real purchasing power | Same unresolved monthly history; verify 2022 survey redesign, linking, bonuses, population and deflator. Do not splice frequencies. |
| BOP-HH inflation expectations | [Bundesbank inflation expectations](https://www.bundesbank.de/en/bundesbank/research/survey-on-consumer-expectations-bop-hh/inflation-expectations-848334) | Germany, intended mean next-12-month inflation, monthly | Exact series key unknown; `6WBHH01` snippet is not a full key. Indirect leads: 2019 pilots then April 2020 monthly; population aged 16+; weights/trimming/online coverage and gaps not verified. No invented 2018–2019 series. |
| CES Germany inflation expectations | [ECB CES](https://www.ecb.europa.eu/stats/ecb_surveys/consumer_exp_survey/html/index.en.html) | Germany-specific weighted median, next 12 months, monthly | Exact series key, German historic publication, horizon/statistic, rollout/weights/population and breaks not verified. Euro-area results cannot substitute for Germany; mean and 3-year expectations cannot substitute for 12-month median. |

For **every candidate**, checked real monthly coverage is **0/96** (2018–2025) and
**0/60** (2021–2025). These are acquisition/verification counts, **not proof that
publishers lack observations**. Native-frequency availability remains unresolved.
[`coverage.json`](../data/german_macro/coverage.json) is deterministically bound to
the catalog; no monthly zero-value series is fabricated. Optional confidence and
HICP are deferred to avoid expanding an unverified control set.

## What was actually reachable

[`search_log.json`](../data/german_macro/search_log.json) records exact requests,
UTC instants, errors, and SHA-256 of successful research responses. All 22 direct
official requests (including metadata, series pages, rights and GENESIS metadata)
failed with **proxy tunnel CONNECT 403**. This is an environment access restriction,
not an observed authentication requirement, charge, API outage or denial by the
publisher. No observation API download was attempted before metadata/rights review.

DuckDuckGo initially returned useful **indirect** official-page descriptions for MIR,
CPI, earnings, BOP-HH and reuse policies. Later responses became HTTP 202 challenges;
requests were not retried to circumvent these. Google returned an interstitial;
Bing returned irrelevant bodies despite 200 responses. Neither is used as evidence.
Full HTML/search payloads remain in the external research cache, not redistributed.
Search snippets establish leads only, not complete metadata, rights or data coverage.

The earnings lead is important negative evidence against a premature "quarterly
only" conclusion. `not_monthly_available` is appropriate **only after** inspecting
the official monthly table and its span and establishing that a suitable monthly
series is unavailable. Current real status is `not_verified`. If only a suitable
quarterly series can ultimately be verified, retain its quarters and flag the
monthly candidate `not_monthly_available`; never interpolate or repeat quarters.

## Rights, vintage and admission

- [ESCB reuse policy](https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html):
  indexed official description permits free reuse of standard public statistics
  subject to disclaimers, **excluding third-party data without originator permission**.
  Verify full terms, attribution and series-specific origin before admission.
- [Destatis GENESIS copyright](https://www.destatis.de/DE/Service/Impressum/copyright-genesis-online.html):
  indexed description names Datenlizenz Deutschland – Namensnennung 2.0. Full terms,
  exact table scope, attribution and changes still need direct review.
- [Bundesbank copyright](https://www.bundesbank.de/en/service/copyright): direct review
  blocked. Survey aggregates and restricted microdata are different products; do not
  assume a survey scientific-use file is open redistribution data.

All current rights statuses remain `not_verified`. No real values are published.
For any later lawful acquisition, preserve exact raw bytes, SHA-256, source URL,
offset-aware retrieval timestamp, publisher/vintage description and complete reviewed
series metadata. Re-fetches create new snapshots; no automatic latest-vintage choice,
duplicate averaging or silent revision replacement. Different measures are not
independent corroboration of the same statistic. MIR via Bundesbank/ECB may represent
the same underlying data and must be checked, not averaged. No overlap cross-check
was possible without observations.

Retrieval time and hash bind today's snapshot, **not historical availability**.
Publication lags/revisions require per-vintage evidence for an actual as-of backtest;
all outputs explicitly say `historical_as_of=not_established`. Preserve unknown
publication dates rather than invent a first-of-month date. KBA's existing
[admission distinctions](PUBLICATION_PRECISION.md) remain untouched.

## Offline implementation and reproducibility

No new dependencies. Python 3.12; use the existing pinned environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-attention.lock
.venv/bin/python -m macro_controls.pipeline --check
.venv/bin/python -m unittest discover -s tests -p test_macro_controls.py -v
.venv/bin/python -m macro_controls.pipeline --fixture \
  --catalog tests/fixtures/macro/sources.json --series cpi \
  --raw tests/fixtures/macro/cpi.csv \
  --provenance tests/fixtures/macro/cpi.provenance.json \
  --derive cpi-yoy --output /tmp/SYNTHETIC-macro-cpi.json
```

Choose a new output name; existing files are refused. `--rebuild-report` explicitly
regenerates the blocked-coverage artifact; `--check` compares bytes without network.
The CLI never reads KBA/Trends or fits a model. Four conspicuously synthetic fixtures
exercise the **ECB SDMX-CSV core shape** (`KEY,FREQ,REF_AREA,UNIT,TIME_PERIOD,OBS_VALUE,
OBS_STATUS`); extra metadata columns are retained in immutable raw bytes, while
identity/frequency/country/unit/multiplier/adjustment drift fails. This is **not a
verified live parser** for Destatis JSON/CSV or Bundesbank survey exports. Their
source-specific layout adapters remain blocked until actual metadata/sample exports
are reviewed; a reviewed handoff to this core shape is supported without claiming
it has been produced from real sources.

A separately reviewed catalog (`scope=reviewed_observations`) must supply an exact
series key, verified definition/frequency/unit/adjustment, evidence references and
`rights.status=reviewed_reuse`. These are reviewer attestations, not automated legal
verification. `source_url` must then be the reviewed official **download URL**, not
just a table homepage. CLI `--download --raw NEW_RAW --output NEW_RESULT` downloads
only such an entry and writes an exclusive raw file plus hash-bound provenance
sidecar. Redirects require renewed review and are refused. For an existing lawful
snapshot use `--raw` with `--provenance`; manipulated hashes fail. No current real
catalog entry can pass this gate. Failed parsing produces no success result; the
acquired raw snapshot/provenance remains inspectable. Do not commit real snapshots
until series-specific redistribution rights have been reviewed.

Output JSON includes catalog hash, all native observations, native monthly rows and
separate derived monthly rows. Each row carries definition/provider/country/unit/
adjustment, original series ID, period/value, vintage/retrieval/source/raw hash,
transformation, rights, source class and quality. `A/P/E/M` source flags map to
observed/provisional/estimated/missing; unknown flags fail for review. Blank is
missing only with `M`; invalid/nonfinite numbers fail. Duplicates, including revised
values for the same period, fail. Missing months are not inserted, dropped to hide
a gap, interpolated or assigned zero. Consumers must check completeness before use.

Two explicit optional derivations, exercised offline:

1. `--derive daily-mean`: arithmetic **calendar-day** mean in original annual rate
   units, only if every calendar day has an explicit finite observation (including
   leap day). Otherwise monthly value is null with `incomplete_daily_coverage`.
   Change events are never carried forward. A business-day EURIBOR mean needs a
   separately reviewed eligible-day/calendar convention; this function cannot
   silently substitute for it. Entirely absent months remain absent.
2. `--derive cpi-yoy`: `100*(I[t]/I[same month previous year]-1)` with the same positive
   index base, series and immutable vintage; input months and quality flags remain
   visible. Missing calendar pairs yield null, regardless of row positions. This
   is a derived rate, not independent corroboration of published rounded inflation.

## Candidate economic protocol — no estimates

This proposal is fixed before inspecting any outcome relationship. It **does not
amend** the [frozen Task 01G protocol](TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md) or
license running an expanded regression. A new reviewed protocol must first specify
sample, outcomes, information set, controls, transformations and multiplicity.
Machine-readable companion: [`candidate_protocol.json`](../data/german_macro/candidate_protocol.json).

- Primary sparse extension: **one** consumer-credit rate measure in level, lag **3
  months** as the prospective order-to-registration-delay hypothesis. Sensitivities
  at lag **0** and **6**, each a separate prespecified comparison; never include or
  search all seven lags. A three-month lag is an economic hypothesis, not an empirically
  known Tesla order delay. Apply positive lag to the earlier macro month.
- Secondary alternative: replace that rate with CPI **YoY**, same 3-month primary
  lag and 0/6 sensitivities. Do not add it automatically to the financing model.
  Each extension adds one macro variable to a separately approved baseline; no
  unrestricted kitchen-sink model on 96/60 months.
- Policy-rate and EURIBOR alternatives may replace retail credit in separate models,
  never enter jointly by default. They measure different transmission stages and
  may be highly collinear. No average of the three concepts.
- Earnings and expectations are documentation-only candidates until definition,
  native frequency, full comparable sample and rights are verified. No quarterly
  expansion or euro-area substitute. No claim that a shorter CES sample has 96 months.
- Rates are expressed as annual percent levels; their differences are **percentage
  points**, not percent growth. CPI YoY is percent, and its difference is percentage
  points. Nominal CPI/earnings index levels may trend; real earnings growth is a
  separate native-frequency transformation, not nominal growth minus a mismatched
  monthly inflation number. Stationarity/break handling must be specified before
  estimation; no automatic test-driven selection from outcomes.
- Real earnings already use a price deflator. Including CPI alongside real earnings
  risks mechanical overlap and unstable interpretation. Expectations can react to
  current inflation; financing conditions and promotions can respond to weak demand.
  Common shocks (energy, subsidies, supply) and simultaneity make observational
  coefficients associations, not causal financing or marketing effects.
- Contemporaneous monthly releases are generally unavailable at the decision origin.
  Fixed lags do not by themselves prove as-of availability. Revised current-vintage
  data support only retrospective descriptions without vintage-specific evidence.
  Any new specification involving the frozen 2025 holdout requires separate approval;
  this task never reads that holdout or tunes a candidate on it.

## Remaining acceptance blockers

Restore permitted official metadata/download access or supply lawful official
metadata and immutable exports. Resolve exact MIR rate/aggregation; DFR and EURIBOR
keys/calendar/rights; CPI series/base/2017 lookback; monthly earnings span and 2022
linking; DE-specific expectations keys, weights/horizons/populations and gaps. Then
add **actual-format** Destatis/Bundesbank adapters, hash-bound real snapshots and
measured native/monthly coverage. Real-source comparability and full requested data
availability therefore remain **unverified**; no empirical or causal result is claimed.
CI validates only the offline preparation and honest blocked report.

## Executed local checks

Python 3.12.14, existing pinned `requirements-attention.lock` environment:

- Full suite: **233 passed**, 40.014 s (210 existing + 23 macro tests).
- Final targeted suite after formatting: **23 passed**, 0.263 s.
- Both existing contract validator commands and offline `kba audit`: passed.
- Blocked macro report check and synthetic CPI-YoY CLI smoke: passed.
- Ruff unused-import checks, formatting, whitespace and protected-path diff: passed;
  KBA/Trends/product ledger/MMM/contracts/frozen protocol have no changes.
- No live source calls in CI. Existing synthetic engine tests execute solely as
  regression verification; no new model or observed-outcome analysis was run.

Exact-head remote CI conclusions and workflow URLs are recorded in the Draft PR
only after observed completion; local success does not imply Actions success.
