"""Extended-window tests use formula-generated synthetic CSVs, never upload values."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from attention.import_trends import (
    ROOT,
    build_import,
    derive_windows,
    inspect_pending,
    periods,
    sha,
)

FIX = ROOT / "tests/fixtures/trends"


def fixture():
    return (FIX / "SYNTHETIC_extended.csv").read_bytes(), json.loads(
        (FIX / "SYNTHETIC_extended_metadata.json").read_text()
    )


class ExtendedTrendsTests(unittest.TestCase):
    def test_274_months_leap_years_and_unchanged_analysis_scale(self):
        raw, m = fixture()
        before = copy.deepcopy(m)
        rows, report = build_import(raw, m, True)
        parts = derive_windows(rows, m)
        self.assertEqual(len(rows), 274)
        self.assertEqual(len(parts["analysis_2018_2025"]), 96)
        self.assertEqual(len(parts["common_2021_2025"]), 60)
        self.assertEqual(max(r["search_interest_index"] for r in rows), 100)
        self.assertEqual(
            max(r["search_interest_index"] for r in parts["analysis_2018_2025"]), 18
        )
        lookup = {r["period"]: r for r in rows}
        for subset in parts.values():
            for r in subset:
                self.assertEqual(r, lookup[r["period"]])
        self.assertEqual(
            report["source_normalization"]["window"],
            {"selection": "all_available_history"},
        )
        self.assertEqual(report["source_window"], m["source_window"])
        self.assertEqual(report["raw_sha256"], sha(raw))
        self.assertEqual(m, before)
        self.assertIn("2020-02", lookup)
        self.assertEqual(
            periods("2019-12", "2020-03"), ["2019-12", "2020-01", "2020-02", "2020-03"]
        )
        self.assertEqual(periods("9999-12", "9999-12"), ["9999-12"])

    def test_partial_final_period_retained_but_not_eligible(self):
        raw, m = fixture()
        rows, report = build_import(raw, m, True)
        self.assertEqual(
            rows[-1]["period_completeness"], "partial_or_unverified_period"
        )
        self.assertIsNotNone(rows[-1]["search_interest_index"])
        self.assertEqual(rows[-2]["period_completeness"], "completed_calendar_month")
        self.assertNotIn("2026-10", report["numeric_index_months"])
        self.assertEqual(report["source_counts"]["partial_or_unverified"], 1)
        self.assertTrue(
            all(
                r["period_completeness"] == "completed_calendar_month"
                for r in derive_windows(rows, m)["analysis_2018_2025"]
            )
        )

    def test_explicit_partial_date_stays_partial_after_later_retrieval(self):
        raw, m = fixture()
        m["retrieved_at"] = "2026-11-03T12:00:00Z"
        m["request_window"] = {"start": "2004-01-01", "end": "2026-10-23"}
        m["normalization"]["window"] = m["request_window"]
        m["source_url"] = m["source_url"].replace(
            "date=all", "date=2004-01-01%202026-10-23"
        )
        rows, _ = build_import(raw, m, True)
        self.assertEqual(
            rows[-1]["period_completeness"], "partial_or_unverified_period"
        )

    def test_value_statuses_survive_subsets_without_fill(self):
        raw, m = fixture()
        lines = raw.decode().splitlines()
        for period, value in [("2018-01", "0"), ("2018-02", "<1"), ("2018-03", "")]:
            lines = [
                f"{period},{value}" if x.startswith(period + ",") else x for x in lines
            ]
        lines = [x for x in lines if not x.startswith("2018-04,")]
        raw = ("\n".join(lines) + "\n").encode()
        m["raw_sha256"] = sha(raw)
        rows, report = build_import(raw, m, True)
        part = derive_windows(rows, m)["analysis_2018_2025"]
        self.assertEqual(part[0]["search_interest_index"], 0)
        self.assertEqual(
            [r["value_status"] for r in part[:4]],
            [
                "observed_index",
                "censored_below_one",
                "missing_in_export",
                "not_in_export",
            ],
        )
        self.assertEqual(report["source_counts"]["blank"], 1)
        self.assertEqual(report["source_counts"]["absent"], 1)

    def test_english_bom_crlf_and_german_are_equivalent(self):
        raw, m = fixture()
        a, _ = build_import(raw, m, True)
        text = (
            raw.decode()
            .replace("Kategorie: Alle Kategorien", "Category: All categories")
            .replace("Monat,Tesla: (Deutschland)", "Month,Tesla: (Germany)")
            .replace("\n", "\r\n")
        )
        raw = ("\ufeff" + text).encode()
        m["raw_sha256"] = sha(raw)
        m["csv_locale"] = "en"
        self.assertEqual(build_import(raw, m, True)[0], a)

    def test_conflicting_metadata_and_invalid_provenance_fail(self):
        raw, base = fixture()
        for mode in (
            "hash",
            "query",
            "geo",
            "property",
            "category",
            "timestamp",
            "future_source",
            "analysis",
            "source",
            "scale",
            "rights",
            "weekly",
            "url_window",
        ):
            m = copy.deepcopy(base)
            if mode == "hash":
                m["raw_sha256"] = "0" * 64
            if mode == "query":
                m["query"]["value"] = "Other"
            if mode == "geo":
                m["geography"] = "US"
            if mode == "property":
                m["search_property"] = "youtube"
            if mode == "category":
                m["category"] = 1
            if mode == "timestamp":
                m["retrieved_at"] = "2026-10-23"
            if mode == "future_source":
                m["source_window"]["end"] = "2026-11"
            if mode == "analysis":
                m["analysis_windows"]["analysis_2018_2025"]["start"] = "2017-01"
            if mode == "source":
                m["source_window"]["start"] = "2005-01"
            if mode == "scale":
                m["normalization"]["window"] = m["analysis_windows"][
                    "analysis_2018_2025"
                ]
            if mode == "rights":
                m["rights"]["private_analysis_confirmed"] = False
            if mode == "weekly":
                m["frequency"] = "weekly"
            if mode == "url_window":
                m["source_url"] = m["source_url"].replace(
                    "date=all", "date=today%205-y"
                )
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                build_import(raw, m, True)

    def test_observed_url_default_category_requires_explicit_metadata(self):
        raw, m = fixture()
        m["source_url"] = m["source_url"].replace("&cat=0", "")
        rows, _ = build_import(raw, m, True)
        self.assertEqual(len(rows), 274)
        m["category"] = None
        with self.assertRaises(ValueError):
            build_import(raw, m, True)
        m["category"] = 1
        with self.assertRaises(ValueError):
            build_import(raw, m, True)

    def test_each_period_validated_not_inferred_from_row_count(self):
        raw, m = fixture()
        for replacement in ("2004-01,5", "2004-13,5", "2004-02-01,5"):
            lines = raw.decode().splitlines()
            lines[4] = replacement
            b = ("\n".join(lines) + "\n").encode()
            n = copy.deepcopy(m)
            n["raw_sha256"] = sha(b)
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                build_import(b, n, True)
        lines = raw.decode().splitlines()
        lines[3], lines[4] = lines[4], lines[3]
        b = ("\n".join(lines) + "\n").encode()
        m["raw_sha256"] = sha(b)
        with self.assertRaises(ValueError):
            build_import(b, m, True)

    def test_pending_sidecar_cannot_pass_admission(self):
        raw, m = fixture()
        m.update(
            origin="observed",
            export_method="official_ui_manual_csv",
            retrieved_at=None,
            source_url=None,
            category=None,
            search_property=None,
            export_attestation=False,
        )
        m["rights"]["private_analysis_confirmed"] = False
        report = inspect_pending(raw, m)
        self.assertEqual(report["structural_counts"]["rows"], 274)
        self.assertEqual(report["structural_counts"]["partial_or_unverified"], 274)
        self.assertFalse(report["empirical_admission"])
        self.assertEqual(report["normalized_csvs"], [])
        self.assertIn("retrieved_at", report["unresolved_fields"])
        self.assertNotIn("search_interest_index", json.dumps(report))
        with self.assertRaises(ValueError):
            build_import(raw, m)

    def test_private_cli_outputs_bound_to_source_and_fixture_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "new"
            args = [
                sys.executable,
                "-m",
                "attention.import_trends",
                "--csv",
                str(FIX / "SYNTHETIC_extended.csv"),
                "--metadata",
                str(FIX / "SYNTHETIC_extended_metadata.json"),
                "--output-dir",
                str(out),
                "--fixture",
            ]
            run = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((out / "coverage.json").read_text())
            self.assertEqual(report["real_observation_months"], [])
            self.assertEqual(
                set(report["outputs"]),
                {"source", "analysis_2018_2025", "common_2021_2025"},
            )
            for v in report["outputs"].values():
                self.assertTrue(v["file"].startswith("fixture_"))
                self.assertEqual(sha((out / v["file"]).read_bytes()), v["sha256"])
                self.assertEqual(v["raw_sha256"], report["raw_sha256"])
            self.assertFalse((out / "observed_monthly.csv").exists())
            args[args.index("--output-dir") + 1] = str(
                ROOT / "artifacts/forbidden_extended_import"
            )
            self.assertNotEqual(
                subprocess.run(args, cwd=ROOT, capture_output=True).returncode, 0
            )

    def test_optional_common_subset_and_old_version_still_work(self):
        raw, m = fixture()
        del m["analysis_windows"]["common_2021_2025"]
        rows, _ = build_import(raw, m, True)
        self.assertEqual(list(derive_windows(rows, m)), ["analysis_2018_2025"])
        old_raw = (FIX / "SYNTHETIC_monthly.csv").read_bytes()
        old_meta = json.loads((FIX / "SYNTHETIC_metadata.json").read_text())
        old_rows, report = build_import(old_raw, old_meta, True)
        self.assertEqual(len(old_rows), 12)
        self.assertNotIn("period_completeness", old_rows[0])
        self.assertNotIn("source_window", report)
