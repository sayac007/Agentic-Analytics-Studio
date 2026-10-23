"""Synthetic test events exercise calendar logic, never stand in for real campaigns."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from campaigns.transform import check_date, csv_bytes, lag, summary, transform

ROOT = Path(__file__).resolve().parents[1]


def event(name="test-a", start="2020-01-20", end="2020-02-05"):
    return dict(
        id=name,
        title="Synthetic parser fixture, not historical evidence",
        candidate_kind="campaign_candidate",
        category="paid_media",
        evidence_class="verified",
        decision="include_paid_indicator",
        geography=dict(
            germany_status="explicit", germany_evidence="Fixture assertion only"
        ),
        source_ids=["fixture"],
        documented_claim="Synthetic test assertion",
        paid_media_evidence="Fixture only",
        campaign_identity_verified=True,
        campaign_id=name,
        interval_status="documented_run",
        start=dict(
            value=start, precision="day", role="campaign_start", source_ids=["fixture"]
        ),
        end=dict(
            value=end, precision="day", role="campaign_end", source_ids=["fixture"]
        ),
        observed_ad_days=[],
        observed_ad_months=[],
    )


def ledger(events):
    return dict(
        ledger_version="1.0.0",
        window=dict(start="2020-01-01", end="2020-05-31"),
        research_as_of="2020-05-31",
        sources=[dict(id="fixture", http_status=200, content_status="article_read")],
        events=events,
    )


class Campaigns(unittest.TestCase):
    def test_date_precision_and_no_implicit_month_day(self):
        for spec in [
            dict(value="2020-02-29", precision="day"),
            dict(value="2020-02", precision="month"),
            dict(value="2020", precision="year"),
            dict(value=None, precision="unknown"),
        ]:
            check_date(spec)
        for spec in [
            dict(value="2021-02-29", precision="day"),
            dict(value="2020-02-01", precision="month"),
            dict(value="2020-13", precision="month"),
            dict(value="", precision="unknown"),
            dict(value="2020-01", precision="day"),
        ]:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                check_date(spec)

    def test_month_boundary_inclusive_run_and_unknown_outside_run(self):
        rows = transform(ledger([event()]))
        self.assertEqual(
            [r["verified_paid_activity"] for r in rows], [1, 1, None, None, None]
        )
        self.assertAlmostEqual(rows[0]["active_day_share"], 12 / 31)
        self.assertAlmostEqual(rows[1]["active_day_share"], 5 / 29)
        self.assertEqual(rows[0]["active_campaign_count"], 1)
        self.assertIsNone(rows[2]["active_day_share"])
        self.assertIsNone(rows[2]["active_campaign_count"])

    def test_overlap_union_and_peak_concurrency_not_campaign_month_sum(self):
        rows = transform(ledger([event(), event("test-b", "2020-02-01", "2020-02-10")]))
        self.assertAlmostEqual(rows[1]["active_day_share"], 10 / 29)
        self.assertEqual(rows[1]["active_campaign_count"], 2)
        rows = transform(
            ledger(
                [
                    event("a", "2020-01-01", "2020-01-05"),
                    event("b", "2020-01-10", "2020-01-15"),
                ]
            )
        )
        self.assertEqual(rows[0]["active_campaign_count"], 1)

    def test_repeated_observations_of_same_campaign_are_deduplicated(self):
        a = event()
        b = event("other-observation")
        b["campaign_id"] = a["campaign_id"]
        self.assertEqual(transform(ledger([a, b]))[0]["active_campaign_count"], 1)

    def test_point_observations_never_bridge_a_flight(self):
        e = event()
        e["interval_status"] = "not_established"
        e["start"] = dict(
            value=None, precision="unknown", role="campaign_start", source_ids=[]
        )
        e["end"] = dict(
            value=None, precision="unknown", role="campaign_end", source_ids=[]
        )
        e["observed_ad_days"] = [
            dict(value="2020-01-10", source_id="fixture"),
            dict(value="2020-03-10", source_id="fixture"),
        ]
        rows = transform(ledger([e]))
        self.assertEqual(
            [r["verified_paid_activity"] for r in rows], [1, None, 1, None, None]
        )
        self.assertTrue(all(r["active_day_share"] is None for r in rows))

    def test_month_precision_does_not_create_full_calendar_month_exposure(self):
        e = event()
        e["start"].update(value="2020-01", precision="month")
        e["end"].update(value="2020-02", precision="month")
        e["observed_ad_months"] = [dict(value="2020-01", source_id="fixture")]
        rows = transform(ledger([e]))
        self.assertEqual(rows[0]["verified_paid_activity"], 1)
        self.assertIsNone(rows[0]["active_day_share"])
        self.assertIsNone(rows[0]["active_campaign_count"])
        self.assertIsNone(rows[1]["verified_paid_activity"])

    def test_unknown_campaign_identity_is_not_one_campaign(self):
        e = event()
        e["campaign_identity_verified"] = False
        e["campaign_id"] = None
        rows = transform(ledger([e]))
        self.assertEqual(rows[0]["verified_paid_activity"], 1)
        self.assertIsNone(rows[0]["active_campaign_count"])

    def test_unsuitable_events_excluded_without_zero_filling(self):
        cases = [
            dict(category="sales_promotion", decision="context_only"),
            dict(category="owned_media", decision="context_only"),
            dict(category="product_event", decision="context_only"),
            dict(category="earned_media_pr", decision="context_only"),
            dict(evidence_class="partial", decision="hold"),
            dict(evidence_class="unverified", decision="hold"),
            dict(evidence_class="excluded", decision="exclude"),
            dict(geography=dict(germany_status="not_established"), decision="exclude"),
        ]
        for change in cases:
            e = event()
            e.update(change)
            with self.subTest(change=change):
                self.assertTrue(
                    all(
                        r["verified_paid_activity"] is None
                        for r in transform(ledger([e]))
                    )
                )

    def test_offer_deadlines_are_not_paid_campaign_bounds(self):
        e = event()
        e["start"]["role"] = "application_eligibility_start"
        e["end"]["role"] = "delivery_deadline"
        self.assertTrue(
            all(r["verified_paid_activity"] is None for r in transform(ledger([e])))
        )

    def test_lag_zero_through_three_and_missing_values(self):
        self.assertEqual(lag([0, None, 1], 1), [None, 0, None])
        with self.assertRaises(ValueError):
            lag([1], -1)
        rows = transform(ledger([event("a", "2020-01-01", "2020-01-01")]))
        for k in range(4):
            self.assertEqual(
                [r["verified_paid_activity_lag" + str(k)] for r in rows],
                [1 if i == k else None for i in range(5)],
            )
        self.assertEqual(
            rows[0]["verified_paid_activity_lag0"], rows[0]["verified_paid_activity"]
        )

    def test_research_cutoff_and_window_clip_do_not_predict_future_activity(self):
        d = ledger([event("a", "2019-12-01", "2020-01-10")])
        d["research_as_of"] = "2020-01-10"
        rows = transform(d)
        self.assertAlmostEqual(rows[0]["active_day_share"], 10 / 31)
        self.assertTrue(all(r["verified_paid_activity"] is None for r in rows[1:]))
        e = event()
        e["interval_status"] = "planned"
        self.assertTrue(
            all(r["verified_paid_activity"] is None for r in transform(ledger([e])))
        )

    def test_unknown_dates_article_date_and_listing_snapshot_are_not_observations(self):
        e = event()
        e["start"].update(value=None, precision="unknown")
        e["end"].update(value=None, precision="unknown")
        e["article_date"] = "2020-01-20"
        e["library_listing_snapshot"] = "2020-01-20"
        self.assertTrue(
            all(r["verified_paid_activity"] is None for r in transform(ledger([e])))
        )

    def test_invalid_dates_and_source_claims_fail_closed(self):
        for mode in [
            "reverse",
            "duplicate",
            "missing_source",
            "shell",
            "bad_category",
            "missing_bound_source",
            "unknown_geography",
            "future_run",
            "future_snapshot",
        ]:
            d = ledger([event()])
            if mode == "future_run":
                d["events"][0]["end"]["value"] = "2020-06-01"
            if mode == "future_snapshot":
                d["events"][0]["observed_ad_days"] = [
                    dict(value="2020-06-01", source_id="fixture")
                ]
            if mode == "reverse":
                d["events"][0]["start"]["value"] = "2020-03-01"
            if mode == "duplicate":
                d["events"].append(copy.deepcopy(d["events"][0]))
            if mode == "missing_source":
                d["events"][0]["source_ids"] = ["absent"]
            if mode == "shell":
                d["sources"][0]["content_status"] = "application_shell_only"
            if mode == "bad_category":
                d["events"][0]["category"] = "media_spend"
            if mode == "missing_bound_source":
                d["events"][0]["start"]["source_ids"] = []
            if mode == "unknown_geography":
                d["events"][0]["geography"]["germany_status"] = "unknown"
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                transform(d)

    def test_determinism_csv_missing_is_blank_and_no_mutation(self):
        d = ledger([event()])
        before = copy.deepcopy(d)
        a = csv_bytes(transform(d))
        b = csv_bytes(transform(d))
        self.assertEqual(a, b)
        self.assertEqual(d, before)
        self.assertNotIn(b"None", a)
        self.assertTrue(
            csv_bytes(transform(ledger([]))).splitlines()[1].startswith(b"2020-01,,,,,")
        )

    def test_committed_real_ledger_is_auditable_not_a_synthetic_success_fixture(self):
        d = json.loads((ROOT / "data/tesla_campaigns/evidence.json").read_text())
        rows = transform(d)
        self.assertEqual(len(rows), 106)
        self.assertEqual(
            csv_bytes(rows),
            (ROOT / "data/tesla_campaigns/monthly_indicators.csv").read_bytes(),
        )
        self.assertEqual(
            summary(d, rows),
            json.loads((ROOT / "data/tesla_campaigns/summary.json").read_text()),
        )
        # The disputed/library-only record is held, never turned into November delivery.
        e = next(e for e in d["events"] if e["id"] == "de-google-listing-2023")
        self.assertEqual(e["decision"], "hold")
        self.assertFalse(e["observed_ad_days"])
        self.assertIsNone(
            next(r for r in rows if r["period"] == "2023-11")["verified_paid_activity"]
        )
        result = subprocess.run(
            [sys.executable, "-m", "campaigns.transform", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
