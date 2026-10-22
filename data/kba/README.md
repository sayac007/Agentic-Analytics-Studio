# Observed KBA extraction, frozen retrieval 2026-10-22

Datenquelle: Kraftfahrt-Bundesamt, FZ 10 Monatsergebnisse, Abruf 2026-10-22;
[dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0);
**eigene Berechnung/eigene Darstellung** (extraction/normalization).
Dataset URIs and raw hashes: `sources.json`; exact sheets/cells: `derived/locations.json`.

`derived/observations.csv` contains observed monthly German passenger-car registration
counts. Each series is explicit: `brand:...` is all powertrains, `market:BEV` is BEV-only.
No synthetic extension or inferred zeros. `vintage` is the source workbook's raw hash;
`quality.json` separately identifies the normalized file hash and column lineage.

Full reporting/execution instructions and admission blockers:
[docs/KBA_MULTIBASELINE.md](../../docs/KBA_MULTIBASELINE.md).
All four selected references are **blocked**, not currently generator inputs.
This acquisition table is never estimator input. No recovery runs were performed.
Keep this attribution, the primary-source catalog and license link with redistributed
derived data. Full raw workbooks remain outside Git; fetch and verify their pinned
bytes using the documented CLI. Transformed offline test fixtures have their own
catalog and cannot be substituted for original source releases.
