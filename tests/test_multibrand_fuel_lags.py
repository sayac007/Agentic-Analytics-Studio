import unittest

import numpy as np
from scipy.stats import multivariate_normal

from multibrand import bvar, data, fuel_lags, study


class FuelLagsTest(unittest.TestCase):
    def test_shift(self):
        self.assertEqual(fuel_lags.shift("2021-02", 4), "2020-10")
        self.assertEqual(fuel_lags.shift("2021-01", 1), "2020-12")

    def test_lag1_equals_base_model(self):
        periods = data.months("2021-01", study.END)
        _, y, x, _ = study.build(periods, study.SPECS["primary"])
        fuel = fuel_lags.fuel_history(study.END)
        post = fuel_lags.fit(y, fuel_lags.regressors(periods, y, x, 1, fuel), 1)
        base = bvar.fit(y, x, lam=0.2)
        np.testing.assert_allclose(post["Bn"], base["Bn"], atol=1e-12)
        np.testing.assert_allclose(post["Sn"], base["Sn"], atol=1e-12)

    def test_extra_lag_regressors_use_pre_sample_fuel(self):
        periods = data.months("2021-01", "2021-06")
        _, y, x, _ = study.build(periods, study.SPECS["primary"])
        fuel = fuel_lags.fuel_history("2021-06")
        Z = fuel_lags.regressors(periods, y, x, 4, fuel)
        k = y.shape[1]
        self.assertEqual(Z.shape, (5, k + 3 + x.shape[1]))
        self.assertAlmostEqual(Z[0, k + 2], fuel["2020-10"])   # row 2021-02, lag 4

    def test_marginal_likelihood_matches_numerical_integration_1d(self):
        # k = 1, one regressor (lag), compare closed form with direct evaluation
        rng = np.random.default_rng(3)
        y = np.cumsum(rng.standard_normal(30))[:, None] * 0.1
        Z = y[:-1]
        post = fuel_lags.fit(np.column_stack([y]), np.column_stack([Z]), 1, lam=0.5)
        # Monte Carlo over the prior: average of p(Y | B, sigma) under NIW prior
        s2 = bvar.ar1_variances(y)
        omega0 = 0.5 ** 2 / s2[0]
        nu0, S0 = 3, s2[0]
        draws = 200000
        sig = S0 / rng.chisquare(nu0, draws)
        B = 0.9 + np.sqrt(sig * omega0) * rng.standard_normal(draws)
        resid = y[1:, 0][None, :] - B[:, None] * Z[None, :, 0]
        loglik = -0.5 * (resid ** 2).sum(1) / sig - 0.5 * len(Z) * np.log(2 * np.pi * sig)
        mc = np.log(np.mean(np.exp(loglik - loglik.max()))) + loglik.max()
        self.assertAlmostEqual(post["logml"], mc, delta=0.1)

    def test_irf_lag1_matches_base_irf(self):
        rng = np.random.default_rng(4)
        Bs = rng.normal(0, 0.2, (5, 3 + 2, 3))
        sig = np.stack([np.eye(3) * 0.01] * 5)
        np.testing.assert_allclose(fuel_lags.irf(Bs, sig, 1, 6), bvar.irf_first_shock(Bs, sig, 6))



class FuelLagsSavedResultsTest(unittest.TestCase):
    """Checks the saved amendment run without refitting."""

    OUT = data.ROOT / "results/multibrand_fuel_lags"

    def test_hashes_report_and_base_identity(self):
        import csv
        import hashlib
        import json
        from scripts import multibrand_fuel_lags_report
        man = json.loads((self.OUT / "manifest.json").read_text())
        proto = hashlib.sha256((data.ROOT / "docs/MULTIBRAND_FUEL_LAGS_PROTOCOL.md").read_bytes()).hexdigest()
        self.assertEqual(proto, fuel_lags.PROTOCOL_SHA256)
        self.assertEqual(man["protocol_sha256"], proto)
        for name, digest in man["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((self.OUT / name).read_bytes()).hexdigest(), digest, name)
        self.assertEqual((self.OUT / "README.md").read_text(), multibrand_fuel_lags_report.build())
        # L = 1 forecasts equal the base model's primary forecasts (same seed, same first draws)
        with (self.OUT / "predictions.csv").open(newline="") as fh:
            lag1 = {(r["origin"], r["horizon"], r["outcome"]): r["prediction_median"]
                    for r in csv.DictReader(fh) if r["spec"] == "L1"}
        with (data.ROOT / "results/multibrand/predictions.csv").open(newline="") as fh:
            base = {(r["origin"], r["horizon"], r["outcome"]): r["prediction_median"]
                    for r in csv.DictReader(fh) if r["spec"] == "primary" and r["outcome"] != "VW_Group"}
        self.assertEqual(lag1, base)


if __name__ == "__main__":
    unittest.main()
