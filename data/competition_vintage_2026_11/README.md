# KBA FZ10 brand panel, vintage 2026-11 (January 2021 – October 2026)

Datenquelle: Kraftfahrt-Bundesamt, Flensburg, FZ 10; Abruf 2026-11-07;
[dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0); eigene Berechnung/Darstellung.

**Why a separate directory:** the frozen Task 04 study binds
`data/competition/brand_monthly_2021_2026.csv`, `kba_checks.json` and
`kba_sources.json` by SHA-256 and requires exactly 69 months
(`regimes/data.py`, `config/task-04-regimes.json`). Appending October 2026 in place
would silently break `python -m regimes.verify`. The frozen files are therefore
unchanged; this directory is the newer vintage for **future** work only.

| File | Content |
|---|---|
| `kba_sources.json` | The 72 frozen catalog entries unchanged plus `fz10-2026-10` (URL, bytes, SHA-256, retrieval second) |
| `kba_checks.json` | Parser checks for all 73 workbooks; the first 72 entries are identical to the frozen file |
| `brand_monthly_2021_2026_10.csv` | Same schema as the frozen panel; rows up to 2026-09 are byte-identical, 142 October rows appended |

Verification performed on 2026-11-07:

- All 72 previously pinned workbooks were downloaded again; **all 72 match the
  pinned SHA-256 and byte size** (no silent KBA revision of earlier releases).
- Regeneration with the unchanged parser `competition/kba.py` reproduces the frozen
  panel exactly for 2021-01 … 2026-09 (prefix comparison of the CSV text).
- October 2026: 254,492 passenger cars, **94,086 BEV**; Tesla 2,932 BEV
  (3.1 % of BEV), YTD 47,742.

Rebuild:

```sh
python -m competition.kba --catalog data/competition_vintage_2026_11/kba_sources.json \
  --raw-dir RAW_DIR --output /tmp/kba-regen
```

then select `period >= 2021-01` from `brand_release_observations.csv` and add the
two constant columns `source_classification=observed`,
`row_absence_policy=missing_not_zero` (identical to `competition.derive.brand_views`).
The Jan–Sep YTD comparison and price views in `data/competition/` are unaffected.
