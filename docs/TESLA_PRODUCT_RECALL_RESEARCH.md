# Task 01H — Tesla Germany product, availability and recall research

Research cutoff: **2026-10-24**; event window **2018-01–2025-12**.
Base: current main including merged PR #12 (`7103767`). No open PR or Task 01G.1
execution is a dependency. The local timestamp-acceptance decision is not changed.
No KBA/Trends table, private value, outcome correlation or fitted relationship was
used to select dates/events. Incidental market figures in automotive articles were
not extracted as outcomes. No new empirical model or recovery experiment is run.

## Selection and result

The fixed initial pass prioritized initial German Model 3/Y entry, Berlin customer
handovers, Highland/Juniper transitions, January 2023 pricing, one financing/supply
example, and recalls illustrating physical versus OTA remedies. It is **not an
exhaustive history**. Missing 2018/2020 milestones do not mean those years had none.

The ledger has **17 versioned milestone records**, **11 parents**, **16 substantive
sources**: **10 verified narrow phases, 6 partial, 1 excluded**. Nine verified phases
have explicit German event evidence; one is German manufacturer support guidance on
a dated remedy, not a German affected-VIN or national rollout census.

| Type | Verified | Partial | Excluded |
|---|---:|---:|---:|
| announcement | 1 | 0 | 1 |
| orders_open | 2 | 0 | 0 |
| first_delivery_de | 4 | 0 | 0 |
| model_refresh | 2 | 0 | 0 |
| price_change | 0 | 1 | 0 |
| financing_offer | 0 | 1 | 0 |
| supply_disruption | 0 | 1 | 0 |
| recall_notice | 0 | 2 | 0 |
| recall_remedy | 1 | 1 | 0 |

No variant_added/removed record was sufficiently established in this pass. Those
schema types are supported; no zero market activity is inferred. Verified dated
claims map to **7 months**; **89 months** have no verified dated claim in this ledger,
not proven inactivity. All 96 months have nonexhaustive event coverage; all 96 MAI
cells remain null. No confirmed inactive month or continuous price/exposure series.

## Source inventory and temporal decisions

All citations, actual short snippets, publishers, access dates, source types and
response hashes are in [evidence.json](../data/tesla_product_events/evidence.json).
The [search log](../data/tesla_product_events/search_log.json) preserves actual GETs,
failed guesses, redirects and blocked requests. Raw articles, images and configuration
payloads remain outside Git. Short native excerpts are evidence, not open-licensing
claims; explanatory content/PR/code is English.

