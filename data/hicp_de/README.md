# Eurostat HICP for Germany: electricity, new cars, all items (2018-01 – 2026-10)

Source: **Eurostat, `prc_hicp_minr`** (HICP – ECOICOP ver. 2, monthly), Germany,
unit `I25` (index 2025 = 100). © European Union, CC BY 4.0
([Eurostat copyright notice](https://ec.europa.eu/eurostat/help/copyright-notice)).
Changes: three series selected, nothing else. Retrieved 2026-11-07
(dataset updated 2026-11-04).

| Column | COICOP 2018 | Meaning | Last month |
|---|---|---|---|
| `electricity_index_2025` | CP0451 | Household electricity consumer prices — proxy for BEV home-charging cost (not public charging) | 2026-09 |
| `new_cars_index_2025` | CP07111 | New passenger cars, all powertrains, quality-adjusted list/transaction prices — general car-price level, **not** brand prices | 2026-09 |
| `all_items_index_2025` | TOTAL | All items (October 2026 is a flash value) | 2026-10 |

No gaps 2018-01 – 2026-09. October 2026 is empty for the two component series
(not yet published) and is **not** filled. The 2015-based dataset `prc_hicp_midx`
ended in December 2025; the 2025-based dataset is used throughout so that no
splicing is needed.

Rebuild: download the three API URLs in `sources.json` to `RAW_DIR/minr_<code>.json`, then

```sh
python -m multibrand.hicp --raw-dir RAW_DIR
```
