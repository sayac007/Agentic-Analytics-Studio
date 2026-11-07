import unittest

import numpy as np

from multibrand import data


class MultibrandDataTest(unittest.TestCase):
    def test_months(self):
        self.assertEqual(data.months("2025-11", "2026-02"), ("2025-11", "2025-12", "2026-01", "2026-02"))

    def test_policy_day_shares(self):
        periods = data.months("2022-12", "2026-01")
        ids, table = data.policy_table(periods)
        col = {i: table[:, j] for j, i in enumerate(ids)}
        at = {p: t for t, p in enumerate(periods)}
        self.assertEqual(col["innovation_premium"][at["2022-12"]], 1.0)
        self.assertEqual(col["innovation_premium"][at["2023-01"]], 0.0)
        self.assertAlmostEqual(col["grant_2023_private"][at["2023-12"]], 17 / 31)
        self.assertEqual(col["company_car_cap_70k"][at["2024-01"]], 1.0)
        self.assertEqual(col["tax_package_2025_07"][at["2025-06"]], 0.0)
        self.assertEqual(col["tax_package_2025_07"][at["2025-07"]], 1.0)
        self.assertEqual(col["grant_2026"][at["2026-01"]], 1.0)
        self.assertTrue((col["vehicle_tax_exemption"] == 1).all())
        self.assertEqual(col["pre_cut_2022_12"].sum(), 1.0)

    def test_real_time_masking(self):
        periods = data.months("2025-10", "2026-03")
        full = data.policy(periods)
        masked = data.policy(periods, origin="2025-12")
        j = data.POLICY.index("grant_2026")
        # announced 2026-01-19: unknown at origin 2025-12, known at origin 2026-01
        self.assertTrue((masked[:, j] == 0).all())
        self.assertEqual(data.policy(periods, origin="2026-01")[periods.index("2026-02"), j], 1.0)
        k = data.POLICY.index("tax_package_2025_07")
        np.testing.assert_array_equal(masked[:, k], full[:, k])
        with self.assertRaises(ValueError):
            data.policy(periods, origin="2023-11")

    def test_design_complete_and_accounting(self):
        periods = data.months("2021-01", "2026-09")
        counts, y, x = data.design(periods)
        self.assertEqual(y.shape, (69, len(data.ENDOGENOUS)))
        self.assertEqual(x.shape, (69, len(data.EXOGENOUS)))
        self.assertFalse(np.isnan(y).any() or np.isnan(x).any())
        for r in counts:
            self.assertEqual(sum(r[g] for g in data.GROUPS) + r["Rest"], r["market"])
        self.assertEqual(counts[-1]["Tesla"], 12552)
        self.assertEqual(counts[-1]["market"], 88599)

    def test_october_prices_missing_not_filled(self):
        self.assertTrue(np.isnan(data.prices(("2026-10",))).all())


if __name__ == "__main__":
    unittest.main()
