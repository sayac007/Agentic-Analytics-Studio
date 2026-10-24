"""Offline only: synthetic observations never establish live access or rights."""

import copy
import io
import json
from datetime import date, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from fuel_oil import fetch_fuel_oil as f

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/fuel_oil"


class Response(io.BytesIO):
    status = 200

    def __init__(self, raw, content_type="text/csv"):
        super().__init__(raw)
        self.headers = {"Content-Type": content_type}


class FuelOilTests(unittest.TestCase):
    def fixture(self, name):
        return (FIX / name).read_bytes()

    def fx(self):
        return f.parse_fx(self.fixture("SYNTHETIC_fx_daily.csv"), "daily")

    def diesel(self):
        return f.parse_diesel_handoff(self.fixture("SYNTHETIC_diesel_handoff.csv"))

    def test_fx_definition_and_numeric(self):
        rows = self.fx()
        self.assertEqual(rows[0]["unit"], "USD_per_EUR")
        self.assertEqual(rows[0]["value"], 1.1)
        self.assertEqual(len(rows), 2)

    def test_fx_wrong_direction_units_key_and_country_currency(self):
        raw = self.fixture("SYNTHETIC_fx_daily.csv")
        for old, new in [
            (b"EXR.D.USD.EUR.SP00.A", b"EXR.D.EUR.USD.SP00.A"),
            (b",USD,EUR,", b",EUR,USD,"),
            (b",USD,0", b",EUR,0"),
            (b",A,USD,", b",M,USD,"),
            (b",1.1,A,", b",0,A,"),
        ]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                f.parse_fx(raw.replace(old, new), "daily")

    def test_missing_nonfinite_and_duplicates_rejected(self):
        raw = self.fixture("SYNTHETIC_fx_daily.csv")
        for value in (b"", b"NaN", b"inf", b"1e999"):
            with self.assertRaises(ValueError):
                f.parse_fx(raw.replace(b",1.1,A,", b"," + value + b",A,"), "daily")
        with self.assertRaisesRegex(ValueError, "Duplicate/revised"):
            f.parse_fx(raw + raw.splitlines()[1] + b"\n", "daily")

    def test_eia_pagination_completeness(self):
        pages = [self.fixture(f"SYNTHETIC_eia_page{i}.json") for i in range(2)]
        rows = f.combine_eia_pages(pages, [0, 2])
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[-1]["period"], "2020-03")
        for bad_pages, offsets in [
            (pages[:1], [0]),
            (pages, [0, 1]),
            (pages[::-1], [0, 2]),
        ]:
            with self.assertRaises(ValueError):
                f.combine_eia_pages(bad_pages, offsets)

    def test_eia_wrong_payload_total_series_units_frequency(self):
        p = json.loads(self.fixture("SYNTHETIC_eia_page0.json"))
        bads = [{"error": "key required"}, {"response": {"data": []}}]
        for key, value in [("frequency", "daily"), ("total", "unknown")]:
            bad = copy.deepcopy(p)
            bad["response"][key] = value
            bads.append(bad)
        for key, value in [("series", "RWTI"), ("units", "USD/litre"), ("value", None)]:
            bad = copy.deepcopy(p)
            bad["response"]["data"][0][key] = value
            bads.append(bad)
        for bad in bads:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                f.parse_eia_page(json.dumps(bad).encode())
        bad = copy.deepcopy(p)
        bad["response"]["data"].append(bad["response"]["data"][0])
        with self.assertRaises(ValueError):
            f.parse_eia_page(json.dumps(bad).encode())

    def test_eia_vintage_total_changed(self):
        a = self.fixture("SYNTHETIC_eia_page0.json")
        b = json.loads(self.fixture("SYNTHETIC_eia_page1.json"))
        b["response"]["total"] = "4"
        with self.assertRaisesRegex(ValueError, "total changed"):
            f.combine_eia_pages([a, json.dumps(b).encode()], [0, 2])

    def test_more_than_5000_observations_not_truncated(self):
        rows = [
            dict(
                period=(date(2010, 1, 1) + timedelta(days=i)).isoformat(),
                series="RBRTE",
                units="Dollars per Barrel",
                value="60",
            )
            for i in range(5001)
        ]
        pages = [
            json.dumps(
                {"response": {"frequency": "daily", "total": "5001", "data": part}}
            ).encode()
            for part in (rows[:5000], rows[5000:])
        ]
        self.assertEqual(len(f.combine_eia_pages(pages, [0, 5000], "daily")), 5001)
        with self.assertRaises(ValueError):
            f.combine_eia_pages(pages[:1], [0], "daily")

    def test_monthly_completeness_not_implied_by_api_total(self):
        rows = [
            dict(period=p, frequency="monthly", value=1)
            for p in ("2026-01", "2026-03", "2026-10")
        ]
        result = f.monthly_coverage(rows, "2026-01", "2026-03", date(2026, 10, 24))
        self.assertEqual(result["missing_months"], ["2026-02"])
        self.assertEqual(result["partial_or_future_months"], ["2026-10"])

    def test_diesel_grade_country_tax_and_unit(self):
        raw = self.fixture("SYNTHETIC_diesel_handoff.csv")
        self.assertEqual(self.diesel()[0]["eur_per_litre"], 1)
        for old, new in [
            (b"automotive_gas_oil", b"E10"),
            (b"automotive_gas_oil", b"Euro-super 95"),
            (b",DE,", b",FR,"),
            (b"with_taxes", b"without_taxes"),
            (b"EUR_per_1000_litres", b"EUR_per_litre"),
            (b"2019-12-30", b"2019-12-31"),
        ]:
            with self.assertRaises(ValueError):
                f.parse_diesel_handoff(raw.replace(old, new))

    def test_weekly_calendar_overlap_month_edges(self):
        out = f.weekly_monthly(self.diesel(), "2020-01", "2020-01", date(2020, 2, 1))[0]
        self.assertEqual(out["covered_days"], 31)
        self.assertAlmostEqual(
            out["value"], (5 * 1 + 7 * 1.1 + 7 * 1.2 + 7 * 1.3 + 5 * 1.4) / 31
        )
        self.assertEqual(out["quality"], "derived_weekly_overlap_approximation")

    def test_missing_week_no_fill_and_partial_month(self):
        rows = self.diesel()
        for subset, as_of in [
            (rows[:2] + rows[3:], date(2020, 2, 1)),
            (rows[1:], date(2020, 2, 1)),
            (rows, date(2020, 1, 30)),
        ]:
            self.assertIsNone(
                f.weekly_monthly(subset, "2020-01", "2020-01", as_of)[0]["value"]
            )
        with self.assertRaises(ValueError):
            f.weekly_monthly(rows + [rows[0]], "2020-01", "2020-01", date(2020, 2, 1))

    def daily_pairs(self):
        ds = [(date(2020, 1, 1) + timedelta(days=i)).isoformat() for i in range(15)]
        b = [
            dict(
                period=d,
                value=60 if i < 7 else 90,
                unit="USD_per_barrel",
                frequency="daily",
            )
            for i, d in enumerate(ds)
        ]
        x = [
            dict(
                period=d, value=1 if i < 7 else 2, unit="USD_per_EUR", frequency="daily"
            )
            for i, d in enumerate(ds)
        ]
        return b, x

    def test_daily_fx_alignment_not_ratio_of_monthly_means(self):
        b, x = self.daily_pairs()
        out = f.brent_eur_monthly(b, x, "2020-01", "2020-01", date(2020, 2, 1))[0]
        self.assertAlmostEqual(out["value"], (7 * 60 + 8 * 45) / 15)
        self.assertNotAlmostEqual(
            out["value"], sum(r["value"] for r in b) / sum(r["value"] for r in x)
        )

    def test_missing_days_partial_and_wrong_quote(self):
        b, x = self.daily_pairs()
        for bb, xx, as_of in [
            (b[:-1], x[:-1], date(2020, 2, 1)),
            (b, x[:-1], date(2020, 2, 1)),
            (b, x, date(2020, 1, 20)),
        ]:
            self.assertIsNone(
                f.brent_eur_monthly(bb, xx, "2020-01", "2020-01", as_of)[0]["value"]
            )
        x[0]["unit"] = "EUR_per_USD"
        with self.assertRaises(ValueError):
            f.brent_eur_monthly(b, x, "2020-01", "2020-01", date(2020, 2, 1))

    def test_redaction_urls_and_exception_text(self):
        key = "secret/key+value"
        text = f.redact(
            "https://api.example/?api_key=" + key + "&x=1 error " + key, (key,)
        )
        self.assertNotIn(key, text)
        self.assertNotIn("secret", text)
        self.assertNotIn("abc123", f.redact("api_key=abc123 unauthorized"))

    def test_request_redacts_error_and_no_auth_or_rate_retry(self):
        for code in (401, 403, 429):

            class Client:
                calls = 0

                def open(self, req, timeout):
                    self.calls += 1
                    raise urllib.error.HTTPError(
                        req.full_url, code, "key=SECRET", {}, None
                    )

            client = Client()
            raw, log = f.request(
                "https://example.org/?api_key=SECRET", ("SECRET",), client
            )
            self.assertIsNone(raw)
            self.assertEqual(client.calls, 1)
            self.assertNotIn("SECRET", json.dumps(log))
            self.assertEqual(log["status"], code)

    def test_transient_retry_bounded(self):
        class Client:
            calls = 0

            def open(self, req, timeout):
                self.calls += 1
                if self.calls == 1:
                    raise urllib.error.HTTPError(
                        req.full_url, 503, "transient", {}, None
                    )
                return Response(b"data", "text/csv; charset=utf-8")

        client = Client()
        with patch("time.sleep"):
            raw, rec = f.request("https://example.org/", opener=client)
        self.assertEqual(raw, b"data")
        self.assertEqual(rec["attempts"], 2)
        self.assertEqual(rec["content_type"], "text/csv")

    def test_credential_echo_and_wrong_content_type_refused(self):
        class Client:
            def open(self, req, timeout):
                return Response(b'{"api_key":"SECRET"}', "application/json")

        raw, rec = f.request("https://example.org/", ("SECRET",), Client())
        self.assertIsNone(raw)
        self.assertNotIn("SECRET", json.dumps(rec))
        for kind in ("fx", "eia", "wob"):
            with self.assertRaises(ValueError):
                f.validate_body(b"<html>error</html>", "text/html", kind, "monthly")

    def test_paging_fetch_records_total_and_offsets_without_secret(self):
        pages = [self.fixture(f"SYNTHETIC_eia_page{i}.json") for i in range(2)]
        urls = []

        def request(url, secrets):
            urls.append(url)
            return pages[len(urls) - 1], dict(
                url=f.redact(url, secrets),
                retrieved_at="2026-10-24T10:00:00Z",
                content_type="application/json",
                raw_sha256=f.sha(pages[len(urls) - 1]),
            )

        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(f, "request", side_effect=request),
        ):
            result, logs = f.fetch_eia("SECRET", tmp, page_size=2)
            self.assertEqual(result["retrieved_rows"], 3)
            self.assertEqual(result["page_offsets"], [0, 2])
            self.assertIn("offset=2", urls[-1])
            self.assertNotIn("SECRET", json.dumps(logs))
            self.assertNotIn(
                "SECRET",
                "".join(p.read_text() for p in Path(tmp).glob("*.manifest.json")),
            )

    def test_fetch_failure_no_success_result(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(f, "request", return_value=(None, {"error": "blocked"})),
        ):
            result, logs = f.fetch_eia("SECRET", tmp)
            self.assertIsNone(result)
            self.assertEqual(list(Path(tmp).iterdir()), [])
        with self.assertRaisesRegex(ValueError, "not set"):
            f.fetch_eia(None, "unused")

    def test_raw_hash_rights_and_fixture_boundaries(self):
        raw = b"SYNTHETIC"
        manifest = dict(
            raw_sha256=f.sha(raw),
            url="https://example.org/fixture",
            retrieved_at="2026-10-24T10:00:00Z",
            vintage="synthetic v1",
            synthetic_fixture=True,
        )
        rights = dict(
            private_analysis="synthetic_fixture",
            raw_redistribution="synthetic_fixture",
            derived_redistribution="synthetic_fixture",
            review_url="https://example.org/rights",
            review_note="synthetic only",
            attribution="Synthetic fixture",
        )
        f.check_snapshot(raw, manifest, rights, fixture=True)
        for bad in [
            dict(manifest, raw_sha256="0" * 64),
            dict(manifest, retrieved_at="2026-10-24"),
            dict(manifest, synthetic_fixture=False),
            dict(manifest, vintage=""),
        ]:
            with self.assertRaises(ValueError):
                f.check_snapshot(raw, bad, rights, fixture=True)
        with self.assertRaises(ValueError):
            f.check_snapshot(raw, manifest, rights)
        with self.assertRaises(ValueError):
            f.rights_gate(dict(rights, private_analysis="not_verified"))

    def test_private_permission_does_not_grant_redistribution(self):
        rights = dict(
            private_analysis="reviewed_permitted",
            raw_redistribution="not_verified",
            derived_redistribution="not_verified",
            review_url="https://example.org/terms",
            review_note="Private review only",
            attribution="Test source",
        )
        f.rights_gate(rights)
        for derived in (False, True):
            with self.assertRaises(ValueError):
                f.redistribution_gate(rights, derived)

    def test_immutable_raw_and_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            f.save_raw(b"abc", {"raw_sha256": f.sha(b"abc")}, tmp, "snapshot.csv")
            with self.assertRaises(FileExistsError):
                f.save_raw(b"other", {}, tmp, "snapshot.csv")
            for name in ("../escape.csv", "/tmp/escape.csv", "x/../../escape.csv"):
                with self.assertRaises(ValueError):
                    f.save_raw(b"abc", {}, tmp, name)
            self.assertEqual((Path(tmp) / "snapshot.csv").read_bytes(), b"abc")

    def test_xlsx_quarantine_never_numeric_admission(self):
        from openpyxl import Workbook

        stream = io.BytesIO()
        book = Workbook()
        book.active.append(["SYNTHETIC", 1000])
        book.save(stream)
        book.close()
        result = f.check_xlsx(stream.getvalue())
        self.assertFalse(result["numeric_observation_verified"])
        self.assertIn("quarantined", result["status"])
        with self.assertRaises(Exception):
            f.check_xlsx(b"not xlsx")

    def test_blocked_coverage_frozen_and_current_windows(self):
        sources = json.loads((f.DATA / "sources.json").read_text())
        report = f.blocked_coverage(sources)
        self.assertEqual(f.encoded(report), (f.DATA / "coverage.json").read_bytes())
        self.assertFalse(report["empirical_completion"])
        for s in report["series"]:
            self.assertEqual([w["expected_months"] for w in s["windows"]], [96, 105])
            self.assertEqual([w["observed_months"] for w in s["windows"]], [0, 0])
            self.assertFalse(s["admitted"])
        self.assertEqual(report["partial_2026_months_excluded"], ["2026-10"])
        self.assertEqual(f.encoded(report), f.encoded(f.blocked_coverage(sources)))


if __name__ == "__main__":
    unittest.main()
