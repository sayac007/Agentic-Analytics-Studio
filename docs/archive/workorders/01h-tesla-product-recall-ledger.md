# Codex Workorder — Task 01H: Tesla Product, Availability & Recall Evidence Ledger

Repository: `sayac007/Agentic-Analytics-Studio`

## Objective

Build a source-backed, reproducible event ledger for Tesla Germany covering January 2018–December 2025. Capture product introductions, order-opening dates, first German deliveries, model refreshes, material price/financing changes, availability constraints, and vehicle recalls. The goal is to support future, *separately authorized* time-series research on Tesla registrations and Google Trends search interest. **Do not fit models, inspect outcome correlations, or claim causal effects in this task.**

## 0. Start conditions and scope

1. Inspect current `main`, open PRs and `AGENTS.md`. Confirm the status of Task 01G.1/PR #12. Do not build on an unmerged feature branch; if a dependency is truly required, stop and explain it. Otherwise work independently from `main`.
2. Read the existing Tesla campaign ledger, KBA provenance/admission documentation, Google Trends data restrictions, statistical contracts and frozen Task 01G protocol.
3. Create branch `research/task-01h-tesla-product-recall-ledger`; create a **Draft PR**; do not merge.
4. Do not alter KBA observations, private Trends values, existing MMM engine/results, estimator isolation, CI signing/credentials, or other repositories.
5. Keep all repository content, code, documentation and PR descriptions in English.

## 1. Research question and source hierarchy

Which independently documented product, availability, price and recall events might plausibly coincide with, precede or follow Tesla registrations and public attention in Germany?

Prefer original sources: Tesla Germany announcements/configurator snapshots, archived official pages, German regulator KBA recall notices and official Tesla recall documents. Use reputable automotive reporting to corroborate dates, pricing and Germany-specific delivery timing. Archive *metadata and URLs*, not entire copyrighted articles. Do not treat publication date as event date without explicit evidence. Search for negative evidence and conflicting sources as well as confirming sources. Maintain a dated search log, including failed or blocked requests.

A source about the US, China or global Tesla operations does not establish an event in Germany. English-language Tesla announcements are not automatically German launch dates. If source access is blocked, retain the gap and do not fabricate a record.

## 2. Event types and temporal semantics

Use explicit event types:

- `announcement`: public announcement or unveiling; not automatically orderable.
- `orders_open`: verified ability to place a German order.
- `first_delivery_de`: verified first German customer delivery or registration period.
- `model_refresh`: documented facelift, trim or substantive product update; distinguish announcement/order/delivery milestones when available.
- `variant_added` / `variant_removed`: German configurator offering changes.
- `price_change`: list-price change with currency, VAT basis, model/trim, effective date and before/after prices when verified.
- `financing_offer`: financing/lease/incentive terms, dates and eligibility; not interchangeable with list price.
- `supply_disruption`: production/delivery bottleneck with Germany relevance and evidence.
- `recall_notice`: regulator/manufacturer notice, including KBA reference when available.
- `recall_remedy`: OTA software fix vs workshop/physical remedy; distinct from announcement date.

For recalls distinguish publication date, defect period, remedy start, affected model/year, severity, affected German vehicles (only if explicitly sourced), and whether it plausibly constrains deliveries. **A recall is not inherently a negative sales shock.** Multiple events may refer to the same underlying incident; link them via stable parent IDs rather than double-counting.

## 3. Machine-readable evidence ledger

Create a compact, versioned ledger such as `data/tesla_product_events/evidence.json` and a schema/validator. Each record should include:

- stable `event_id`, `event_type`, title, affected model(s)/trim(s), geography and Germany evidence;
- event date or interval, precision (`day`, `month`, `year`, `unknown`), date role (`announced`, `effective`, `observed_active`, `ended`, etc.);
- factual description, source URLs, publisher, accessed-on date, primary/secondary status, quoted evidence snippet within copyright limits;
- status (`verified`, `partial`, `unverified`, `excluded`), conflicts, explicit missing fields and rationale;
- optional prices/units, KBA recall reference, affected vehicle counts, remedy category;
- provenance category (`observed_event`, `derived_indicator`, `hypothesis`) and version.

Keep source-level observations separate from inferred event windows. Do not invent dates, prices, production quantities, delivery lead times, recall severity, or German reach.

## 4. Availability proxy: avoid a false TDP equivalent

Investigate whether historical German configurator evidence supports a monthly **Model Availability Index**. Treat it as a potential *breadth-of-orderable-offer* proxy, **not** as Total Distribution Points or physical inventory/supply capacity.

