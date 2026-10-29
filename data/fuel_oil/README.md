# Blocked fuel/oil/FX acquisition

No numeric real observations or empty pseudo-observation files are committed.
`access_log.json` records ten actual failed primary requests. `sources.json` keeps
candidate definitions/URLs separate from verified metadata and rights. `coverage.json`
binds the catalog and reports zero retrieved verified observations for all four
candidates in 96/105-month windows; it does not prove absent publisher history.

Run `python -m fuel_oil.fetch_fuel_oil --check` offline. See
[acquisition and manual handoff](../../docs/archive/docs/GERMAN_FUEL_OIL_ACQUISITION.md) and
[conditional attribution](../../docs/archive/docs/DATA_SOURCES_FUEL_OIL.md). Keep later raw/derived
snapshots outside Git until separately reviewed rights and admission are resolved.

## Later uploaded-original assessment (Task 01I.1)

`real_sources.json` binds the three actual user uploads, source identification and
rights/provenance gaps. `real_coverage.json` contains metadata/QA only, computed from
those originals: source-native ECB/Brent 96/105 months; diesel temporal coverage
83/92 months; zero admitted. This later assessment does not rewrite the earlier
blocked live-access report. See `docs/REAL_ENERGY_DATA_IMPORT.md`.
