# Task 01G.1 — current decision/status

## Completed checks

PR #10 and PR #11 were confirmed merged before branching from current main at
`b2ee65b56c1461de98be70c4f06833b1ddb82abe`.
The actual private original is present: **2,947 bytes**, **274 monthly records**, January
2004–October 2026, with independently recomputed SHA-256:
`28e0b00b697ceb65833ca5bb2039d43c0ab4350d9a732e884edd3a44fe0da84e`.
No real index values or screenshot are committed.

The workorder reports local Windows created/modified time **2026-10-23 18:20:44**,
and access time **18:22:04**, Europe/Berlin. The proposed creation-time reference is
**2026-10-23T18:20:44+02:00**, typed `local_file_creation_time`. The available evidence
is the user's **workorder description** of properties; no separate Windows image
was available to independently inspect. No Windows username/local path is published.
Metadata may be copied/altered. This is not `verified_google_download_time`, a signed
Google event or evidence of historical as-of availability. Original exact Google
download time remains unknown; the previous unknown-time record is preserved.

Private analytical use remains explicitly **user-confirmed** under reviewed Google
conditions. Attribution: Data source: Google Trends (https://www.google.com/trends).
This is not independent legal verification or a new real-value publication decision.
No repeated private-use approval is required.

## Proposed narrow contract

[The reviewable provenance amendment](LOCAL_TIMESTAMP_ADMISSION.md) introduces
metadata 1.2.0 with explicit type, limitations and a human acceptance flag. Existing
1.0.0/1.1.0 interfaces remain unchanged. Local timezone/offset and daylight-saving
rules are checked; invalid or source-confirmed labels are rejected. Existing source,
rights, hash, full-window normalization, missingness and partial-month checks remain.
The diagnostic gate independently requires the same human decision and this amendment's
hash in the bound admission record. The frozen Task 01G statistical protocol is not edited.

**Human acceptance is currently false.** The conditional workorder is not treated as
approval of its own proposed exception. The compact machine-readable
[status](../data/organic_attention/task01g1_status.json) records pending admission and
no real execution. This is definition-of-done outcome **B** until that decision is made.

## Actual private actions and artifacts

Outside Git, `/workspace/private-attention/task01g1/` contains:

- `local_timestamp_evidence.json`: qualified transcription of the supplied description.
- `proposed_local_metadata.json`: unchanged source hash/query/rights, proposed local
  analysis timestamp, and `local_timestamp_basis_accepted=false`.
- `pending_admission.json`: no fabricated human acceptance/review time; existing
  user terms confirmation retained, with raw/metadata/protocol/amendment bindings.
- `inspection/pending.json`: structural inspection only, no admitted values.

A normal real diagnostic invocation was actually attempted and **refused** with
`Explicit human acceptance of qualified local timestamp basis is pending`, before
Trends import/KBA join/statistics. No real-result directory was generated. No admitted
real-value source/subset CSVs, econometric tables, plots or reports were produced.
No original file or earlier private sidecar was overwritten.

## Minimum next action

Explicitly accept or reject the concrete basis in the amendment: use the
**workorder-described local creation timestamp**, with its limitations, for the
private retrospective analysis. This does not request permission to publish values
or re-ask the already confirmed private-use right.

On acceptance, record that decision in both bound metadata/admission artifacts,
update changed metadata hashes and source-specific review fields, import through
the normal 1.2.0 path, and run the unchanged Task 01G CLI. Preserve source-wide scale,
96-/60-month selections and partial October 2026. The frozen model/diagnostic methods
and all no-causal/ROI/as-of restrictions remain. Until acceptance, do not run real
statistics or silently relabel local creation as Google delivery.

## Offline reproduction

```sh
python3 -m pip install -r requirements-attention.lock
python3 -m unittest discover -s tests -p test_local_timestamp.py -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -m unittest discover -s tests -v
```

All positive acceptance cases in tests are **synthetic simulations of a decision**,
not actual approval of this user's evidence. CI remains synthetic-only; no screenshot,
private raw/derived values or empirical output is uploaded as an artifact. Final local
and exact-head remote test evidence is recorded in the workorder/Draft PR.

### Executed local validation (2026-10-24)

- Python 3.12.14, pinned runtime: **196 tests passed**, including **9 new local-time tests**, 37.930 seconds.
- Targeted local-time suite: 9 passed, including qualified type/UTC conversion, Berlin summer/winter offsets, malformed or Google-confirmed labels, explicit acceptance, independent amendment binding, legacy compatibility and preserved hash/rights/scale gates.
- Actual original file: independently re-hashed; private proposed metadata inspected; normal diagnostic execution refused for pending human basis acceptance, with no output directory.
- Ruff on touched Python files, whitespace and protected-artifact checks passed.
- Exact-head GitHub Actions results are reported in the Draft PR only after completion.

No real-data numerical analysis or value publication occurred. The fixed Task 01G
statistical protocol and existing synthetic-only CI remain unchanged.
