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

Details and future protocol: [Research report](../../docs/ORGANIC_ATTENTION_FEASIBILITY.md).
