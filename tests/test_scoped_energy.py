"""Offline synthetic software checks; no real study inputs in CI."""

import copy
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import statsmodels.api as sm
from fuel_oil import scoped_study as s

GEN = Path(__file__).resolve().parent / "fixtures/scoped_energy/generate.py"


class ScopedEnergyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = runpy.run_path(str(GEN))["generate"](self.root / "fixture")
        self.energy = self.fixture / "energy"
        self.permits = self.fixture / "permits"
        self.kba = self.fixture / "SYNTHETIC_kba.csv"

    def json(self, path):
        return json.loads(path.read_text())

    def write(self, path, value):
        path.write_bytes(s.encoded(value))

    def inputs(self):
        return s.load_aligned(self.energy, self.kba)

    def test_protocol_first_commit_and_authorization_are_frozen(self):
        s.freeze_gate()
        self.assertEqual(s.sha(s.PROTOCOL.read_bytes()), s.PROTOCOL_SHA)
        with patch.object(s, "PROTOCOL_SHA", "0" * 64), self.assertRaises(ValueError):
            s.gate(self.energy, self.permits, self.kba, True)

    def test_admission_key_unit_scope_and_brent_refusal_before_outcomes(self):
        path = self.permits / "eurusd.admission.json"
        original = self.json(path)
        for key, value in [
            ("series_id", "RBRTE"),
            ("unit", "EUR_per_USD"),
            ("scope", "private_retrospective_only"),
        ]:
            self.write(path, dict(original, **{key: value}))
            with (
                patch.object(
                    s, "load_aligned", side_effect=AssertionError("outcomes touched")
                ),
                self.assertRaises(ValueError),
            ):
                s.run(
                    self.energy,
                    self.permits,
                    self.kba,
                    self.root / "must-not-exist",
                    True,
                )
            self.assertFalse((self.root / "must-not-exist").exists())
        self.write(path, original)
        manifest = self.json(self.energy / "fixture_manifest.json")
        manifest["sources"]["brent_usd"] = {}
        self.write(self.energy / "fixture_manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "Brent"):
            s.gate(self.energy, self.permits, self.kba, True)

    def test_hash_mismatch_and_fixture_real_mixing_fail(self):
        path = self.energy / "eurusd.quarantined.json"
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "hash"):
            s.gate(self.energy, self.permits, self.kba, True)
        with self.assertRaises((ValueError, OSError)):
            s.gate(self.energy, self.permits, self.kba, False)

    def test_valid_fixture_gate_provenance_and_no_brent_source(self):
        proof = s.gate(self.energy, self.permits, self.kba, True)
        self.assertEqual(set(proof["sources"]), {"eurusd", "diesel_de"})
        self.assertEqual(proof["scope"], "SYNTHETIC_FIXTURE_ONLY")
        self.assertFalse(proof["task_01j_executed"])

    def test_exact_month_join_units_duplicates_and_outside_window_exclusion(self):
        y, energy = self.inputs()
        self.assertEqual(y.shape, (96,))
        self.assertEqual(np.isfinite(energy["diesel_de"]).sum(), 83)
        path = self.energy / "eurusd.quarantined.json"
        original = self.json(path)
        bad = copy.deepcopy(original)
        bad["observations"].append(bad["observations"][0])
        self.write(path, bad)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.inputs()
        bad = copy.deepcopy(original)
        bad["observations"][0]["unit"] = "EUR_per_USD"
        self.write(path, bad)
        with self.assertRaisesRegex(ValueError, "unit"):
            self.inputs()
        # Later raw rows are not analyzed or converted into 2026 outcomes.
        extended = copy.deepcopy(original)
        extended["observations"].append(
            dict(extended["observations"][-1], period="2026-01", value=999999)
        )
        self.write(path, extended)
        with self.kba.open("a") as f:
            f.write(
                "2026-01,NOT_A_MODELING_VALUE,brand:TESLA,SYNTHETIC,SYNTHETIC,all\n"
            )
        yy, xx = self.inputs()
        np.testing.assert_array_equal(y, yy)
        np.testing.assert_array_equal(energy["eurusd"], xx["eurusd"])

    def test_gap_filling_or_unexpected_missing_value_refused(self):
        path = self.energy / "diesel_de.monthly_approx.quarantined.json"
        original = self.json(path)
        for p in ["2022-01", "2022-04", "2025-01"]:
            changed = copy.deepcopy(original)
            row = next(r for r in changed["observations"] if r["period"] == p)
            row["value"] = 1.2 if row["value"] is None else None
            self.write(path, changed)
            with self.assertRaisesRegex(ValueError, "missingness"):
                self.inputs()

    def test_lag_direction_and_missingness_are_calendar_based(self):
        values = np.arange(96, dtype=float)
        lag = s.lagged(values, 2)
        self.assertTrue(np.isnan(lag[:2]).all())
        np.testing.assert_array_equal(lag[2:], values[:-2])
        _, energy = self.inputs()
        diff = s.difference(energy["diesel_de"])
        for p in ["2022-01", "2022-02", "2022-04", "2022-05"]:
            self.assertTrue(np.isnan(diff[s.PERIODS.index(p)]))
        self.assertTrue(np.isnan(s.lagged(diff, 2)[s.PERIODS.index("2022-06")]))
        with self.assertRaises(ValueError):
            s.lagged(values, 7)

    def test_ols_hand_example_and_hac_shape(self):
        xx = np.column_stack([np.ones(5), np.arange(-2, 3)])
        yy = np.array([1, 2, 2, 4, 6])
        fit = s.fit_hac(yy, xx, np.arange(5), min_df=0)
        np.testing.assert_allclose(fit["coefficients"], [3, 1.2])
        self.assertEqual(fit["covariance"].shape, (2, 2))
        self.assertTrue(np.isfinite(fit["se"]).all())

    def test_contiguous_hac_matches_statsmodels_reference(self):
        rng = np.random.default_rng(13)
        x = np.column_stack([np.ones(80), np.linspace(0, 2, 80)])
        y = x @ np.array([3.0, 2.0]) + rng.normal(size=80)
        actual = s.fit_hac(y, x, np.arange(80))
        ref = sm.OLS(y, x).fit(
            cov_type="HAC", cov_kwds={"maxlags": 3, "use_correction": True}, use_t=False
        )
        np.testing.assert_allclose(actual["coefficients"], ref.params, rtol=1e-11)
        np.testing.assert_allclose(
            actual["covariance"], ref.cov_params(), rtol=1e-10, atol=1e-12
        )

    def test_gapped_hac_manual_score_pairs_do_not_compress_calendar(self):
        idx = np.array([0, 1, 4, 5, 9, 10])
        y = np.array([1.0, 2.0, 3.0, 2.0, 0.0, 4.0])
        x = np.ones((6, 1))
        residual = y - y.mean()
        meat = float(residual @ residual)
        for h in [1, 2, 3]:
            for i, t in enumerate(idx):
                for j, u in enumerate(idx):
                    if t - u == h:
                        meat += 2 * (1 - h / 4) * residual[i] * residual[j]
        expected = meat / 36 * 6 / 5
        fit = s.fit_hac(y, x, idx, min_df=0)
        self.assertAlmostEqual(fit["covariance"][0, 0], expected)
        compressed = s.fit_hac(y, x, np.arange(6), min_df=0)
        self.assertNotAlmostEqual(
            fit["covariance"][0, 0], compressed["covariance"][0, 0]
        )

    def test_invalid_fits_rank_df_nonfinite_and_calendar_order(self):
        for y, x, idx in [
            (np.ones(25), np.ones((25, 2)), np.arange(25)),
            (np.ones(5), np.ones((5, 1)), np.arange(5)),
            (np.r_[np.nan, np.ones(29)], np.ones((30, 1)), np.arange(30)),
            (np.arange(30.0), np.ones((30, 1)), np.arange(30)[::-1]),
        ]:
            with self.assertRaises(ValueError):
                s.fit_hac(y, x, idx)

    def test_diagnostics_use_contiguous_segment_and_do_not_change_lags(self):
        _, energy = self.inputs()
        v = energy["diesel_de"]
        seg = s.contiguous_segment(v)
        self.assertEqual(s.PERIODS[seg[0]], "2022-05")
        self.assertEqual(len(seg), 44)
        d = s.diagnostics(v, True)
        self.assertEqual(d["deterministic"], "ct")
        self.assertEqual(d["adf"]["lags"], 3)
        self.assertEqual(d["kpss"]["lags"], 3)
        self.assertEqual(len(d["acf"]), 13)
        self.assertEqual(s.diagnostics(np.ones(96), True)["status"], "not_estimable")
        self.assertEqual(
            s.diagnostics(np.arange(26.0), False)["status"], "not_estimable"
        )
        np.testing.assert_array_equal(
            s.contiguous_segment(np.array([1.0, 2.0, np.nan, 3.0, 4.0])), [0, 1]
        )

    def test_fixed_family_samples_and_original_trend(self):
        y, energy = self.inputs()
        result = s.analyze(y, energy)
        self.assertEqual(len(result["associations"]), 28)
        n = {
            (r["source"], r["transformation"], r["lag"]): r["n"]
            for r in result["associations"]
        }
        self.assertEqual(n[("eurusd", "differences", 0)], 95)
        self.assertEqual(n[("eurusd", "differences", 6)], 89)
        self.assertEqual(n[("diesel_de", "levels", 0)], 83)
        self.assertEqual(n[("diesel_de", "differences", 0)], 73)
        self.assertEqual(s.controls(["2018-01", "2018-04"])[1, 1], 3)
        for r in result["associations"]:
            if r["status"] == "estimated":
                self.assertGreaterEqual(
                    r["holm_pvalue_28_tests"] + 1e-14, r["raw_pvalue"]
                )

    def test_holdout_outcomes_never_change_training_coefficients(self):
        y, energy = self.inputs()
        first = s.holdout(y, energy["eurusd"])
        y[84:] += 10000
        second = s.holdout(y, energy["eurusd"])
        self.assertEqual(first["holdout_periods"], s.PERIODS[84:])
        for name in first["models"]:
            np.testing.assert_array_equal(
                first["models"][name]["fit"]["coefficients"],
                second["models"][name]["fit"]["coefficients"],
            )
            np.testing.assert_array_equal(
                first["models"][name]["predicted_counts"],
                second["models"][name]["predicted_counts"],
            )
            self.assertNotEqual(
                first["models"][name]["rmse_counts"],
                second["models"][name]["rmse_counts"],
            )
        energy["eurusd"][90] = np.nan
        self.assertEqual(s.holdout(y, energy["eurusd"])["status"], "not_estimable")

    def test_private_output_refusal_happens_before_any_read(self):
        for out in [s.ROOT / "artifacts/forbidden-study", self.fixture]:
            with (
                patch.object(s, "gate", side_effect=AssertionError("gate touched")),
                self.assertRaises(ValueError),
            ):
                s.run(self.energy, self.permits, self.kba, out, True)

    def test_deterministic_end_to_end_cli_quiet_and_private_only(self):
        one = self.root / "one"
        two = self.root / "two"
        s.run(self.energy, self.permits, self.kba, one, True)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "fuel_oil.scoped_study",
                "--fixture",
                "--energy-dir",
                str(self.energy),
                "--permits-dir",
                str(self.permits),
                "--kba",
                str(self.kba),
                "--output",
                str(two),
            ],
            cwd=s.ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)
        self.assertNotIn("coefficient", result.stdout + result.stderr)
        manifest = self.json(one / "manifest.json")
        self.assertTrue(manifest["completed"])
        self.assertFalse(manifest["public_results_allowed"])
        self.assertEqual(manifest["scope"], "SYNTHETIC_FIXTURE_ONLY")
        for name, h in manifest["file_hashes"].items():
            self.assertEqual(s.sha((one / name).read_bytes()), h)
            self.assertEqual((one / name).read_bytes(), (two / name).read_bytes(), name)
        self.assertEqual(
            (one / "manifest.json").read_bytes(), (two / "manifest.json").read_bytes()
        )
        proof = self.json(one / "provenance.json")
        self.assertEqual(set(proof["sources"]), {"eurusd", "diesel_de"})
        self.assertNotIn(str(self.root), json.dumps(proof))


if __name__ == "__main__":
    unittest.main()
