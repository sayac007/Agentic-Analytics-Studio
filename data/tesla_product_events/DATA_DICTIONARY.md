# Data dictionary

`ledger_version` and each `record_version` version the **curation**, not the publisher's source revision. Source response SHA-256 fingerprints retrieved bytes; canonical ledger and derived CSV hashes are separate.

| Field | Meaning |
|---|---|
| `event_id` / `parent_id` | Stable milestone / underlying incident identifiers. Multiple source reports belong on one milestone; distinct announcement/order/delivery/notice/remedy phases may share a parent. |
| `event_type` | Explicit product/availability/price/financing/supply/recall phase; not an estimated shock. |
| `models`, `trim_id` | Model family and optional stable offering ID. Raw trim labels/aliases remain provisional; no complete historical trim census claimed. |
| `geography` | Explicit DE evidence, manufacturer DE service guidance, unknown scope or foreign scope. German language alone does not establish affected German population. |
| `date`, `end_date` | Value + day/month/year/unknown precision + role. Unknown is null; no month-first-day padding. Internal uncertainty bounds only reject impossible interval order and are never exported as invented event days. |
| `date_basis` | Source-specific temporal justification, including explicit relative weekday resolution where used. Publication date is not automatically an event date. |
| `status` | verified narrow factual phase, partial, unverified or excluded. Verified is source-reviewed, not a guarantee of independent multi-publisher corroboration. |
| `conflicts`, `missing_fields`, `rationale` | What is not established or disagrees; never silently reconciled to fit an outcome. |
| `price` | Quoted currency EUR, list-price-per-vehicle unit, explicit VAT basis (possibly unknown), before/after/change. No computed before price, subsidy normalization or continuous series here. Unknown VAT keeps the candidate partial. |
| `financing_terms` | Separate text evidence for rate, eligibility and deadlines. An observed offer date is not its start; nominal/APR/tenor gaps remain explicit. |
| `recall` | KBA reference, affected DE count and severity nullable unless sourced; manufacture/defect descriptions, remedy category and independently evidenced delivery constraint. Recall is not itself a supply shock. |
| `provenance_category` | Factual ledger records are `observed_event`; hypotheses cannot become verified milestones. Output summary/indicators are `derived_indicator`, potential explanatory proxies, not measured media. |
| `sources` | Primary/secondary, publisher, access date, distinct publication precision, URL, short actual snippet, byte hash and reuse caveat. Archive URL/capture is not source publication time. |
| `availability_observations` | Isolated points, bounded scope, explicit incomplete census/no continuity. They cannot generate a monthly MAI. |

## Monthly CSV semantics

For each event type, `*_parents` counts distinct **verified documented parent incidents** whose eligible phase date lies in that month. Day dates are assigned to their containing month; month dates retain their month and appear in `month_precision_event_ids`. Year/unknown dates do not produce a positive month. Partial, unverified, excluded and planned phases do not produce positive indicators.

Different phases remain separate columns. Same-parent same-type observations within a month do not inflate the count; duplicate same milestones fail validation. No total event/"shock" index combines recall notice and remedy. A remedy may precede a formal notice if explicitly evidenced; no artificial cross-phase ordering is imposed.

`supporting_event_ids` traces each positive row. `manufacturer_guidance_event_ids` flags limited manufacturer-DE-guidance claims separately from explicit German milestones. `coverage=nonexhaustive_event_evidence` applies even in positive months: counts are curated lower bounds, not the national total. Empty cells are unknown, not 0. No source establishes inactivity.

`model_availability_index` is always null in this release. `availability_coverage=insufficient_monthly_configurator_census`. A future positive MAI path needs separate evidence/method review; no flag can turn these sparse observations into continuous availability or volume-weighted TDP.
