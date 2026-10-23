"""Offline synthetic API shapes; no network, authentic texts or invented Tesla data."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from attention.transform import (
    adapt,
    csv_bytes,
    diagnostics,
    month,
    timestamp,
    transform,
)

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return json.loads(
        (ROOT / "tests/fixtures/attention/youtube_synthetic.json").read_text()
    )


class AttentionTests(unittest.TestCase):
    def test_month_aggregation_keeps_categories_separate(self):
        rows, _ = transform(fixture())
        self.assertEqual([r["period"] for r in rows], ["2020-01", "2020-02", "2020-03"])
        self.assertEqual(rows[0]["earned_video_publications"], 1)
        self.assertEqual(rows[1]["owned_video_publications"], 1)
        self.assertEqual(rows[2]["community_video_publications"], 1)
        self.assertEqual(rows[2]["community_comments_published"], 1)
        self.assertIsNone(rows[0]["owned_video_publications"])

    def test_timezone_month_boundary_and_utc_option(self):
        d = fixture()
        local, _ = transform(d)
        d["aggregation_timezone"] = "UTC"
        utc, _ = transform(d)
        self.assertEqual(local[1]["owned_video_publications"], 1)
        self.assertEqual(utc[0]["owned_video_publications"], 1)
        self.assertEqual(utc[1]["community_video_publications"], 1)
        self.assertEqual(utc[1]["community_comments_published"], 1)

    def test_equivalent_offsets_and_dst_are_not_naive(self):
        self.assertEqual(
            timestamp("2020-03-01T00:30:00+01:00"), timestamp("2020-02-29T23:30:00Z")
        )
        d = fixture()
        d["window"] = {"start": "2020-03", "end": "2020-04"}
        d["batches"][0]["response"]["items"][0]["snippet"]["publishedAt"] = (
            "2020-03-31T22:30:00Z"
        )
        rows, _ = transform(d)
        self.assertEqual(rows[1]["owned_video_publications"], 1)

    def test_dates_fail_closed(self):
        for v in (
            "2020-02-30T00:00:00Z",
            "2020-01-01",
            "2020-01-01T00:00:00",
            "2020-01-01T00:00:00+25:00",
        ):
            with self.subTest(v=v), self.assertRaises(ValueError):
                timestamp(v)
        for v in ("2020-00", "2020-13", "2020-1", "2020-01\n"):
            with self.subTest(v=v), self.assertRaises(ValueError):
                month(v)

    def test_deduplicate_repeated_pages_and_retrieval_snapshots(self):
        d = fixture()
        d["batches"].append(copy.deepcopy(d["batches"][0]))
        d["batches"][-1]["response"]["items"][0]["statistics"]["viewCount"] = "99999"
        self.assertEqual(transform(d), transform(fixture()))

    def test_conflicting_duplicate_fails_instead_of_arbitrary_selection(self):
        d = fixture()
        d["batches"].append(copy.deepcopy(d["batches"][0]))
        d["batches"][-1]["response"]["items"][0]["snippet"]["publishedAt"] = (
            "2020-02-01T01:30:00Z"
        )
        with self.assertRaisesRegex(ValueError, "Conflicting duplicate"):
            adapt(d)

    def test_views_at_retrieval_never_become_historical_views(self):
        d = fixture()
        original, _ = transform(d)
        for b in d["batches"][:3]:
            b["response"]["items"][0]["statistics"]["viewCount"] = "0"
        rows, _ = transform(d)
        self.assertEqual(original, rows)
        self.assertTrue(
            all(
                r[c + "_historical_views"] is None
                for r in rows
                for c in ("owned", "earned", "community")
            )
        )
        self.assertNotIn("viewCount", json.dumps(adapt(d)))

    def test_empty_pages_and_unseen_months_are_unknown_not_zero(self):
        d = fixture()
        for b in d["batches"]:
            b["response"] = {"items": [], "nextPageToken": "FAKE_MORE"}
        rows, _ = transform(d)
        self.assertTrue(
            all(v is None for r in rows for k, v in r.items() if k != "period")
        )
        self.assertNotIn(b"None", csv_bytes(rows))
        self.assertIn(b"2020-01,,,,,,,,,\n", csv_bytes(rows))

    def test_language_content_and_audience_evidence_are_independent(self):
        d = fixture()
        self.assertEqual(d["sources"][0]["geography"]["language"], "de")
        self.assertTrue(d["sources"][0]["geography"]["content_germany"])
        self.assertEqual(d["sources"][0]["geography"]["audience_country"], "unknown")
        d["sources"][0]["geography"]["country"] = "DE"
        with self.assertRaises(ValueError):
            adapt(d)
        d = fixture()
        d["sources"][0]["geography"]["evidence"] = ""
        with self.assertRaises(ValueError):
            adapt(d)

    def test_public_comments_are_community_not_owned_channel_content(self):
        d = fixture()
        d["batches"][-1]["source_id"] = "owned"
        d["batches"][-1]["response"]["items"][0]["snippet"]["channelId"] = "FAKE_owned"
        rows, _ = transform(d)
        self.assertEqual(rows[2]["community_comments_published"], 1)
        self.assertIsNone(rows[2]["owned_comments_published"])

    def test_text_authors_replies_and_sentiment_are_not_exported(self):
        records = adapt(fixture())
        self.assertNotIn("textDisplay", json.dumps(records))
        self.assertNotIn("author", json.dumps(records))
        self.assertEqual(sum(r["kind"] == "comment_publication" for r in records), 1)
        rows, records = transform(fixture())
        self.assertFalse(diagnostics(fixture(), rows, records)["sentiment_available"])

    def test_bad_responses_counts_and_selection_fail_closed(self):
        for mode in (
            "error",
            "missing_items",
            "wrong_channel",
            "future",
            "unsupported",
            "bad_count",
            "category",
            "source_duplicate",
            "origin",
            "rights",
        ):
            d = fixture()
            b = d["batches"][0]
            obj = b["response"]["items"][0]
            if mode == "error":
                b["response"]["error"] = {"code": 403}
            if mode == "missing_items":
                b["response"] = {}
            if mode == "wrong_channel":
                obj["snippet"]["channelId"] = "OUTSIDE_SELECTION"
            if mode == "future":
                obj["snippet"]["publishedAt"] = "2027-01-01T00:00:00Z"
            if mode == "unsupported":
                b["resource"] = "historical_views"
            if mode == "bad_count":
                obj["statistics"]["viewCount"] = "NaN"
            if mode == "category":
                d["sources"][0]["category"] = "combined"
            if mode == "source_duplicate":
                d["sources"].append(copy.deepcopy(d["sources"][0]))
            if mode == "origin":
                d["sources"][0]["origin"] = "observed"
            if mode == "rights":
                d["sources"][0]["rights"] = "publicly_accessible_so_free"
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                adapt(d)

    def test_unreviewed_empirical_population_cannot_pass(self):
        d = fixture()
        d["status"] = "empirically_populated"
        with self.assertRaises(ValueError):
            adapt(d)
        d["status"] = "not empirically populated"
        with self.assertRaises(ValueError):
            adapt(d)

    def test_window_selection_and_determinism_no_mutation(self):
        d = fixture()
        before = copy.deepcopy(d)
        a = transform(d)
        self.assertEqual(a, transform(d))
        self.assertEqual(before, d)
        d["window"] = {"start": "2020-02", "end": "2020-02"}
        rows, records = transform(d)
        self.assertEqual(len(rows), 1)
        self.assertEqual(diagnostics(d, rows, records)["distinct_observed_sources"], 1)
        d["window"] = {"start": "2020-03", "end": "2020-01"}
        with self.assertRaises(ValueError):
            transform(d)

    def test_committed_unpopulated_outputs_and_both_windows(self):
        d = json.loads((ROOT / "data/organic_attention/observations.json").read_text())
        rows, records = transform(d)
        self.assertEqual(len(rows), 96)
        self.assertEqual(records, [])
        self.assertEqual(
            csv_bytes(rows),
            (ROOT / "data/organic_attention/monthly_indicators.csv").read_bytes(),
        )
        report = diagnostics(d, rows, records)
        self.assertEqual(
            report,
            json.loads((ROOT / "data/organic_attention/summary.json").read_text()),
        )
        self.assertEqual(report["unknown_months"], 96)
        self.assertEqual(report["shared_2021_2025_months"], 60)
        self.assertEqual(report["shared_2021_2025_observed_months"], [])

    def test_cli_offline_reproduction_and_tamper_detection(self):
        check = subprocess.run(
            [sys.executable, "-m", "attention.transform", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            out, report = Path(tmp) / "out.csv", Path(tmp) / "summary.json"
            args = [
                sys.executable,
                "-m",
                "attention.transform",
                "--input",
                str(ROOT / "tests/fixtures/attention/youtube_synthetic.json"),
                "--output",
                str(out),
                "--summary",
                str(report),
            ]
            run = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(
                json.loads(report.read_text())["status"], "synthetic_fixture"
            )
            out.write_bytes(b"tampered")
            self.assertNotEqual(
                subprocess.run(
                    args + ["--check"], cwd=ROOT, capture_output=True
                ).returncode,
                0,
            )
