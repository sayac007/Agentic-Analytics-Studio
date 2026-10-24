"""Offline macro contracts: genuine missingness, provenance, frequency and arithmetic."""

import copy
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from macro_controls import pipeline as m

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/macro"


class MacroControlsTests(unittest.TestCase):
    def setUp(self):
        self.catalog = m.validate_catalog(
            json.loads((FIX / "sources.json").read_text())
        )

    def inputs(self, name="monthly_rate"):
        s = copy.deepcopy(next(s for s in self.catalog["series"] if s["id"] == name))
        return (
            (FIX / (name + ".csv")).read_bytes(),
            s,
            json.loads((FIX / (name + ".provenance.json")).read_text()),
        )

    def rows(self, name="monthly_rate"):
        return m.normalize(*self.inputs(name), fixture=True)

    def changed(self, column, value, name="monthly_rate"):
        raw, s, p = self.inputs(name)
        reader = csv.DictReader(io.StringIO(raw.decode()))
        fields = reader.fieldnames
        rows = list(reader)
        rows[0][column] = value
        out = io.StringIO(newline="")
        w = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        raw = out.getvalue().encode()
        p["raw_sha256"] = m.digest(raw)
        return raw, s, p

    def test_fixture_native_units_and_missingness(self):
        rows = self.rows()
        self.assertEqual([r["value"] for r in rows], [2, None, 3])
        self.assertEqual(rows[1]["quality_status"], "missing")
        self.assertEqual(rows[2]["quality_status"], "provisional")
        self.assertEqual(rows[0]["unit"], "PC")
        self.assertEqual(len(m.monthly_rows(rows)), 3)  # March never fabricated.
        self.assertEqual(rows[0]["historical_as_of"], "not_established")

    def test_frequency_country_unit_id_drift(self):
        for col, val in [
            ("FREQ", "Q"),
            ("REF_AREA", "U2"),
            ("UNIT", "basis_points"),
            ("KEY", "OTHER"),
        ]:
            with self.subTest(col=col), self.assertRaisesRegex(ValueError, "drift"):
                m.normalize(*self.changed(col, val), fixture=True)

    def test_periods_and_calendar_dates(self):
        for p, freq in [
            ("2020-13", "M"),
            ("2020-00", "M"),
            ("2020-1", "M"),
            ("2020-01\n", "M"),
            ("2020-Q5", "Q"),
            ("2019-02-29", "D"),
            ("../2020-01", "M"),
            ("2020-01-01", "E"),
        ]:
            with self.subTest(p=p), self.assertRaises(ValueError):
                m.period(p, freq)
        self.assertEqual(m.period("2020-02-29", "D"), "2020-02-29")
        self.assertEqual(len(m.months("2018-01", "2025-12")), 96)

    def test_bad_numeric_and_empty_field_fail(self):
        for v in ("", "nan", "NaN", "inf", "1e999", "1,2", " 2", "--", "<1"):
            with self.subTest(v=v), self.assertRaises(ValueError):
                m.normalize(*self.changed("OBS_VALUE", v), fixture=True)

    def test_missing_flag_consistency_and_unknown_status(self):
        for v in ("M", "X", ""):
            with self.subTest(v=v), self.assertRaises(ValueError):
                m.normalize(*self.changed("OBS_STATUS", v), fixture=True)

    def test_duplicate_and_revision_fail_no_selection(self):
        raw, s, p = self.inputs()
        for revised in (
            raw.splitlines()[1],
            raw.splitlines()[1].replace(b",2,A", b",9,P"),
        ):
            changed = raw + revised + b"\n"
            p["raw_sha256"] = m.digest(changed)
            with self.assertRaisesRegex(ValueError, "Duplicate/revised"):
                m.normalize(changed, s, p, fixture=True)

    def test_hash_provenance_and_retrieval_fail_closed(self):
        raw, s, p = self.inputs()
        for key, val in [
            ("raw_sha256", "0" * 64),
            ("source_url", "https://other.example/"),
            ("retrieved_at", "2020-01-01"),
            ("retrieved_at", "2020-01-01T00:00:00"),
            ("release_or_vintage", ""),
        ]:
            bad = dict(p, **{key: val})
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.normalize(raw, s, bad, fixture=True)
        with self.assertRaises(ValueError):
            m.normalize(raw + b"\n", s, p, fixture=True)

    def test_no_fixture_in_production_or_real_in_fixture(self):
        with self.assertRaises(ValueError):
            m.normalize(*self.inputs())
        raw, s, p = self.inputs()
        s["metadata_status"] = "verified"
        with self.assertRaises(ValueError):
            m.normalize(raw, s, p, fixture=True)

    def test_catalog_identity_provenance_and_unknown_scope(self):
        for mutate in [
            lambda c: c.update(scope="observed"),
            lambda c: c["series"].append(c["series"][0]),
            lambda c: c["series"][0].update(source_url="http://example.org"),
            lambda c: c["series"][0].update(evidence=[]),
            lambda c: c["series"][0].update(frequency="E"),
        ]:
            bad = copy.deepcopy(self.catalog)
            mutate(bad)
            with self.assertRaises(ValueError):
                m.validate_catalog(bad)

    def test_production_blocked_no_network(self):
        c = m.validate_catalog(json.loads((m.DATA / "sources.json").read_text()))
        with patch(
            "urllib.request.build_opener",
            side_effect=AssertionError("network forbidden"),
        ):
            for s in c["series"]:
                with self.assertRaises(ValueError):
                    m.download(s, Path("not-created.csv"))
        self.assertFalse(Path("not-created.csv").exists())

    def test_quarterly_not_monthly_available_in_adapter(self):
        rows = self.rows("quarterly_earnings")
        self.assertEqual(
            [r["observation_period"] for r in rows], ["2020-Q1", "2020-Q2"]
        )
        self.assertEqual(m.monthly_rows(rows), [])
        with self.assertRaises(ValueError):
            m.cpi_yoy(rows)
        # This proves adapter policy, NOT absence of a real monthly Destatis series.

    def test_daily_leap_year_mean_exact(self):
        rows = self.rows("daily_policy")
        mean = m.daily_monthly_mean(rows)[0]
        self.assertAlmostEqual(mean["value"], (14 + 15 * 3) / 29)
        self.assertEqual(mean["quality_status"], "derived_complete")
        self.assertEqual(mean["frequency"], "M")
        self.assertEqual(mean["raw_sha256"], rows[0]["raw_sha256"])

    def test_daily_incomplete_or_missing_not_filled(self):
        rows = self.rows("daily_policy")
        for subset in (
            rows[:-1],
            rows[1:],
            [dict(r, value=None) if i == 14 else r for i, r in enumerate(rows)],
        ):
            out = m.daily_monthly_mean(subset)[0]
            self.assertIsNone(out["value"])
            self.assertEqual(out["quality_status"], "incomplete_daily_coverage")
        # Two change-event rows must NOT become a complete daily/monthly rate.
        self.assertIsNone(m.daily_monthly_mean([rows[0], rows[-1]])[0]["value"])
        with self.assertRaises(ValueError):
            m.daily_monthly_mean(self.rows())

    def test_daily_duplicates_mixed_vintage_nonfinite_rejected(self):
        rows = self.rows("daily_policy")
        for bad in (
            rows + [rows[0]],
            [rows[0], dict(rows[1], unit="BP")],
            [rows[0], dict(rows[1], raw_sha256="0" * 64)],
            [dict(rows[0], value=float("nan"))],
        ):
            with self.assertRaises(ValueError):
                m.daily_monthly_mean(bad)

    def test_cpi_yoy_calendar_not_row_lag(self):
        rows = self.rows("cpi")
        yoy = {r["observation_period"]: r for r in m.cpi_yoy(rows)}
        self.assertAlmostEqual(yoy["2020-01"]["value"], 10)
        self.assertAlmostEqual(yoy["2020-03"]["value"], 10)
        self.assertIsNone(yoy["2020-02"]["value"])
        self.assertEqual(yoy["2020-01"]["unit"], "percent_yoy")
        self.assertEqual(yoy["2020-01"]["input_periods"], ["2019-01", "2020-01"])

    def test_cpi_no_cross_base_revision_zero_or_missing(self):
        rows = self.rows("cpi")
        for bad in (
            rows + [rows[0]],
            [rows[0], dict(rows[-1], unit="index_2015_100")],
            [dict(rows[0], value=0)],
            [dict(rows[0], value=float("inf"))],
        ):
            with self.assertRaises(ValueError):
                m.cpi_yoy(bad)
        rows[0]["value"] = None
        self.assertIsNone(m.cpi_yoy(rows)[2]["value"])

    def test_blocked_coverage_real_counts_not_synthetic(self):
        c = json.loads((m.DATA / "sources.json").read_text())
        report = m.coverage(c)
        self.assertEqual(m.encode(report), (m.DATA / "coverage.json").read_bytes())
        for s in report["series"]:
            self.assertEqual([w["expected_months"] for w in s["windows"]], [96, 60])
            self.assertEqual(
                [w["verified_monthly_observations"] for w in s["windows"]], [0, 0]
            )
        with self.assertRaises(ValueError):
            m.coverage(self.catalog)

    def test_cli_deterministic_and_failures_create_no_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            args = [
                sys.executable,
                "-m",
                "macro_controls.pipeline",
                "--fixture",
                "--catalog",
                str(FIX / "sources.json"),
                "--series",
                "monthly_rate",
                "--raw",
                str(FIX / "monthly_rate.csv"),
                "--provenance",
                str(FIX / "monthly_rate.provenance.json"),
                "--output",
                str(out),
            ]
            first = subprocess.run(args, cwd=ROOT, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_bytes = out.read_bytes()
            self.assertNotEqual(
                subprocess.run(args, cwd=ROOT, capture_output=True).returncode, 0
            )
            out.unlink()
            self.assertEqual(
                subprocess.run(args, cwd=ROOT, capture_output=True).returncode, 0
            )
            self.assertEqual(out.read_bytes(), first_bytes)
            out.unlink()
            bad = args.copy()
            bad.remove("--fixture")
            self.assertNotEqual(
                subprocess.run(bad, cwd=ROOT, capture_output=True).returncode, 0
            )
            self.assertFalse(out.exists())

    def test_exclusive_download_preserves_existing_bytes(self):
        _, s, _ = self.inputs()
        s["metadata_status"] = "verified"
        s["rights"]["status"] = "reviewed_reuse"
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp) / "raw.csv"
            raw.write_bytes(b"immutable")
            with patch(
                "urllib.request.build_opener",
                side_effect=AssertionError("network forbidden"),
            ):
                with self.assertRaises(ValueError):
                    m.download(s, raw)
            self.assertEqual(raw.read_bytes(), b"immutable")

    def test_layout_multiplier_and_adjustment_fail_closed(self):
        raw, s, p = self.inputs()
        for suffix in (b",UNIT_MULT", b",ADJUSTMENT"):
            lines = raw.splitlines()
            changed = (
                lines[0]
                + suffix
                + b"\n"
                + b"\n".join(
                    line + (b",2" if suffix == b",UNIT_MULT" else b",SA")
                    for line in lines[1:]
                )
                + b"\n"
            )
            p["raw_sha256"] = m.digest(changed)
            with self.assertRaisesRegex(ValueError, "multiplier|adjustment"):
                m.normalize(changed, s, p, fixture=True)
        for bad in (
            raw.replace(b"OBS_VALUE", b"OTHER"),
            raw + b"too,few,columns\n",
            raw.splitlines()[0] + b"\n",
        ):
            p["raw_sha256"] = m.digest(bad)
            with self.assertRaises(ValueError):
                m.normalize(bad, s, p, fixture=True)

    def test_reviewed_metadata_still_requires_rights_and_evidence(self):
        raw, s, p = self.inputs()
        s["metadata_status"] = "verified"
        s["rights"]["status"] = "not_verified"
        with self.assertRaisesRegex(ValueError, "rights not verified"):
            m.normalize(raw, s, p)
        s["rights"]["status"] = "reviewed_reuse"
        s["evidence"] = []
        with self.assertRaisesRegex(ValueError, "evidence"):
            m.normalize(raw, s, p)

    def test_download_hashes_immutable_bytes_and_rejects_redirects(self):
        raw, s, _ = self.inputs()
        s["metadata_status"] = "verified"
        s["rights"]["status"] = "reviewed_reuse"

        class Opener:
            def open(self, url, timeout):
                self.url, self.timeout = url, timeout
                return io.BytesIO(raw)

        def build(handler):
            with self.assertRaisesRegex(ValueError, "Redirect"):
                handler().redirect_request(
                    None, None, 302, "", {}, "https://unreviewed.example/"
                )
            return Opener()

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch("urllib.request.build_opener", side_effect=build),
        ):
            path = Path(tmp) / "snapshot.csv"
            p = m.download(s, path)
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(p["raw_sha256"], m.digest(raw))
            self.assertIsNotNone(m.timestamp(p["retrieved_at"]).tzinfo)

    def test_cli_bad_hash_writes_no_success_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            p = self.inputs()[2]
            p["raw_sha256"] = "0" * 64
            sidecar = Path(tmp) / "bad.json"
            sidecar.write_text(json.dumps(p))
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "macro_controls.pipeline",
                    "--fixture",
                    "--catalog",
                    str(FIX / "sources.json"),
                    "--series",
                    "monthly_rate",
                    "--raw",
                    str(FIX / "monthly_rate.csv"),
                    "--provenance",
                    str(sidecar),
                    "--output",
                    str(out),
                ],
                cwd=ROOT,
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
