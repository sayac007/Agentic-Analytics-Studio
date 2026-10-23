"""Synthetic CSV contract tests only; no real Trends observation or live requests."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlencode

from attention.import_trends import (
    DATA,
    ROOT,
    blocked_coverage,
    build_import,
    csv_bytes,
    sha,
)

FIXTURES = ROOT / "tests/fixtures/trends"


def fixture():
    return (FIXTURES / "SYNTHETIC_monthly.csv").read_bytes(), json.loads(
        (FIXTURES / "SYNTHETIC_metadata.json").read_text()
    )


def changed(raw):
    _, meta = fixture()
    meta["raw_sha256"] = sha(raw)
    return raw, meta


class TrendsImportTests(unittest.TestCase):
    def test_native_monthly_csv_censoring_missingness_and_real_zero(self):
        raw, meta = fixture()
        rows, report = build_import(raw, meta, fixture=True)
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["search_interest_index"], 0)
        self.assertEqual(
            rows[1],
            dict(
                period="2018-02",
                search_interest_index=None,
                value_status="censored_below_one",
            ),
        )
        self.assertEqual(rows[2]["value_status"], "not_in_export")
        self.assertEqual(rows[3]["search_interest_index"], 100)
        self.assertEqual(rows[4]["value_status"], "missing_in_export")
        self.assertEqual(report["numeric_index_months"], ["2018-01", "2018-04"])
        self.assertEqual(report["censored_below_one_months"], ["2018-02"])
        self.assertEqual(report["real_observation_months"], [])
        self.assertEqual(report["status"], "synthetic_fixture")
        self.assertIn(b"2018-02,,censored_below_one", csv_bytes(rows))

    def test_german_bom_crlf_decimal_csv(self):
        raw, meta = fixture()
        raw = "\ufeffKategorie: Alle Kategorien\r\n\r\nMonat,Tesla: (Deutschland)\r\n2018-01,12.5\r\n".encode()
        meta["csv_locale"] = "de"
        meta["raw_sha256"] = sha(raw)
        rows, _ = build_import(raw, meta, True)
        self.assertEqual(rows[0]["search_interest_index"], 12.5)
        self.assertTrue(all(r["search_interest_index"] is None for r in rows[1:]))

    def test_known_hash_and_provenance_binding(self):
        raw, meta = fixture()
        with self.assertRaisesRegex(ValueError, "hash"):
            build_import(raw + b"\n", meta, True)
        with self.assertRaisesRegex(ValueError, "provenance"):
            build_import(raw, meta, False)
        meta["origin"] = "observed"
        with self.assertRaises(ValueError):
            build_import(raw, meta, True)

    def test_duplicate_and_unordered_months_rejected(self):
        for lines in ("2018-01,1\n2018-01,1", "2018-02,2\n2018-01,1"):
            raw, meta = changed(("Month,Tesla: (Germany)\n" + lines + "\n").encode())
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                build_import(raw, meta, True)

    def test_malformed_numeric_rows_fail_closed(self):
        for value in (
            "NaN",
            "Infinity",
            "-1",
            "101",
            "1_0",
            " 10",
            "true",
            "1e2",
            "0,5",
        ):
            raw, meta = changed(f"Month,Tesla: (Germany)\n2018-01,{value}\n".encode())
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_import(raw, meta, True)
        for row in (
            "2018-13,1",
            "2018-01-01,1",
            "2018-1,1",
            ",1",
            "2018-01",
            "2018-01,1,extra",
            "2019-01,1",
            '"2018-01,1',
        ):
            raw, meta = changed(("Month,Tesla: (Germany)\n" + row + "\n").encode())
            with self.subTest(row=row), self.assertRaises(ValueError):
                build_import(raw, meta, True)

    def test_wrong_query_geo_category_locale_and_frequency_headers(self):
        for header in (
            "Month,Nikola Tesla: (Germany)",
            "Month,Tesla: (United States)",
            "Week,Tesla: (Germany)",
            "Month;Tesla: (Germany)",
            "Category: Autos",
            "Monat,Tesla: (Deutschland)",
        ):
            raw, meta = changed((header + "\n2018-01,1\n").encode())
            with self.subTest(header=header), self.assertRaises(ValueError):
                build_import(raw, meta, True)

    def test_scale_window_flags_and_frequency_conflicts(self):
        raw, base = fixture()
        for mode in (
            "weekly",
            "tz",
            "max",
            "scale_kind",
            "combined",
            "rescaled",
            "normalization_window",
            "normalization_geo",
            "flag_type",
            "bounds_type",
            "future",
            "partial",
            "unknown_field",
            "origin",
            "attestation",
            "rights",
        ):
            m = copy.deepcopy(base)
            if mode == "weekly":
                m["frequency"] = "weekly"
            if mode == "tz":
                m["time_zone"] = "Europe/Berlin"
            if mode == "max":
                m["normalization"]["max"] = 1
            if mode == "scale_kind":
                m["normalization"]["kind"] = "absolute_searches"
            if mode == "combined":
                m["normalization"]["combined_exports"] = True
            if mode == "rescaled":
                m["normalization"]["rescaled"] = True
            if mode == "normalization_window":
                m["normalization"]["window"] = {
                    "start": "2019-01-01",
                    "end": "2019-12-31",
                }
            if mode == "normalization_geo":
                m["normalization"]["geography"] = "US"
            if mode == "flag_type":
                m["normalization"]["rescaled"] = 0
            if mode == "bounds_type":
                m["normalization"]["min"] = False
            if mode == "future":
                m["retrieved_at"] = "2018-12-31T23:59:00Z"
            if mode == "partial":
                m["request_window"]["start"] = "2018-01-02"
            if mode == "unknown_field":
                m["generator"] = "fictional"
            if mode == "origin":
                m["origin"] = "proxy"
            if mode == "attestation":
                m["export_attestation"] = False
            if mode == "rights":
                m["rights"]["private_analysis_confirmed"] = False
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                build_import(raw, m, True)

    def test_source_url_bound_to_exact_query_request_and_property(self):
        raw, base = fixture()
        for mode in (
            "geo",
            "term",
            "date",
            "property",
            "duplicate",
            "host",
            "category",
        ):
            m = copy.deepcopy(base)
            params = {
                "q": "Tesla",
                "geo": "DE",
                "cat": "0",
                "date": "2018-01-01 2018-12-31",
            }
            if mode == "geo":
                params["geo"] = "US"
            if mode == "term":
                params["q"] = "Tesla Motors"
            if mode == "date":
                params["date"] = "2018-01-01 2025-12-31"
            if mode == "property":
                params["gprop"] = "youtube"
            if mode == "category":
                params["cat"] = "47"
            m["source_url"] = "https://trends.google.com/trends/explore?" + urlencode(
                params
            )
            if mode == "duplicate":
                m["source_url"] += "&geo=DE"
            if mode == "host":
                m["source_url"] = m["source_url"].replace(
                    "trends.google.com", "example.com"
                )
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                build_import(raw, m, True)

    def test_topic_alternative_is_separate_with_declared_evidence(self):
        raw, m = fixture()
        # Explicitly fake ID, not a claim about a real Tesla topic.
        m["query"] = {
            "kind": "topic",
            "value": "/m/FAKE_TEST_ONLY",
            "label": "Tesla company fixture",
            "topic_evidence_url": "https://trends.google.com/trends/explore?q=%2Fm%2FFAKE_TEST_ONLY",
        }
        m["source_url"] = m["source_url"].replace("q=Tesla", "q=%2Fm%2FFAKE_TEST_ONLY")
        raw = raw.replace(b"Tesla: (Germany)", b"Tesla company fixture: (Germany)")
        m["raw_sha256"] = sha(raw)
        _, report = build_import(raw, m, True)
        self.assertEqual(report["provenance"]["query"]["kind"], "topic")
        m["query"]["topic_evidence_url"] = None
        with self.assertRaises(ValueError):
            build_import(raw, m, True)

    def test_no_observation_input_does_not_create_positive_coverage(self):
        raw, m = changed(b"Month,Tesla: (Germany)\n2018-01,\n")
        # Mock the declared-observed contract branch in memory only, never repository evidence.
        m.update(origin="observed", export_method="official_ui_manual_csv")
        _, report = build_import(raw, m)
        self.assertEqual(report["status"], "not_empirically_populated")
        self.assertEqual(report["coverage_2018_2025"]["unknown_months"], 96)

    def test_coverage_intersections_and_no_pit_claim(self):
        raw, m = changed(b"Month,Tesla: (Germany)\n2018-01,0\n2018-02,<1\n")
        # Pure contract test, not actual Google-origin evidence.
        m.update(origin="observed", export_method="official_ui_manual_csv")
        _, report = build_import(raw, m)
        self.assertEqual(
            report["coverage_2018_2025"]["observed_months"], ["2018-01", "2018-02"]
        )
        self.assertEqual(report["coverage_2021_2025"]["unknown_months"], 60)
        self.assertEqual(report["historical_point_in_time"], "not_verified")

    def test_deterministic_no_input_mutation(self):
        raw, m = fixture()
        before = copy.deepcopy(m)
        self.assertEqual(build_import(raw, m, True), build_import(raw, m, True))
        self.assertEqual(m, before)

    def test_cli_fixture_is_private_does_not_change_raw_or_existing_empirical(self):
        raw, m = fixture()
        empirical_before = (DATA / "monthly_indicators.csv").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "new"
            args = [
                sys.executable,
                "-m",
                "attention.import_trends",
                "--csv",
                str(FIXTURES / "SYNTHETIC_monthly.csv"),
                "--metadata",
                str(FIXTURES / "SYNTHETIC_metadata.json"),
                "--output-dir",
                str(out),
                "--fixture",
            ]
            run = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue((out / "fixture_monthly.csv").exists())
            self.assertFalse((out / "observed_monthly.csv").exists())
            self.assertEqual(
                json.loads((out / "coverage.json").read_text())[
                    "real_observation_months"
                ],
                [],
            )
            self.assertNotEqual(
                subprocess.run(args, cwd=ROOT, capture_output=True).returncode, 0
            )
        self.assertEqual((FIXTURES / "SYNTHETIC_monthly.csv").read_bytes(), raw)
        self.assertEqual(
            (DATA / "monthly_indicators.csv").read_bytes(), empirical_before
        )

    def test_cli_copied_known_fixture_cannot_be_relabelled_observed(self):
        raw, m = fixture()
        m.update(origin="observed", export_method="official_ui_manual_csv")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "csv.csv").write_bytes(raw)
            (p / "meta.json").write_text(json.dumps(m))
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "attention.import_trends",
                    "--csv",
                    str(p / "csv.csv"),
                    "--metadata",
                    str(p / "meta.json"),
                    "--output-dir",
                    str(p / "out"),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("synthetic fixtures", run.stderr)
            self.assertFalse((p / "out").exists())

    def test_invalid_input_creates_no_successful_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "attention.import_trends",
                    "--csv",
                    str(FIXTURES / "SYNTHETIC_monthly.csv"),
                    "--metadata",
                    str(DATA / "trends_import_metadata.template.json"),
                    "--output-dir",
                    str(out),
                    "--fixture",
                ],
                cwd=ROOT,
                capture_output=True,
            )
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(out.exists())

    def test_blocked_coverage_requires_actual_failure_evidence(self):
        access = json.loads((DATA / "task01f_access.json").read_text())
        access["attempts"][0]["http_status"] = 200
        with self.assertRaises(ValueError):
            blocked_coverage(json.dumps(access).encode())

    def test_blocked_report_and_cli_are_reproducible_without_network(self):
        expected = blocked_coverage((DATA / "task01f_access.json").read_bytes())
        self.assertEqual(
            expected, json.loads((DATA / "real_data_coverage.json").read_text())
        )
        self.assertIsNone(expected["observed_csv"])
        run = subprocess.run(
            [sys.executable, "-m", "attention.import_trends", "--check-blocked"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), expected)


if __name__ == "__main__":
    unittest.main()
