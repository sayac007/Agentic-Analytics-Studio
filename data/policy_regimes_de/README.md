# German BEV incentive programmes as monthly indicators (2021-01 – 2026-10)

`chronology.json` lists every federal purchase and tax incentive for new BEVs that
was in force during the sample, with legal validity dates, the date from which
it was publicly known (`known_by`, used for real-time forecasting) and sources.
`monthly.csv` is generated from it by `multibrand.data.policy_table`.

**Coding:** share of calendar days in the month on which the rule applied
(1 = whole month, 0 = not in force). This equals an ordinary 0/1 dummy except in
December 2023, when the Umweltbonus ended on the 17th (17/31 = 0.5484).

| Column | Programme | Valid | Used in the BVARX |
|---|---|---|---|
| `innovation_premium` | Umweltbonus with doubled federal share, all buyers | 2020-07-08 – 2022-12-31 | yes |
| `grant_2023_all` | Umweltbonus reduced rates, private and business | 2023-01-01 – 2023-08-31 | yes |
| `grant_2023_private` | Umweltbonus reduced rates, private persons only | 2023-09-01 – 2023-12-17 | yes |
| `grant_2026` | E-Auto-Förderprogramm 2026, income-dependent | from 2026-01-01 (announced 2026-01-19, portal 2026-05-19) | yes |
| `company_car_cap_70k` | Company-car 0.25 % rule, cap 60k → 70k EUR | 2024-01-01 – 2025-06-30 | no: coincides with the end of the Umweltbonus, absorbed in the baseline |
| `tax_package_2025_07` | Company-car cap 100k EUR **and** 75 % special depreciation for business EVs | from 2025-07-01 | yes (both start the same day, one indicator) |
| `vehicle_tax_exemption` | Motor-vehicle tax exemption § 3d KraftStG | whole sample | no: constant |
| `company_car_quarter_rule` | Company-car 0.25 % rule (base) | whole sample | no: constant |
| `pre_cut_2022_12` | Last month before the announced 2023 cut | 2022-12 | yes (pulse) |
| `pre_business_end_2023_08` | Last month before businesses lost eligibility | 2023-08 | yes (pulse) |

Baseline (all estimable indicators 0): January 2024 – June 2025, i.e. no purchase
grant and the 70k company-car cap. Coefficients are therefore differences to that
baseline. They are **conditional associations**, not causal programme effects:
the programmes coincide with the energy-price shock, model launches and Tesla's
2025 share loss.

Sources: legal texts (§ 6, § 7 EStG, § 3d KraftStG, current consolidated versions),
BAFA and BMUV announcements (hashed in `data/task04_regimes/policy_chronology.json`),
the German Wikipedia article *Umweltbonus* (revision 270724749) and three tax-adviser
summaries for the historical company-car caps. The historical caps (60k, 70k) and
the exact promulgation dates of the 2024 and 2025 tax laws were **not** read in the
Federal Law Gazette; `known_by` for the 2025 package is set conservatively to
2025-07-31.
