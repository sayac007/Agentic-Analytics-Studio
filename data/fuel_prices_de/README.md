# German retail fuel prices (EU Weekly Oil Bulletin), retrieval 2026-11-07

> **Source and rights notice.** Source: European Commission, Directorate-General
> for Energy, *Weekly Oil Bulletin – price history* (© European Union).
> The workbook states: "Reproduction is authorised provided the source is
> acknowledged." EU-owned website content is licensed under CC BY 4.0
> ([legal notice](https://commission.europa.eu/legal-notice_en), read 2026-11-07).
> The prices are **reported to the Commission by the Member States**; whether the
> CC BY 4.0 default covers these Member-State figures was **not independently
> verified**. **Changes:** German Euro-super 95 and diesel columns selected,
> EUR/1000 l converted to EUR/l, monthly values computed (own calculation).
> The European Commission is not responsible for these derived figures.
> Publication follows the maintainer decision of 2026-11-07 recorded in
> [`docs/ENERGY_RIGHTS_ADMISSION.md`](../../docs/ENERGY_RIGHTS_ADMISSION.md);
> remove the files if a rights holder objects.

Workbook `Weekly_Oil_Bulletin_Prices_History_maticni_4web.xlsx`, sheet
`Prices with taxes`, columns `DE_price_with_tax_euro95` and
`DE_price_with_tax_diesel`. Exact URL, retrieval second, bytes and SHA-256 are in
`sources.json`; the raw workbook is not committed (size).

| File | Content |
|---|---|
| `weekly.csv` | 449 German weekly values, bulletin dates 2018-01-01 – 2026-10-26, EUR per litre incl. taxes |
| `monthly.csv` | 106 months 2018-01 – 2026-10, two definitions (below) |
| `sources.json` | Source, rights evidence, columns, output hashes, coverage |

## Monthly definitions

| Column | Definition | Coverage 2018-01 – 2026-10 | Coverage 2021-01 – 2026-10 |
|---|---|---:|---:|
| `*_eur_per_litre` | Calendar-day weighted: each Monday value covers Monday–Sunday; a month gets a value only if every day is covered (same convention as `fuel_oil.import_energy`) | 93 / 106 | 65 / 70 |
| `*_bulletin_mean_eur_per_litre` | Plain mean of the bulletins dated in the month | 106 / 106 | 70 / 70 |

Incomplete calendar-day months (both grades, holiday weeks without a bulletin):
2018-04, 2018-12, 2019-01, 2019-04, 2019-12, 2020-01, 2020-04, 2020-12, 2021-01,
2021-04, 2021-12, 2022-01, 2022-04. The two definitions differ by at most
0.0512 EUR/l in months where both exist. The diesel count for 2018–2025 (13 of 96
incomplete) reproduces the independently documented private diesel QA.

Limits: national weighted averages reported for the bulletin date (Monday); not
daily pump prices, not E10, not regional; nominal EUR. The Commission revises the
history workbook in place; the SHA-256 pins the vintage used. Fuel prices measure
only the combustion side of running costs.

## Rebuild

```sh
python -m fuel_oil.oil_bulletin --workbook PATH/wob_history.xlsx --start 2018-01 --end 2026-10
python -m unittest tests.test_oil_bulletin
```

Verify the workbook hash against `sources.json` first.
