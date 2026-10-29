# Task 01I.2 — energy rights and private retrospective admission

Assessment date: 2026-10-24. Base `main` `b80be27`, with PRs #16/#17 confirmed merged.
No energy/outcome models, correlations, new statistical protocol or public real values.
This records source-specific human decisions, not a general legal clearance.
The explicit review of 2026-10-24 accepts ECB and qualified EC private use, while
withholding unconditional EIA admission. PR #18 remains Draft; Task 01J is not authorised.

## Evidence actually reviewed

1. Three private original files and normalized snapshots remain available. Exact
   raw SHA-256 bindings match the existing real-source catalog and private inventory.
   Native identities/units/layouts are those verified in
   [Task 01I.1](archive/docs/REAL_ENERGY_DATA_IMPORT.md). No import rerun or successful live download
   is claimed: this task rechecked existing raw/normalized hashes and QA metadata.
2. The actual EC workbook reproduction notice was reread at `Prices with taxes!B1115`
   and `B1117`. A metadata-only [evidence artifact](../data/fuel_oil/rights_evidence/ec_embedded_notice.json)
   binds the source hash, cell-text hashes and short quotation. It permits literal
   reproduction with source acknowledgement; no real values are copied here.
3. Five new official policy/methodology requests failed at the environment proxy,
   CONNECT 403. Exact URLs, UTC assessment/request times, null provider status and
   null policy-body hash are recorded. Failed requests are **not** policy evidence.
4. The user supplied an [externally reviewed research handoff](../data/fuel_oil/rights_evidence/externally_reviewed_policy_handoff_2026-10-24.md).
   Its original bytes are preserved and hash-bound in
   [`rights_admission.json`](../data/fuel_oil/rights_admission.json). Accept its general
   policy findings as **externally reviewed primary-source research**, not as pages
   personally accessed by Codex, complete verbatim legal texts, a legal opinion or
   blanket source-specific approval. Review date is day-precision 2026-10-24; no
   external access clock time is invented. Own assessment timestamps are separate.

5. The user then supplied the [explicit human decision](../data/fuel_oil/rights_evidence/human_admission_decision_2026-10-24.md).
   It is preserved as a transcribed message and a hash-bound structured transcription,
   separately from the earlier general research handoff. The decision has **day
   precision only**; its exact instant is unknown. No download/publication/as-of
   timestamp is inferred. Exact source keys/units/raw hashes bind each decision.

## Source-specific decision matrix

Statuses apply to the **intended source and analytical scope**, not a claim that an
unresolved use is legally prohibited. `not_verified` means evidence/decision pending.

| Source | Private analysis | Public unchanged raw redistribution | Public derived redistribution | Analytical admission |
|---|---|---|---|---|
| ECB `EXR.M.USD.EUR.SP00.A`, monthly USD/EUR | permitted for stated private scope | not_verified / no approval | not_verified / no approval | admitted, private retrospective only |
| EIA `RBRTE`, monthly USD/barrel | provisional support only; legal status `not_verified` | not_verified / no approval | not_verified / no approval | blocked; unconditional permit explicitly withheld |
| EC Germany diesel monthly overlap approximation | permitted, qualified project-specific basis | not_verified / no approval | not_verified / no approval | admitted with unresolved limitations retained |

All three retain verified source identity, unit and raw-hash bindings. The two
private admissions follow the **explicit human decision and successful integrity
checks**, not the earlier general handoff alone. Public redistribution is not
approved for any source. The EC literal-source reproduction notice remains evidence
of conditional source acknowledgement terms; it is not a public-release approval.
Qualified EC acceptance is not full legal clearance: its third-party/member-state
scope limitations remain `not_verified`, and no legal guarantee is claimed.
`analysis_scope_verified` refers to the recorded private-scope acceptance supported
by the explicit human decision; it does not assert independent legal clearance of
the unresolved EC ownership/third-party limitations.

### ECB — human-accepted private retrospective source

