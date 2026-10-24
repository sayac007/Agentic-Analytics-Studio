# Task 01I.2 — energy rights and private retrospective admission

Assessment date: 2026-10-24. Base `main` `b80be27`, with PRs #16/#17 confirmed merged.
No energy/outcome models, correlations, new statistical protocol or public real values.
This records source-specific decisions, not a general legal opinion.

## Evidence actually reviewed

1. Three private original files and normalized snapshots remain available. Exact
   raw SHA-256 bindings match the existing real-source catalog and private inventory.
   Native identities/units/layouts are those verified in
   [Task 01I.1](REAL_ENERGY_DATA_IMPORT.md). No import rerun or successful live download
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

## Source-specific decision matrix

Statuses apply to the **intended source and analytical scope**, not a claim that an
unresolved use is legally prohibited. `not_verified` means evidence/decision pending.

| Source | Private analysis | Public unchanged raw redistribution | Public derived redistribution | Analytical admission |
|---|---|---|---|---|
| ECB `EXR.M.USD.EUR.SP00.A`, monthly USD/EUR | not_verified | not_verified | not_verified | blocked pending exact-product exception review and human decision |
| EIA `RBRTE`, monthly USD/barrel | not_verified | not_verified | not_verified | blocked pending exact-product exception review and human decision |
| EC Germany diesel monthly overlap approximation | not_verified | permitted conditionally for literal source reproduction | not_verified | blocked pending derived-scope review and human decision |

All three have verified source identity, unit and raw-hash bindings, within the
limitations below. No actual human admission approval has been recorded or generated.
A source's private permission does not require permission to publish its raw/derived
values. Conversely, a literal reproduction notice is not automatically a decision
about a project-defined monthly estimator. Rights status is also separate from the
workorder's explicit restriction against publishing real observations.

### ECB — externally reviewed general policy; exact source exception pending

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

Pending: source-specific confirmation that this exact EXR product is covered without
an applicable third-party/exception restriction, then an explicit source-bound private
admission decision. Do not require publication permission merely to admit private use.

### EIA — externally reviewed general policy; protected-material exception pending

[EIA Copyrights and Reuse](https://www.eia.gov/about/copyrights_reuse.php): external
review reports general public-domain use/distribution of US-government information
products/databases, acknowledgment including publication date, source links and
translator credit for translations. **Third-party contributed/licensed materials,
logos and some images** may have separate protected rights.

Actual OLE workbook verifies EIA `RBRTE`, Europe Brent Spot Price FOB, Monthly,
Dollars per Barrel. No special licence field was found in the inspected source
layout; that is not proof that protected contributed data are absent. Workbook clock
text is not a proven publication/retrieval timestamp and will not be used as one.

Pending: exact RBRTE product/exception check and a source-bound private admission
decision. Attribution must retain unknown publication date rather than invent one;
use the verified snapshot hash/vintage description and add an actual date when evidenced.

### EC — direct workbook notice plus externally reviewed default, derived scope pending

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

Pending: confirm applicability of the externally reviewed general/individual notices
to private monthly derivation, appropriate credit/change notice, and an explicit
source-bound private admission decision. No extra permission for publishing values
is silently folded into this private-analysis decision.

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
private-retrospective scope, reviewer and hash-bound human decision evidence. No
approval flags or success-looking admission files are created by this assessment.
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

The actual private verification/writer command ran: **zero admissions written** and
no admission directory created. This is a real blocked decision, not a missing-file
claim. Full tests/CI are reported after actual execution; green code tests are not
scientific admission or legal clearance.

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

## Concrete decision required before Task 01J

The external handoff expressly says it is **not blanket source-specific admission**
and retains exact-product exception/ownership checks. The remaining review/decision
must therefore be recorded per source; no approval is assumed from the handoff.

Potential subset **after** its own checks and human decision: ECB + EIA could support
a separately authorised private Brent/FX study without waiting for diesel. They do
not currently satisfy Task 01J's unchanged requirement for admitted diesel as well;
any narrower study scope needs explicit human authorisation, not a silent protocol
change. Diesel inclusion additionally needs a predeclared treatment of the 13 gaps
and 2022 missing months. No subset is admitted **now**, and no Task 01J work is run.

Requested final review: confirm absence/applicability of third-party exceptions for
EXR and RBRTE, confirm the exact EC monthly private-derived scope, and approve or
reject **each** private retrospective admission against this matrix's hash bindings.
Public raw/derived release and 2026 KBA admission remain separate decisions.

## Actually executed validation

Python 3.12.14, existing pinned dependencies; no new dependency:

- Full local suite: **292 passed**, 45.164 s (274 existing + 18 new rights tests).
- Targeted rights suite: **18 passed**, 0.166 s, offline/synthetic permits only.
- Actual private raw/normalized/monthly hash and coverage audit passed; attempted
  writer returned zero admissions and created no admission directory.
- Both contract examples, KBA audit, unchanged importer metadata check, rights check,
  Ruff import/format and whitespace checks passed. Earlier acquisition/coverage and
  source/unit/hash bindings remained unchanged.
- Initial fixture-root/repeated-fixture/text-format assertion failures were corrected;
  the final results above passed. No source permission was changed to fix a test.

Exact-head remote Actions links/conclusions are maintained in the Draft PR after
observed completion. Green tests are code verification, not source rights clearance.
