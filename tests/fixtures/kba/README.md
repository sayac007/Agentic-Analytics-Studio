# Attributed real KBA parser snapshots (not synthetic fixtures)

Datenquelle: Kraftfahrt-Bundesamt, FZ 10 monthly releases, Abruf 2026-10-22;
[Datenlizenz Deutschland – Namensnennung – Version 2.0 (dl-de/by-2-0)](https://www.govdata.de/dl-de/by-2-0).
The exact dataset URIs, raw hashes and source cells are in `sources.json`.
The legacy XLS and KBA license PDF are unmodified. XLSX files are data-table test
fixtures with cover media/drawings removed; original and transformed SHA-256 values
are recorded separately. They are not original downloads, and live fetching and
benchmark admission are refused for this fixture catalog. Selection is solely for parser
coverage: legacy XLS, legacy XLSX, displayed-month Excel date, shifted table header,
modern BEV and corrected release. These seven months are not a continuous benchmark.

The KBA PDF grants reuse for publicly supplied KBA data/statistics, including legacy
files lacking their own imprint. Only numeric registration tables are reused; cover photographs/graphics were removed
from the XLSX fixtures rather than assumed separately licensed. Derived normalized
outputs elsewhere are **eigene Berechnung/eigene Darstellung**; source symbols are
never silently converted to zeros. No historical values are invented in these files.
