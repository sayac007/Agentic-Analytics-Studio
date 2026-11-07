import unittest

import numpy as np

from multibrand import bvar, data, fuel_lags, fuel_tv, study


class FuelTvTest(unittest.TestCase):
    def test_time_functions(self):
        self.assertAlmostEqual(fuel_tv.g("2021-02", "linear"), (1 - 34.5) / 12)
        self.assertAlmostEqual(fuel_tv.g("2026-09", "linear"), (68 - 34.5) / 12)
        self.assertEqual(fuel_tv.g("2023-12", "step"), 0.0)
        self.assertEqual(fuel_tv.g("2024-01", "step"), 1.0)

    def test_base_without_interaction_equals_base_model(self):
        periods = data.months("2021-01", study.END)
        _, y, x, _ = study.build(periods, study.SPECS["primary"])
        post = fuel_tv.fit(y, x, None, 1.0)
        base = bvar.fit(y, x, lam=0.2)
        np.testing.assert_allclose(post["Bn"], base["Bn"], atol=1e-12)
        fuel = fuel_lags.fuel_history(study.END)
        lag1 = fuel_lags.fit(y, fuel_lags.regressors(periods, y, x, 1, fuel), 1)
        self.assertAlmostEqual(post["logml"], lag1["logml"], places=8)

    def test_recovers_rising_coefficient(self):
        rng = np.random.default_rng(5)
        n = 2000
        gv = np.linspace(-2, 2, n)
        f = np.zeros(n)
        m = np.zeros(n)
        for t in range(1, n):
            f[t] = 0.8 * f[t - 1] + 0.1 * rng.standard_normal()
            m[t] = 0.3 * m[t - 1] + (1.0 + 0.5 * gv[t]) * f[t - 1] + 0.05 * rng.standard_normal()
        y = np.column_stack([f, m])
        x = np.ones((n, 1))
        post = fuel_tv.fit(y, x, gv, 25.0, lam=1.0)
        k = 2
        self.assertAlmostEqual(post["Bn"][0, 1], 1.0, delta=0.05)   # b0 in equation of m
        self.assertAlmostEqual(post["Bn"][k, 1], 0.5, delta=0.05)   # b1

    def test_simulate_uses_interaction(self):
        Bs = np.zeros((1, 2 + 1 + 1, 2))
        Bs[0, 2, 1] = 1.0                                          # c on equation 1
        sig = np.array([np.eye(2) * 1e-12])
        paths = fuel_tv.simulate(Bs, sig, np.array([2.0, 0.0]), np.zeros((1, 1)), [3.0],
                                 np.random.default_rng(0))
        self.assertAlmostEqual(paths[0, 0, 1], 6.0, places=4)



class FuelTvTrendTest(unittest.TestCase):
    def test_trend_main_effect_separates_trend_from_rising_coefficient(self):
        # DGP: market has a pure time trend, fuel coefficient is constant (no rise).
        from multibrand import fuel_tv_trend  # noqa: F401  (module import check)
        rng = np.random.default_rng(6)
        n = 1500
        gv = np.linspace(-2, 2, n)
        f = 0.7 + np.zeros(n)
        m = np.zeros(n)
        for t in range(1, n):
            f[t] = 0.7 + 0.8 * (f[t - 1] - 0.7) + 0.05 * rng.standard_normal()
            m[t] = 0.3 * m[t - 1] + 1.0 * f[t - 1] + 0.4 * gv[t] + 0.05 * rng.standard_normal()
        y = np.column_stack([f, m])
        x_trend = np.column_stack([np.ones(n), gv])
        with_main = fuel_tv.fit(y, x_trend, gv, 25.0, lam=1.0)
        without_main = fuel_tv.fit(y, np.ones((n, 1)), gv, 25.0, lam=1.0)
        self.assertLess(abs(with_main["Bn"][2, 1]), 0.1)           # no spurious rise
        self.assertGreater(without_main["Bn"][2, 1], 0.2)          # flawed 1.2.0 form picks up trend


if __name__ == "__main__":
    unittest.main()
