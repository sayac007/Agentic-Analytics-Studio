import unittest

import numpy as np

from multibrand import bvar


class BvarRecoveryTest(unittest.TestCase):
    """Synthetic recovery only; says nothing about the real data."""

    def setUp(self):
        rng = np.random.default_rng(1)
        self.A = np.array([[0.7, 0.0], [0.3, 0.5]])  # y_t = A y_{t-1} + ...
        self.c = np.array([[1.0, -0.5], [0.0, 2.0]])  # rows: const, dummy
        n = 3000
        x = np.column_stack([np.ones(n), (rng.random(n) < 0.3).astype(float)])
        self.Sigma = np.array([[0.04, 0.01], [0.01, 0.09]])
        L = np.linalg.cholesky(self.Sigma)
        y = np.zeros((n, 2))
        for t in range(1, n):
            y[t] = self.A @ y[t - 1] + self.c.T @ x[t] + L @ rng.standard_normal(2)
        self.y, self.x = y, x

    def test_posterior_mean_recovers_coefficients(self):
        post = bvar.fit(self.y, self.x, lam=0.2)
        # With n = 3000 the prior is negligible: posterior mean ~ OLS
        Z = np.column_stack([self.y[:-1], self.x[1:]])
        ols = np.linalg.lstsq(Z, self.y[1:], rcond=None)[0]
        np.testing.assert_allclose(post["Bn"], ols, atol=0.01)
        np.testing.assert_allclose(post["Bn"][:2, :].T, self.A, atol=0.05)
        np.testing.assert_allclose(post["Bn"][3, :], self.c[1], atol=0.05)  # dummy effects
        # intercepts are strongly correlated with lag coefficients in a persistent process
        np.testing.assert_allclose(post["Bn"][2, :], self.c[0], atol=0.15)
        sigma_mean = post["Sn"] / (post["nun"] - 2 - 1)
        np.testing.assert_allclose(sigma_mean, self.Sigma, atol=0.01)

    def test_draws_irf_and_simulation_shapes(self):
        post = bvar.fit(self.y[:400], self.x[:400])
        rng = np.random.default_rng(2)
        Bs, sig = bvar.draw(post, 200, rng)
        self.assertEqual(Bs.shape, (200, 4, 2))
        irf = bvar.irf_first_shock(Bs, sig, 6)
        self.assertEqual(irf.shape, (200, 7, 2))
        # impact of shock 0 on variable 0 equals its Cholesky SD (positive)
        self.assertTrue((irf[:, 0, 0] > 0).all())
        np.testing.assert_allclose(np.median(irf[:, 0, 0]), np.sqrt(self.Sigma[0, 0]), atol=0.02)
        paths = bvar.simulate(Bs, sig, self.y[399], self.x[400:403], rng)
        self.assertEqual(paths.shape, (200, 3, 2))

    def test_rejects_missing_values(self):
        x = self.x[:50].copy()
        x[10, 1] = np.nan
        with self.assertRaises(ValueError):
            bvar.fit(self.y[:50], x)


if __name__ == "__main__":
    unittest.main()
