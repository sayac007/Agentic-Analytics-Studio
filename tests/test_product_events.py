"""Offline event-contract checks; calendar mutations are synthetic unit cases only."""

import copy
import json
import subprocess
import sys
import unittest

from jsonschema import ValidationError
from product_events.transform import DATA, ROOT, csv_bytes, transform, validate


def ledger():
    return json.loads((DATA / "evidence.json").read_text())


class ProductEvidenceTests(unittest.TestCase):
    def invalid(self, d):
        with self.assertRaises((ValueError, ValidationError)):
            validate(d)

    def test_required_source_provenance_and_hash(self):
        for key in (
            "publisher",
            "url",
            "accessed_on",
            "response_sha256",
            "source_type",
        ):
            d = ledger()
            del d["sources"][0][key]
            with self.subTest(key=key):
                self.invalid(d)
        d = ledger()
        d["sources"][0]["response_sha256"] = "not-a-hash"
        self.invalid(d)
        d = ledger()
        d["events"][0]["source_ids"] = ["absent"]
        self.invalid(d)
        d = ledger()
        d["sources"][0]["url"] = "https://"
        self.invalid(d)

    def test_invalid_day_month_year_and_unknown_dates(self):
        for p, v in [
            ("day", "2021-02-29"),
            ("month", "2021-13"),
            ("month", "2021-01-01"),
            ("year", "0000"),
            ("unknown", "2020-01-01"),
            ("day", None),
        ]:
            d = ledger()
            d["events"][0]["date"].update(precision=p, value=v)
            with self.subTest(p=p, v=v):
                self.invalid(d)

    def test_interval_order_and_source_future_dates(self):
        d = ledger()
        e = d["events"][0]
        e["date"].update(precision="day", value="2019-03-20")
        e["end_date"] = {"precision": "month", "value": "2019-02", "role": "ended"}
        self.invalid(d)
        d = ledger()
        d["sources"][0]["publication_date"].update(precision="day", value="2027-01-01")
        self.invalid(d)
        d = ledger()
        d["events"][0]["date"].update(precision="month", value="2017-12")
        self.invalid(d)

    def test_germany_scope_is_required_for_verified_events(self):
        d = ledger()
        d["events"][0]["geography"]["status"] = "not_established"
        self.invalid(d)
        d = ledger()
        d["events"][0]["geography"]["evidence"] = ""
        self.invalid(d)
        rows, _ = transform(ledger())
        self.assertIsNone(
            next(r for r in rows if r["period"] == "2024-04")["announcement_parents"]
        )

    def test_duplicate_parent_or_same_milestone_rejected(self):
        d = ledger()
        d["parents"].append(copy.deepcopy(d["parents"][0]))
        self.invalid(d)
        d = ledger()
        e = copy.deepcopy(d["events"][0])
        e["event_id"] = "synthetic-duplicate"
        d["events"].append(e)
        self.invalid(d)
        d = ledger()
        d["events"][0]["parent_id"] = "absent"
        self.invalid(d)

    def test_source_milestones_share_parent_but_are_separate_columns(self):
        rows, _ = transform(ledger())
        r = next(r for r in rows if r["period"] == "2023-09")
        self.assertEqual(r["model_refresh_parents"], 1)
        self.assertEqual(r["orders_open_parents"], 1)
        d = ledger()
        e = copy.deepcopy(
            next(e for e in d["events"] if e["event_id"] == "highland-orders_open")
        )
        e["event_id"] = "synthetic-second-observation"
        e["date"]["value"] = "2023-09-02"
        d["events"].append(e)
        self.assertEqual(
            next(r for r in transform(d)[0] if r["period"] == "2023-09")[
                "orders_open_parents"
            ],
            1,
        )

    def test_price_currency_units_vat_and_finite_arithmetic(self):
        for field, value in [
            ("currency", "USD"),
            ("unit", "monthly_payment"),
            ("after", float("nan")),
        ]:
            d = ledger()
            p = next(e for e in d["events"] if e["price"])["price"]
            p[field] = value
            with self.subTest(field=field):
                self.invalid(d)
        d = ledger()
        e = next(e for e in d["events"] if e["price"])
        e["status"] = "verified"
        self.invalid(d)
        d = ledger()
        p = next(e for e in d["events"] if e["price"])["price"]
        p["before"] = 100
        p["after"] = 80
        p["reported_change"] = 5
        self.invalid(d)

    def test_financing_is_not_a_list_price(self):
        d = ledger()
        price = copy.deepcopy(next(e["price"] for e in d["events"] if e["price"]))
        next(e for e in d["events"] if e["event_type"] == "financing_offer")[
            "price"
        ] = price
        self.invalid(d)

    def test_recall_notice_not_remedy_and_no_automatic_supply_shock(self):
        d = ledger()
        rows, _ = transform(d)
        r = next(r for r in rows if r["period"] == "2024-06")
        self.assertEqual(r["recall_remedy_parents"], 1)
        self.assertIsNone(r["recall_notice_parents"])
        self.assertIsNone(r["supply_disruption_parents"])
        e = next(e for e in d["events"] if e["event_id"] == "hood-ota-remedy")
        self.assertIsNone(e["recall"]["affected_de_count"])
        self.assertEqual(e["recall"]["delivery_constraint"], "not_established")
        e["recall"]["delivery_constraint"] = "documented"
        self.invalid(d)
        d = ledger()
        next(e for e in d["events"] if e["event_id"] == "hood-ota-remedy")["date"][
            "role"
        ] = "announced"
        self.invalid(d)

    def test_month_precision_is_retained_and_not_first_day_padded(self):
        rows, _ = transform(ledger())
        r = next(r for r in rows if r["period"] == "2019-02")
        self.assertEqual(r["first_delivery_de_parents"], 1)
        self.assertIn("model3-first-de", r["month_precision_event_ids"])
        self.assertEqual(ledger()["events"][0]["date"]["value"], "2019-02")
        d = ledger()
        d["events"][0]["date"].update(precision="year", value="2019")
        self.assertIsNone(
            next(r for r in transform(d)[0] if r["period"] == "2019-02")[
                "first_delivery_de_parents"
            ]
        )

    def test_unknown_is_not_zero_and_hypothesis_not_verified(self):
        rows, summary = transform(ledger())
        self.assertEqual(summary["confirmed_inactive_months"], 0)
        self.assertIsNone(rows[0]["announcement_parents"])
        self.assertNotIn(b"None", csv_bytes(rows))
        d = ledger()
        d["events"][0]["provenance_category"] = "hypothesis"
        self.invalid(d)

    def test_sparse_offer_snapshots_never_become_continuous_mai(self):
        d = ledger()
        rows, _ = transform(d)
        self.assertTrue(all(r["model_availability_index"] is None for r in rows))
        d["availability_observations"][0]["complete_census"] = True
        self.invalid(d)
        d = ledger()
        d["availability_observations"][0]["continuity_established"] = True
        self.invalid(d)

    def test_determinism_no_mutation_and_exact_committed_outputs(self):
        d = ledger()
        before = copy.deepcopy(d)
        rows, summary = transform(d)
        self.assertEqual((rows, summary), transform(d))
        self.assertEqual(d, before)
        self.assertEqual(len(rows), 96)
        self.assertEqual(
            csv_bytes(rows), (DATA / "monthly_indicators.csv").read_bytes()
        )
        self.assertEqual(summary, json.loads((DATA / "summary.json").read_text()))

    def test_offline_cli_regeneration_does_not_modify_kba_or_trends(self):
        protected = list((ROOT / "data/kba/derived").iterdir()) + list(
            (ROOT / "data/organic_attention").iterdir()
        )
        before = {p: p.read_bytes() for p in protected if p.is_file()}
        for suffix in ([], ["--check"]):
            run = subprocess.run(
                [sys.executable, "-m", "product_events.transform"] + suffix,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
        for p, b in before.items():
            self.assertEqual(p.read_bytes(), b)