[ESCB reuse policy](https://www.ecb.europa.eu/stats/ecb_statistics/governance_and_quality_framework/html/usage_policy.en.html):
external review reports free reuse of public ESCB statistics, commercial/noncommercial,
with credit and preservation of official statistics/metadata. Confidential statistics
are excluded; standard disclaimers, revisions/withdrawal, exceptional restrictions and
**third-party originator permission** remain relevant. Project transformations must
be distinct from unchanged official source observations.

Actual upload verifies the exact EXR monthly reference-series key and USD-per-EUR
header; it has no source-agency or licensing column. That absence does not independently
resolve third-party exceptions. The precise monthly collection convention is still
not supplied by this portal export. Source-reference URL is known, actual download
URL/time and revision flags remain unknown; these are retained provenance gaps, not
invented new timing gates for retrospective use.

Human decision: **ACCEPT** this exact EXR source for private retrospective exploratory
research, citing ECB reference-rate methodology and ESCB reuse policy, subject to
existing source/unit/hash/attribution/integrity gates. Those gates were rechecked.
This records human acceptance, not personal Codex access to those pages or historical
point-in-time/public-redistribution permission.

### EIA — Refinitiv/LSEG underlying source; unconditional admission withheld

[EIA Copyrights and Reuse](https://www.eia.gov/about/copyrights_reuse.php): external
review reports general public-domain use/distribution of US-government information
products/databases, acknowledgment including publication date, source links and
translator credit for translations. **Third-party contributed/licensed materials,
logos and some images** may have separate protected rights.

Actual OLE workbook verifies EIA `RBRTE`, Europe Brent Spot Price FOB, Monthly,
Dollars per Barrel. No special licence field was found in the inspected source
layout; that is not proof that protected contributed data are absent. Workbook clock
text is not a proven publication/retrieval timestamp and will not be used as one.

The new human review reports that EIA's official spot-price source notes identify
**Refinitiv (LSEG)** as the underlying data source. Record this as a human-reviewed
source finding, not a source-note page personally fetched by Codex; no exact notes
URL or access instant was supplied and none is invented.

Human decision: general EIA reuse supports **provisional internal exploration**, but
source-specific third-party rights remain unresolved. Preserve `legal_status=
not_verified`; **do not create an unconditional analytical admission permit**. No
RBRTE private admission record was emitted, and the permission flags cannot be
changed to override the structured human withholding decision.

Attribution retains unknown publication date rather than inventing one and records
the underlying Refinitiv/LSEG source per human review. Source data availability is
not rights clearance. This source remains outside the admitted subset.

### EC — qualified project-specific private acceptance, not legal clearance

[EU legal notice](https://european-union.europa.eu/legal-notice_en),
[Weekly Oil Bulletin](https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en):
external review reports CC BY 4.0 as the default for EU-owned website content with
credit/change notices, subject to individual notices, third-party ownership and
excluded trademark/logo/other rights. The handoff explicitly leaves ownership and
Member State supplied price-data applicability unresolved for this historical workbook.
It does not establish that every government-hosted dataset is CC BY 4.0.

The workbook itself states: “Reproduction is authorised provided the source is
acknowledged.” Thus the exact source's literal reproduction has a conditional
permission basis and private handling of original bytes is supported. This is not
public release approval, and does not settle the intended monthly derived-use scope.
The unchanged original, unit conversion and monthly overlap assumption remain separate.

EUR/1,000 litres is accepted from the user's cited
[Decision 1999/566/EC](https://eur-lex.europa.eu/eli/dec/1999/566/oj/eng/pdf) plus
independently verified `Prices with taxes!A/BB/BD` Germany/diesel/with-tax mapping.
The decision is **methodology/unit evidence, not a licence**; its PDF remains unread
by Codex due proxy failure. Conversion is original `/1000`. Calendar-day weighting
of Monday–Sunday intervals is a clearly labelled project approximation, not evidence
of seven measured daily prices or an official monthly mean.

Human decision: **ACCEPT on a qualified project-specific basis** for private
retrospective research, including the separate `/1000` conversion and explicitly
labelled calendar-overlap monthly approximations. Preserve original weekly bytes,
embedded acknowledgement notice, credit/change notices and all 13 missing months.
Unresolved third-party/member-state scope limitations remain in the matrix and
private permit; legal status remains `not_verified` rather than being promoted to
full legal clearance. No public redistribution approval or legal guarantee follows.

## Actual diesel missingness — independent of outcomes

The existing private monthly QA was hash-verified; all 13 incomplete months remain
null, with no interpolation, carry-forward or invented daily observations.

| Year | Incomplete months | Count |
|---|---|---:|
| 2018 | April, December | 2 |
| 2019 | January, April, December | 3 |
| 2020 | January, April, December | 3 |
| 2021 | January, April, December | 3 |
| 2022 | January, April | 2 |
| 2023–2025 and completed 2026 | none under the existing overlap rule | 0 |

Actual completed coverage: ECB/Brent **96/96** (2018–2025) and **105/105** through
September 2026; diesel **83/96** and **92/105**. January and April 2022 are missing:
2022 has ten complete monthly approximations. This affects potential energy-only
onset/lag support; do not bridge the gaps or choose a favorable episode date. No
registration/attention relationships were inspected. E10 remains excluded. October
2026 remains partial; KBA ends in 2025, so a 2026 outcome comparison stays blocked.

## Independent admission mechanics and reproducibility

`fuel_oil/rights_admission.py` checks each source's identity/unit/raw hash, evidence
hash and contained paths, source-specific scope/exception review and explicit human
decision **independently**. A blocked diesel decision or absent diesel private file
does not prevent a supported ECB/EIA admission. Public redistribution states are not
prerequisites for private analysis. Missing review evidence cannot be replaced with
a URL or self-declared `admitted` flag; test permits are synthetic only.

A positive private decision must name the source key, original unit, exact raw hash,
private-retrospective scope, reviewer and hash-bound human decision evidence. The human approval is recorded only for ECB and qualified EC use; EIA has an
explicit withholding record. No unapproved source receives a success-looking permit.
When genuinely supported, the writer emits only per-source hash-bound admission
metadata in a new private directory, never source values. It rechecks that source's
own original/normalized hashes and coverage. Diesel admission additionally binds its
monthly approximation and all gaps. Historical point-in-time stays `not_established`.
Evidence gates and records are attestation checks, not automated legal interpretation.

Existing importer catalogs, quarantined outputs, previous coverage, frozen protocols
and numerical results are unchanged. This later matrix adds an explicit rights layer;
legacy acquisition snapshots are not silently rewritten as permits.

```sh
# Existing pinned Python 3.12 environment; no new dependencies.
python -m fuel_oil.rights_admission --check
python -m unittest discover -s tests -p test_energy_rights.py -v
# Private verification, no values/paths printed:
python -m fuel_oil.rights_admission --check --private-dir /PRIVATE/energy-run
# Only after supported review/decision records exist:
python -m fuel_oil.rights_admission --private-dir /PRIVATE/energy-run --output /PRIVATE/new-admissions
```

The actual private verification/writer command rechecked original, normalized and
monthly hashes/coverage and wrote **exactly two** private records: ECB and qualified
EC diesel. No RBRTE record exists. They carry matrix/decision/source hashes, the
day-precision human decision, attribution, all conditions, unresolved limitations,
no-public-release status and `task_01j_authorized=false`. Source observations remain
private and unchanged. Existing `quarantined` files are historical QA snapshots;
the new source-bound permits form a separate private authorisation layer.

## English credits and change notices (conditional on resolved source scope)

- ECB unchanged source: “Source: ECB statistics. EXR.M.USD.EUR.SP00.A, USD per EUR;
  snapshot SHA-256 [verified hash].” Preserve official metadata. For derived work:
  “Project-derived analysis of ECB statistics; not an official ECB statistic.”
- EIA: “Source: U.S. Energy Information Administration, Europe Brent Spot Price FOB
  (RBRTE), monthly USD/barrel; publication date unknown in this export, snapshot
  SHA-256 [verified hash].” Replace unknown date only with verified evidence; source
  workbook text and ingestion time are not invented publication dates.
- EC: “Source: European Commission, Directorate-General for Energy, Weekly Oil
  Bulletin, Germany automotive gas oil, prices including taxes; snapshot SHA-256
  [verified hash]. EUR/litre conversion and calendar-overlap monthly estimates
  calculated by Agentic Analytics Studio from weekly observations; not official
  monthly means. Source acknowledged under the workbook reproduction notice.”

## Task 01J remains stopped; future admitted-source scope needs approval

Current admitted subset: **ECB EUR/USD + qualified EC Germany diesel**, only for
private retrospective exploratory research under the recorded conditions. RBRTE is
not unconditionally admitted because Refinitiv/LSEG rights remain unresolved.

Task 01J's unchanged scope requires admitted Brent as well as the other energy
sources; it therefore cannot start automatically. A future study limited to the
admitted subset requires its **own explicit scope approval and preregistered protocol**,
including treatment of the 13 gaps/January and April 2022. No models or frozen Task
01G changes are made here. A 2026 outcome comparison also still requires separately
verified KBA 2026 data. Public release and historical as-of use remain unapproved.

## Actually executed validation

Existing pinned Python 3.12.14 environment; no new dependencies:

- Final full suite for explicit human decisions: **294 passed**, 43.030 s.
- Targeted rights suite: **20 passed**, 0.141 s. Synthetic tests retain a separate
  pending baseline; real human decisions are checked against the structured message
  transcription, including EIA withholding and qualified EC limitations.
- Actual private check revalidated original/normalized/monthly hashes and coverage;
  exactly two permits were emitted and bound to the current matrix. No EIA permit.
- Both contract validators, KBA audit, unchanged importer metadata check, rights
  check, Ruff import/format, whitespace and protected-path checks passed.
- No raw files, normalized values, source hashes, frozen protocols, MMM/Stage A or
  KBA/Trends/Macro data changed. No Task 01J or new outcome fit ran.

Current-head remote Actions evidence is updated in Draft PR #18 only after observed
completion. Previous-head CI is not evidence for this decision update. No automatic
merge or public release approval follows from green tests.