| Milestone / source | Decision |
|---|---|
| [Model 3 first German handovers, 2019-02-15 report](https://teslamag.de/news/tesla-liefert-die-ersten-model-3-in-deutschland-aus-bilder-23374) | Verified **February 2019**, exact first day unknown. Belgian port arrival and publication day are not substituted for German delivery. |
| [German Model Y introduction, 2021-08-20 report](https://teslamag.de/news/massenmodell-kein-kleinwagen-tesla-model-y-start-offiziell-deutschland-40279) | Explicit Thursday press introduction resolves to **2021-08-19**. The same article says immediate take-away/test drives were not available. This is not order opening/delivery. |
| [First German Model Y handovers](https://teslamag.de/news/deutschland-start-tesla-model-y-mehrere-staedten-fruehe-besteller-uebergeben-40371) | Verified **August 2021**. Earliest Friday report is tentative; several Sunday/Monday locations do not prove one unique first day. |
| [German-built Model Y Performance handover](https://teslamag.de/news/delivery-day-tesla-ceo-musk-erste-model-y-deutsche-gigafactory-46884), [follow-up](https://teslamag.de/news/deutschland-erste-reine-elektroauto-fabrik-tesla-delivery-day-46893) | **2022-03-22**, specifically first German-built Performance handovers. Not first ever German Model Y. Two reports share a parent and publisher, not two independent events/publishers. Capacity targets are not realized supply. |
| [Highland announcement and German ordering](https://teslamag.de/news/neues-tesla-model-3-basis-version-1000-euro-mehr-678-km-reichweite-60773) | Explicit Friday-morning/immediately-orderable wording supports **2023-09-01**, distinct refresh/order phases. Planned late-October European deliveries are not actual first German deliveries. |
| [Archived official German configurator](https://web.archive.org/web/20230901090712id_/https://www.tesla.com/de_DE/model3/design) | Actual archived body read, not merely CDX listing. Embedded `Lexicon.m3` reports market DE, effective time 2023-09-01T00:50:00Z, two trim keys. Corroborates a point catalog change, not successful checkout/all-month availability. |
| [Juniper German offer](https://teslamag.de/news/tesla-europa-verkauf-neues-model-y-launch-edition-hoher-preis-64681) | **2025-01-24**, separate refresh and immediate-order phases. Prior Asian unveiling is not a DE opening; March deliveries were initially guidance. Launch Series extras make a naive price delta incomparable. |
| [Juniper handover report](https://teslamag.de/news/10-25-tesla-model-y-kunden-trump-effekt-dritte-megafactory-akku-analyse-64859) | Sunday March 9 explicitly reports Friday first refreshed handovers, including German factory-site customers: **2025-03-07**. Market/stock commentary is not used as an outcome. |
| [January 2023 German price reductions](https://teslamag.de/news/tesla-preise-model-y-9100-euro-billiger-model-3-6000-euro-55941) | Explicit **2023-01-13** German configurator change, but **partial**: VAT basis/original snapshot/direct before-price quote absent. Quoted after-price/reduction retained; before price not fabricated by subtraction. No verified comparable-price monthly indicator yet. |
| [December 2023 financing](https://teslamag.de/news/umweltbonus-endspurt-tesla-model-3-highland-rabatt-model-y-zinsen-62978) | **Partial observed offer on 2023-12-11**, not its start. Rate basis/tenor/downpayment and original terms incomplete. Eligibility/deadlines remain text; financing is not list price or a government policy source. |
| [Planned German production interruption](https://teslamag.de/news/tesla-woche-2-2024-pause-gruenheide-highland-usa-hertz-preise-sinken-63297) | **Partial late-January 2024 plan**, not an observed realized start/end/lost-capacity figure. No fabricated day or supply exposure. |
| [Official eMMC FAQ](https://www.tesla.com/de_de/support/8gb-emmc-recall-frequently-asked-questions), [German-context conflict report](https://teslamag.de/news/rueckruf-alte-tesla-mcus-china-verwirrung-bei-deutschen-kunden-33867) | Notice and mixed software/hardware remedy are separate **partial undated German phases**. US/China dates and global software uptake do not establish DE dates/counts. |
| [Official hood-warning guidance](https://www.tesla.com/de_de/support/recall-unintended-front-hood-opening) | Notice date unknown/partial. Body explicitly documents OTA remedy from **2024-06-18**, not the notice date or German recall-news date. No workshop required; German affected-VIN rollout not independently verified. |
| [Global new Model 3 Performance announcement](https://www.tesla.com/blog/introducing-new-model-3-performance) | Dated **2024-04-23**, but excluded from German timing. English global manufacturer copy does not establish a DE announcement/order/delivery date. |

There are **4 primary** sources (two German Tesla recall pages, one global announcement,
one archived official configurator) and **12 secondary** articles, all from Teslamag.
A two-article same-publisher follow-up is not independent corroboration. This public
text-access bias is explicit; no licensed monitoring coverage or completeness claim.

### Negative evidence, conflicts and access limits

- Several guessed Tesla/KBA/electrive paths returned 404. Publisher searches sometimes
  redirected to a homepage or returned irrelevant/current stories. These responses
  are discovery failures, not evidence of no event.
- The KBA recall database CONNECT request was denied by the environment. No actual
  regulator recall entry/reference/German vehicle count was inspected. Guessed KBA
  information paths were 404; no access restriction was bypassed.
- The February 2021 report describes some German eMMC emails but others absent, and
  no KBA listing **at that time**. This is not timeless proof of no recall. The
  primary FAQ discusses software plus hardware, parts contact and old vehicles,
  not an exactly dated German repair program or current capacity constraint.
- The eMMC FAQ has inconsistent replacement-memory unit wording. No replacement
  capacity is encoded as a verified quantity. Manufacture-before-March-2018 scope
  is not a defect-occurrence interval or exposure of newly registered cars.
- Hood-page metadata and visible body disagree on earliest affected Model 3/S/X
  model years. The conflict remains; no severity grade, count or KBA code invented.
- Current 2026 retrieval of an undated support page does not establish historical
  public awareness or exact-vintage availability in 2024. An explicit remedy may
  predate formal notice; forcing notice-before-remedy would corrupt the record.

## Model Availability Index feasibility

A provisional stable family/trim taxonomy is retained with aliases and versioned
records. It is **not a complete historical all-Tesla offering universe**, especially
legacy S/X and changing trim/battery names. Broad aliases require version review;
product redesign/launch editions and old stock may coexist.

One official historical German configurator body and two dated configurator reports
are point evidence only. The Archive query was narrowly bounded to September 1–2,
2023 with at most three results; only one actual body was fetched. Its embedded JSON
was read without executing archived scripts or calling current APIs. Other internal
configuration definitions are not automatically active/orderable offerings. The
German Model 3 catalog has narrower scope than the entire German Tesla catalog.

No source proves the full eligible offer set or absence of a trim for every month,
let alone uninterrupted orderability. A primary point snapshot does not prove checkout
success, delivery lead time, stock, production capacity or continuous availability.
Therefore **no numeric monthly MAI is produced**. All 96 values are null with an
explicit insufficient-census flag; no forward filling, volume weights or TDP analogue.

A future breadth-of-orderable-offer proxy needs a frozen complete taxonomy, original
DE evidence for each orderable offering, a declared monthly measurement rule and
adequate coverage to distinguish absence from unobserved states. It would still be
unweighted offering breadth, not weighted distribution, physical inventory or supply
capacity. Another reviewed task must implement/admit such a measurement if supported.

## Reproducible indicators and limits

[Data dictionary](../data/tesla_product_events/DATA_DICTIONARY.md) specifies phase
roles and mappings. `python3 -m product_events.transform [--check]` validates the compact
schema plus date/scope/parent/price/recall invariants, then regenerates 96 CSV rows and
a hashed summary offline. It never reads KBA or private Trends inputs.

Only verified day/month phases generate positive **distinct-parent lower-bound counts**.
Month-only evidence keeps precision IDs; year/unknown/partial/planned/excluded entries
never generate invented monthly exposure. Missing means unknown, never proven zero.
Manufacturer DE service guidance is visibly flagged in its own supporting-ID column.
No overall event index double-counts notice/remedy or announcement/order milestones.
Regeneration is deterministic; schema/tests and CI never fetch live sources.

## Later research protocol — proposal only

This ledger does not amend frozen Task 01G retrospectively. A separately reviewed
extension must first admit event definitions, source vintages, rights and temporal
coverage. Product launch publicity may affect searches immediately; order opening can
precede deliveries/registration by weeks or months; customer handover and registration
need not occur on the same day. Notice date may drive attention independently of
remedy availability. Recalls of older vehicles do not inherently reduce new deliveries.

A possible sparse specification would predeclare one chosen phase per Model 3 entry,
Model Y entry, Highland and Juniper transition, with separate documented recall-news
sensitivity only after German notice dates are verified. Do not pool all phases or
select dates/lags after looking at favorable correlations. Freeze a small lag family
(e.g. contemporaneous and 1–3 months for ordering, a separately justified delivery
lag), multiple-comparison rules, date-uncertainty alternatives and missing-event policy.
No parameters, outcome relationship or statistical significance are estimated here.

Launches, financing, discounts and recall communications can respond to demand,
production conditions or publicity: reverse causality/endogeneity remain central.
Subsidies, supply constraints, model mix, quarterly delivery seasonality, general BEV
trends and nonautomotive attention confound apparent patterns. Government policy
controls need primary dated sources; a retailer's bonus promotion is insufficient.
Calendar baselines, pretrends/placebos, alternative windows and a fixed holdout would
need prospective review, not residual-driven controls or a favorable event subset.

2022 and 2026 energy-price questions are **future research only**, requiring verified
energy/policy series and identification. The admitted KBA panel ends in 2025; no 2026
registrations or energy/war attribution is claimed. Event-study association, forecast
improvement and causal identification are different objectives. Retrospective event
curation does not create historical as-of availability or causal advertising ROI.
No event columns are inserted into the existing MMM estimator interface.

## Validation

Local and exact-head remote results are recorded in the workorder/Draft PR after
completion. No KBA observations, private Trends data, admission decisions, existing
MMM engine/results, frozen Task 01G methods or other repositories are modified.

### Executed local checks — 2026-10-24

Python 3.12.14 and the existing pinned runtime:

- Full suite: **210 tests passed**, including **14 new product-event tests**, 37.921 seconds.
- Targeted new suite: 14 passed. Covers required source provenance, impossible/mixed-precision intervals, Germany scope, parent deduplication, price currency/VAT/finite arithmetic, financing separation, notice versus remedy, month precision, unknown versus zero, sparse snapshots and deterministic regeneration without KBA/Trends writes.
- `python3 -m product_events.transform --check`: exact CSV/summary regeneration and hash binding passed.
- Both existing example validators and KBA normalized-data audit: passed.
- Ruff on new Python files, whitespace and protected-artifact diffs passed. One initial unused test import was removed.

Remote CI results are recorded in the Draft PR only after the exact head's runs finish.
No live research in CI and no new runtime dependencies.