First define a stable model/trim taxonomy and evidence rules for when an offering is verifiably orderable. Build a monthly unweighted count **only for months with sufficient coverage to distinguish absence from missing observation**. Isolated archived snapshots do not prove uninterrupted availability between them. Unknown months remain `null`, not zero. Do not assign volume weights without independently sourced, predeclared information. Keep availability breadth separate from delivery capacity and pricing.

If coverage is insufficient, deliver a feasibility report and event-based indicators instead of a fake continuous MAI.

## 5. Monthly indicators, no outcome fitting

Implement a deterministic, small Python transformer for 2018-01 through 2025-12 that can emit separate indicators for verified announcement, German order opening, first delivery, refresh, verified price changes, recall notice and remedy. For day-precise events, document the monthly assignment rule; for month-only evidence retain precision flags. Where an event was not verified, use unknown/coverage flags rather than claiming confirmed inactivity.

Do not fill undocumented intervals with zeros. No fabricated continuous price series or recall exposure counts. Do not merge into the Google Trends or KBA dataset in this task. No regression, lag tuning, causal inference, ROI or recovery benchmark.

## 6. Research protocol for later analysis

Write `docs/TESLA_PRODUCT_RECALL_RESEARCH.md` including:

- event source inventory, temporal precision, coverage and limitations;
- plausible different lags for order start versus delivery/registration;
- endogeneity: launches, discounts and recalls may respond to demand or operating conditions;
- confounding by subsidies, supply, model mix, seasonality, general BEV trends and attention;
- 2022 and 2026 energy-price-shock questions as future research only; this task's KBA panel ends in 2025;
- candidate future specifications, *not estimated now*, with a predeclared sparse set of events and sensitivity analyses;
- a clear distinction between event-study associations, forecast improvement and causal identification.

Do not revise the frozen Task 01G analysis protocol retrospectively. Propose a separately reviewed extension if needed.

## 7. Tests and CI

Add targeted offline tests for: schema and required provenance; impossible dates and temporal order; Germany-specific evidence; duplicated parent incidents; price currency/units; recall notice vs remedy; event-to-month mapping; unknown vs zero; partial-date handling; sparse configurator snapshots not becoming continuous availability; deterministic regeneration; non-overwrite of existing KBA/Trends artifacts.

No live web requests in CI. No new general-purpose compliance framework. Do not assert test/CI success without actual execution. Record exact commit and workflow links.

## 8. Deliverables and review gates

Deliver:

1. `data/tesla_product_events/evidence.json` with verifiable source citations and unresolved entries clearly marked;
2. compact source/search log and data dictionary;
3. deterministic monthly indicators with missingness/coverage columns, if supported;
4. `docs/TESLA_PRODUCT_RECALL_RESEARCH.md` and short README link;
5. offline validator/transformer and focused tests;
6. Draft PR with concise event counts by type/status, coverage, unresolved sources, actual test and CI outcomes.

**Acceptance criteria:** A reviewer can trace each asserted German event and its date to a specific source, distinguish order opening from deliveries, and distinguish recall announcements from remedies. Any Model Availability Index is only produced where historical coverage supports it. No private Trends data or unapproved third-party material is published. Leave PR in Draft; do not merge.

## 9. Effort discipline

Do a focused initial pass rather than exhaustively searching every Tesla news article. Prioritize events likely to affect the 2018–2025 German registration series, but define selection criteria *before* consulting KBA outcomes. Report coverage gaps instead of widening scope indefinitely. Scientific substance and inspectability take priority over file count and elaborate infrastructure.


## Execution record — 2026-10-24

- [x] Current main including merged PR #12 used; no unmerged branch dependency or inherited timestamp acceptance.
- [x] Focused selection precedes outcome relationships; no KBA/Trends tables consulted and no models/associations estimated for this research.
- [x] 17 phase records, 11 parents and 16 substantive sources; 10 verified narrow claims, 6 partial, 1 excluded. Nine explicit German milestones plus one qualified German manufacturer-remedy guidance date.
- [x] Actual archived German configurator body read; limited point evidence, not continuous catalog coverage. All 96 MAI cells unknown.
- [x] Separate publication/event dates and recall notice/remedy, parent deduplication, price/financing/VAT gaps and source conflicts documented. No German recall population/KBA reference invented.
- [x] Source/search log, schema/validator, deterministic 96-month indicators/hash summary, dictionary and research report delivered.
- [x] Local full suite 210 passed (14 new), 37.921 s; targeted suite 14 passed; validator/audit/lint/whitespace/protected-artifact checks passed.
- [x] Existing KBA/Trends data, frozen protocol, MMM/results, estimator isolation and other repositories unchanged.
- [ ] Exact-head remote CI conclusions/URLs maintained in Draft PR after completion.

No live API research in CI, no raw article/configurator payload/images redistributed,
no numeric continuous MAI, outcome fitting, causal/ROI claim or automatic merge.
