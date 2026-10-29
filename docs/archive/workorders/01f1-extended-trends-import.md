# Task 01F.1 — Extended Google Trends Import

Source: user-uploaded `Codex_Task_01F1_Extended_Google_Trends_Import.md`.
The original workorder includes real index examples; those values are deliberately
not copied into this public workorder record.

## Scope and acceptance

- Confirm PR #8 merged; branch `data/task-01f1-extended-trends-import` from current main.
- Preserve the private original export and source-wide scale; separate source and analysis windows.
- Support full history, native monthly German/English CSV, 96/60-month subsets and partial-period flags.
- Preserve provenance/rights gates, missingness, synthetic separation and private output paths.
- Keep pending metadata explicit; no admitted real-data output without verified metadata.
- Offline focused/full tests; English deliverables; Draft PR only, no merge.
- No KBA/Statistical Contracts/MMM/results/isolation or upstream changes, and no outcome analysis.

## Execution

PR #8 merge confirmed: `66abaddd7b736792230a1d325fb498a74f8f3810`.
Original upload found and hash matched; 274 unique ordered monthly rows.
Only a pending structural inspection was run on the actual file. A subsequent user screenshot evidences the URL and UI settings; "today and now"
provides a retrieval date but no exact timestamp. Private-use rights review and
exact download timestamp remain unresolved.
No real index values or admitted real-value CSVs are published.

## Verification and remaining blocker

- [x] Local full suite: 175 passed (11 new), including all 17 legacy import tests.
- [x] Existing offline checks and synthetic Stage-A/KBA fixture smoke checks passed.
- [x] Raw upload preserved; no real index values committed; protected artifacts unchanged.
- [x] Pending inspection, generalized private handoff, synthetic tests and English documentation delivered.
- [ ] Empirical admission awaits exact download timestamp and private-use rights review.
- [ ] Publication of real values requires a separate verified rights/publication decision.
- [ ] Current-commit remote CI result and URLs maintained in the Draft PR.

No automatic merge.
