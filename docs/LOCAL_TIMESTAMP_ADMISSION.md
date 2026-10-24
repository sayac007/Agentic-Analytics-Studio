# Task 01G.1 — proposed qualified local timestamp basis

## Decision requiring explicit human acceptance

For **private retrospective analysis only**, permit metadata 1.2.0 to use a
user-attested local Windows file creation timestamp as the analysis-time reference,
while preserving its evidence type and limitations. This is an explicit provenance
amendment to Task 01G's exact retrieval-time basis, **not a change to its frozen
statistical methods**. The original Task 01G protocol remains unchanged and hashed.
No previous unknown Google download time becomes verified by this amendment.

The proposed specific reference is **2026-10-23T18:20:44+02:00**, evidence type
`local_file_creation_time`. Europe/Berlin was UTC+02:00 on that date. The same wall
time was reported as modification time; later access time is not selected as creation
or retrieval time. UTC conversion is 2026-10-23T16:20:44Z, not a second observation.

Evidence available to this task: the user's workorder describes Windows properties
for the original file and its size. A separate original Windows screenshot is not
attached in the accessible conversation. Consequently this is **user-attested
screenshot transcription**, not a claim that the assistant independently inspected
the image, verified Windows metadata or witnessed a Google delivery event.
No local Windows username/path or private screenshot is published.

## Qualification retained with every accepted artifact

User-attested local Windows file creation time in Europe/Berlin; not independent
proof of Google delivery. Local metadata may be copied or altered; SHA-256 establishes
byte identity only. The field `retrieved_at` in this new version denotes the qualified
**analysis timestamp used**, not a source-confirmed download instant.

The type `verified_google_download_time` is not accepted by this local-evidence
contract. It cannot be inferred from a screenshot, matching size, matching created/
modified times, an access time, a hash or a user confirmation of private-use rights.
No historical Point-in-time availability follows.

## Narrow implementation and gate

- Versions 1.0.0/1.1.0 retain their existing interfaces and behavior. Version 1.2.0
  adds `timestamp_evidence_type`, `timestamp_evidence_limitations` and
  `local_timestamp_basis_accepted`; the only new supported evidence type is
  `local_file_creation_time`.
- Local offset must match Europe/Berlin at that instant, including daylight-saving
  rules. Limitations are mandatory. Unknown/malformed times/types or an unaccepted
  basis fail before import; `--inspect-pending` can emit a report with no value CSVs.
- Acceptance must be an **explicit human decision** about this qualified basis. The
  current user workorder is conditional and does not silently set that decision true.
  Proposed actual metadata therefore uses `local_timestamp_basis_accepted=false`.
- The separate private econometric admission record must also reflect that same
  decision and bind this document's SHA-256 through
  `local_timestamp_amendment_sha256`. This is one human decision recorded in two
  bound artifacts, not a request for duplicate permission.
- Existing source, raw/metadata/subset/protocol/KBA hashes, rights and calendar gates
  remain. Existing confirmed lawful private analytical use is retained and need not
  be requested again. Public redistribution remains a separate decision.

After human acceptance and completion of the existing source-specific review, the
original full export can be imported privately. It keeps the request-wide 0–100 scale,
row-selected 96-/60-month subsets and a partial October 2026 bucket. The existing
frozen diagnostic CLI can then run privately with the unchanged statistical protocol.
The output binds both the frozen protocol and this provenance amendment, and records
the qualified timestamp and limitations explicitly. No real run occurs before that
acceptance. No model selection, causal attribution, ROI or MMM changes are authorized.

## Concrete acceptance question

Does the user accept the **workorder-described local creation evidence** at
2026-10-23T18:20:44+02:00 as sufficient for the private retrospective analysis,
with the limitations above and without treating it as verified Google download time?

Until that decision is explicit, outcome **B** applies: `pending_empirical_admission`,
no admitted real-data CSVs/diagnostics, and a documented next action. A later explicit
approval can be recorded against the unchanged raw/metadata/protocol/amendment hashes;
no approval or review timestamp is fabricated in advance.
