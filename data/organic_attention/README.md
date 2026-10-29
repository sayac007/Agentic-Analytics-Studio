# Organic attention feasibility — not empirically populated

Research 2026-10-23; January 2018–December 2025, with separate 2021–2025 coverage.

- `sources.json`: 11 candidate signals, official references, conditional feasibility,
  access/rights/coverage blockers. Potential reconstruction is not observed coverage.
- `access_log.json`: actual document/query URLs, results, document response hashes;
  no raw pages, secrets, real comments, usernames or video counters redistributed.
- `observations.json`: explicit empty empirical dataset, no fabricated observations.
- `monthly_indicators.csv`: 96 months; all attention/view cells **unknown, not zero**.
- `summary.json`: reproducible coverage/diagnostics; 0/96 and 0/60 observed months.

`python3 -m attention.transform [--check]` reproduces/checks the empty artifacts offline.
The positive example in `tests/fixtures/attention/youtube_synthetic.json` is entirely
fictional and must never be presented as Tesla data. Populated adapter inputs are
restricted to synthetic fixtures pending real-data access and rights review.
Current view snapshots cannot become historical view observations. No sentiment,
association, causality or German audience reach is inferred.

Details and future protocol: [Research report](../../docs/DATA.md).

Task 01F keeps these empirical artifacts empty after a fresh official-UI HTTP 429.
`task01f_access.json` records the attempt; `real_data_coverage.json` records 96/60
unknown months. `trends_import_metadata.template.json` is an incomplete handoff template,
not a provenance assertion. Private user-CSV import and rights requirements:
[First real observation handoff](../../docs/DATA.md).

Task 01F.1: `extended_import_handoff.json` records the hash-bound pending structural
inspection, not empirical admission. No real index values are included.
`trends_extended_metadata.template.json` separates source and analysis windows;
see [extended import](../../docs/archive/docs/GOOGLE_TRENDS_EXTENDED_IMPORT.md).
