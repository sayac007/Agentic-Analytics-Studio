# Blocked fuel/oil/FX acquisition

No numeric real observations or empty pseudo-observation files are committed.
`access_log.json` records ten actual failed primary requests. `sources.json` keeps
candidate definitions/URLs separate from verified metadata and rights. `coverage.json`
binds the catalog and reports zero retrieved verified observations for all four
candidates in 96/105-month windows; it does not prove absent publisher history.

Run `python -m fuel_oil.fetch_fuel_oil --check` offline. See
[acquisition and manual handoff](../../docs/GERMAN_FUEL_OIL_ACQUISITION.md) and
[conditional attribution](../../docs/DATA_SOURCES_FUEL_OIL.md). Keep later raw/derived
snapshots outside Git until separately reviewed rights and admission are resolved.
