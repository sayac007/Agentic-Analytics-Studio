"""Synthetic-only software checks: no empirical relationships or private values."""

import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

from attention.econometrics import (
    PROTOCOL,
    ROOT,
    admit,
    analyze,
    fit,
    join_months,
    lagged,
    pseudo_holdout,
    series_diagnostics,
)
from attention.import_trends import sha

spec = importlib.util.spec_from_file_location(
    "econometric_fixture", ROOT / "tests/fixtures/econometrics/generate.py"
)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class EconometricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.paths = helper.generate(cls.root / "fixture")
        cls.rows, cls.provenance = admit(*cls.paths, fixture=True)
        cls.pp, cls.y, cls.x = join_months(cls.rows, cls.paths[-1], fixture=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_exact_join_units_and_provenance(self):
        self.assertEqual(len(self.pp), 96)
        self.assertEqual(self.pp[0], "2018-01")
        self.assertEqual(self.pp[-1], "2025-12")
        self.assertEqual(self.provenance["label"], "SYNTHETIC_FIXTURE_ONLY")
        self.assertEqual(self.provenance["protocol_sha256"], sha(PROTOCOL.read_bytes()))

    def test_missing_duplicate_partial_censored_and_order_rejected(self):
        for mode in (
            "missing",
            "duplicate",
            "order",
            "partial",
            "censored",
            "nonfinite",
        ):
            rows = [r.copy() for r in self.rows]
            if mode == "missing":
                rows = [r for r in rows if r["period"] != "2020-01"]
            if mode == "duplicate":
                rows.append(rows[0].copy())
            if mode == "order":
                rows[170], rows[171] = rows[171], rows[170]
            if mode in ("partial", "censored", "nonfinite"):
                r = next(r for r in rows if r["period"] == "2020-01")
                if mode == "partial":
                    r["period_completeness"] = "partial_or_unverified_period"
                if mode == "censored":
                    r["value_status"] = "censored_below_one"
                    r["search_interest_index"] = None
                if mode == "nonfinite":
                    r["search_interest_index"] = float("nan")
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                join_months(rows, self.paths[-1], True)

    def test_kba_missing_and_wrong_fixture_class_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "kba.csv"
            text = self.paths[-1].read_text()
            for modified in (
                text.replace("synthetic_fixture", "unverified"),
                "\n".join(text.splitlines()[:-1]) + "\n",
            ):
                p.write_text(modified)
                with self.assertRaises(ValueError):
                    join_months(self.rows, p, True)

    def test_lag_direction_no_future_wraparound(self):
        v = np.array([10.0, 20.0, 30.0, 40.0])
        out = lagged(v, 2)
        self.assertTrue(np.isnan(out[:2]).all())
        np.testing.assert_array_equal(out[2:], [10, 20])
        np.testing.assert_array_equal(lagged(v, 0), v)
        with self.assertRaises(ValueError):
            lagged(v, -1)

    def test_ols_hac_against_small_manual_example(self):
        x = np.column_stack([np.ones(8), np.arange(8)])
        y = np.array([1.0, 3.0, 2.0, 5.0, 4.0, 8.0, 6.0, 9.0])
        beta, r = fit(y, x)
        expected = np.array([1.0833333333333333, 1.0476190476190477])
        # Verify the hand-computable normal-equation solution, then score sandwich.
        np.testing.assert_allclose(beta, np.linalg.solve(x.T @ x, x.T @ y), atol=1e-12)
        e = y - x @ beta
        score = x * e[:, None]
        meat = score.T @ score
        for lag in range(1, 4):
            cross = score[lag:].T @ score[:-lag]
            meat += (1 - lag / 4) * (cross + cross.T)
        inv = np.linalg.inv(x.T @ x)
        cov = inv @ meat @ inv * (8 / 6)
        np.testing.assert_allclose(r.cov_params(), cov, rtol=1e-10)
        np.testing.assert_allclose(beta, expected, atol=1e-12)
        with self.assertRaises(ValueError):
            fit(y, np.ones((8, 2)))

    def test_train_holdout_and_scaler_do_not_use_holdout_values(self):
        first = pseudo_holdout(self.pp, self.y, self.x)
        y = self.y.copy()
        x = self.x.copy()
        y[-12:] += 50000
        x[-12:] += 10000
        other = pseudo_holdout(self.pp, y, x)
        self.assertEqual(first["attention_training_mean"], float(self.x[:-12].mean()))
        self.assertEqual(
            first["attention_training_mean"], other["attention_training_mean"]
        )
        self.assertEqual(first["attention_training_sd"], other["attention_training_sd"])
        self.assertEqual(len(first["training_periods"]), 81)
        self.assertEqual(first["holdout_periods"][0], "2025-01")
        for name in first["models"]:
            self.assertEqual(
                first["models"][name]["coefficients"],
                other["models"][name]["coefficients"],
            )
        yonly = pseudo_holdout(self.pp, y, self.x)
        for name in first["models"]:
            self.assertEqual(
                first["models"][name]["predictions"],
                yonly["models"][name]["predictions"],
            )

    def test_reproducible_diagnostics_and_acf_arithmetic(self):
        v = np.array([np.sin(i * 0.7) + 0.1 * i for i in range(60)])
        a = series_diagnostics(v, True)
        self.assertEqual(a, series_diagnostics(v, True))
        z = v - v.mean()
        self.assertAlmostEqual(a["acf"][1], float(z[1:] @ z[:-1] / (z @ z)))
        self.assertEqual(a["adf"]["lags"], 3)
        self.assertEqual(a["kpss"]["lags"], 3)
        self.assertEqual(a["deterministic"], "ct")
        self.assertEqual(a["adf"]["null"], "unit root")
        self.assertEqual(len(a["acf_ci"]), 13)

    def test_fixed_association_family_and_window_sizes(self):
        result = analyze(self.pp, self.y, self.x, "SYNTHETIC_FIXTURE_ONLY")
        self.assertEqual(len(result["associations"]), 14)
        self.assertEqual({r["n"] for r in result["associations"]}, {89, 53})
        for r in result["associations"]:
            self.assertGreaterEqual(r["p_holm_14"] + 1e-15, r["p_raw"])
            self.assertLessEqual(r["ci95"][0], r["estimate"])
            self.assertGreaterEqual(r["ci95"][1], r["estimate"])
        self.assertEqual(
            len(
                result["windows"]["2021-01_2025-12"]["pseudo_holdout"][
                    "training_periods"
                ]
            ),
            45,
        )
        self.assertFalse(result["causal_interpretation"])

    def test_pending_admission_hash_and_derived_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = list(helper.generate(Path(tmp) / "fixture"))
            a = paths[3]
            record = json.loads(a.read_text())
            record["status"] = "pending"
            a.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "Pending"):
                admit(*paths, True)
            record["status"] = "synthetic_fixture_only"
            record["raw_sha256"] = "0" * 64
            a.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "hash"):
                admit(*paths, True)
            record["raw_sha256"] = sha(paths[0].read_bytes())
            a.write_text(json.dumps(record))
            coverage = json.loads((paths[2] / "coverage.json").read_text())
            name = coverage["outputs"]["analysis_2018_2025"]["file"]
            (paths[2] / name).write_text("tampered")
            with self.assertRaisesRegex(ValueError, "Tampered"):
                admit(*paths, True)

    def test_unknown_retrieval_fails_before_kba_read_or_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "meta.json"
            m = json.loads(self.paths[1].read_text())
            m["retrieved_at"] = None
            p.write_text(json.dumps(m))
            with self.assertRaisesRegex(ValueError, "Timestamp"):
                admit(
                    self.paths[0],
                    p,
                    self.paths[2],
                    Path(tmp) / "absent_admission",
                    Path(tmp) / "absent_kba",
                    True,
                )
        with self.assertRaises(ValueError):
            admit(*self.paths, fixture=False)

    def test_missing_numerical_dependency_is_not_a_successful_fit(self):
        with mock.patch.dict(sys.modules, {"statsmodels.api": None}):
            with self.assertRaises(ImportError):
                fit(np.arange(8.0), np.column_stack([np.ones(8), np.arange(8)]))

    def test_cli_fixture_artifacts_replay_and_private_output_isolation(self):
        args = [sys.executable, "-m", "attention.econometrics"]
        for key, p in zip(
            ("raw", "metadata", "import-dir", "admission", "kba"), self.paths
        ):
            args += ["--" + key, str(p)]
        with tempfile.TemporaryDirectory() as tmp:
            outputs = []
            for i in range(2):
                out = Path(tmp) / str(i)
                run = subprocess.run(
                    args + ["--output-dir", str(out), "--fixture"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                outputs.append(out)
                result = json.loads((out / "diagnostics.json").read_text())
                self.assertEqual(result["label"], "SYNTHETIC_FIXTURE_ONLY")
                self.assertIn("SYNTHETIC_FIXTURE_ONLY", (out / "report.md").read_text())
                self.assertEqual(len(list(out.glob("*.png"))), 6)
                for name, digest in json.loads(
                    (out / "inventory.json").read_text()
                ).items():
                    self.assertEqual(sha((out / name).read_bytes()), digest)
                with (out / "associations.csv").open() as f:
                    self.assertEqual(len(list(csv.DictReader(f))), 14)
            self.assertEqual(
                (outputs[0] / "diagnostics.json").read_bytes(),
                (outputs[1] / "diagnostics.json").read_bytes(),
            )
            forbidden = ROOT / "artifacts/forbidden-econometric-output"
            run = subprocess.run(
                args + ["--output-dir", str(forbidden), "--fixture"],
                cwd=ROOT,
                capture_output=True,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(forbidden.exists())
