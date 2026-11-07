# German retail fuel prices (EU Weekly Oil Bulletin) — metadata only

Retrieval 2026-11-07. Source: **European Commission, DG Energy, Weekly Oil
Bulletin – price history workbook** (`Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx`),
sheet `Prices with taxes`, columns `DE_price_with_tax_euro95` (new: Euro-super 95)
and `DE_price_with_tax_diesel`.

**No price values are committed.** The repository's rights decision for this
workbook (`docs/ENERGY_RIGHTS_ADMISSION.md`) admits it for private retrospective
research only; public redistribution of derived values is not approved, because
the applicability of the EU CC BY 4.0 default to Member-State-supplied price data
is unresolved. On 2026-11-07 the Commission legal notice
(https://commission.europa.eu/legal-notice_en) was readable again and states
CC BY 4.0 for EU-owned content; the workbook itself says "Reproduction is
authorised provided the source is acknowledged". Whether that suffices for
publishing the derived series is a **maintainer decision**, not taken here.

`sources.json` pins the workbook (URL, retrieval second, bytes, SHA-256), the exact
columns and the hashes of the privately generated outputs.

## Method (identical convention to `fuel_oil.import_energy`)

- EUR per 1000 l → EUR per litre (exact `/1000`).
- Each Monday bulletin value covers Monday–Sunday. A calendar month receives a
  value only if every day is covered by a non-missing weekly value; the monthly
  value is the calendar-day weighted mean. Otherwise the month stays empty.
- Nominal, incl. taxes, national weighted average; not E10, not daily pump prices.

## Coverage of the 2026-11-07 vintage (computed, values private)

| Window | Months | Complete Euro-super 95 | Complete diesel |
|---|---:|---:|---:|
| 2018-01 – 2026-10 | 106 | 93 | 93 |
| 2021-01 – 2026-10 (KBA model window) | 70 | 65 | 65 |

Incomplete months (both grades, holiday weeks without a bulletin): 2018-04,
2018-12, 2019-01, 2019-04, 2019-12, 2020-01, 2020-04, 2020-12, 2021-01, 2021-04,
2021-12, 2022-01, 2022-04. None after April 2022. The diesel count for 2018–2025
(13 of 96 incomplete) reproduces the independently documented private diesel QA.

## Regenerate privately

```sh
python -m fuel_oil.oil_bulletin --workbook PATH/wob_history.xlsx \
  --output PRIVATE_DIR --start 2018-01 --end 2026-10
python -m unittest tests.test_oil_bulletin
```

Verify the workbook hash against `sources.json` first; the Commission revises the
history workbook in place.
