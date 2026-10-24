"""Actual-format adapters tested with synthetic values; no original uploads in CI."""

from datetime import date
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import openpyxl
from fuel_oil import import_energy as e

FIX = Path(__file__).resolve().parent / "fixtures/energy_import"


class EnergyImportTests(unittest.TestCase):
    def raws(self):
        return {
            k: (FIX / name).read_bytes()
            for k, name in {
                "eurusd": "SYNTHETIC_ecb.csv",
                "brent_usd": "SYNTHETIC_brent.xls",
                "diesel_de": "SYNTHETIC_diesel.xlsx",
            }.items()
        }

    def mutated_wob(self, cell, value):
        b = openpyxl.load_workbook(io.BytesIO(self.raws()["diesel_de"]))
        b.active[cell] = value
        out = io.BytesIO()
        b.save(out)
        b.close()
        return out.getvalue()

    def test_inspection_has_no_observed_values(self):
        inventory = e.inspect_inputs(self.raws())
        self.assertEqual(inventory["diesel_de"]["price_column"], "BD")
        self.assertEqual(inventory["brent_usd"]["series_id"], "RBRTE")
        self.assertEqual(inventory["eurusd"]["columns"], 3)
        self.assertNotIn("observations", json.dumps(inventory))

    def test_ecb_native_portal_shape_dates_units_unknown_flags(self):
        rows = e.parse_fx(self.raws()["eurusd"])
        self.assertEqual(rows[0]["value"], 1.1)
        self.assertEqual(rows[0]["unit"], "USD_per_EUR")
        self.assertIsNone(rows[0]["source_status"])
        self.assertEqual(rows[0]["original_date"], "2018-01-31")

    def test_ecb_wrong_key_quote_label_status(self):
        raw = self.raws()["eurusd"]
        for old, new in [
            (b"EXR.M.USD.EUR", b"EXR.M.EUR.USD"),
            (b"EXR.M.", b"EXR.D."),
            (b"2018Jan", b"2018Feb"),
            (b"2018-01-31", b"2018-01-30"),
            (b"1.1", b"nan"),
        ]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                e.parse_fx(raw.replace(old, new))

    def test_ecb_duplicate_and_censored_never_filled(self):
        raw = self.raws()["eurusd"]
        with self.assertRaises(ValueError):
            e.parse_fx(raw + raw.splitlines()[1] + b"\n")
        rows = e.parse_fx(raw.replace(b"1.1", b"..."))
        self.assertIsNone(rows[0]["value"])
        cov = e.coverage(rows, "2018-01", "2018-02", date(2026, 10, 24))
        self.assertEqual(cov["censored_or_missing_value_months"], 1)
        self.assertIsNone(cov["revised_months"])

    def test_native_xls_monthly_brent(self):
        rows = e.parse_brent(self.raws()["brent_usd"])
        self.assertEqual(rows[0]["series_id"], "RBRTE")
        self.assertEqual(rows[0]["unit"], "USD_per_barrel")
        self.assertEqual(rows[0]["value"], 10)
        self.assertEqual(rows[0]["period"], "2018-01")

    def test_wrong_xls_container_series_and_units(self):
        raw = self.raws()["brent_usd"]
        for bad in (
            b"<html>error</html>",
            self.raws()["diesel_de"],
            raw.replace(b"RBRTE", b"RWTI!"),
            raw.replace(b"Dollars per Barrel", b"Euroooo per Litre!"),
        ):
            with self.assertRaises((ValueError, e.xlrd.XLRDError)):
                e.parse_brent(bad)

    def test_xls_annual_summary_or_footnote_fails(self):
        raw = self.raws()["brent_usd"]
        b, c, s = e.open_eia(raw)
        original = s.cell

        def cell(row, col):
            if row == 3 and col == 0:
                import xlrd

                return xlrd.sheet.Cell(xlrd.XL_CELL_TEXT, "Annual total")
            return original(row, col)

        with (
            patch.object(e, "open_eia", return_value=(b, c, s)),
            patch.object(s, "cell", side_effect=cell),
        ):
            with self.assertRaises(ValueError):
                e.parse_brent(raw)

    def test_wob_actual_country_grade_tax_volume_shape(self):
        rows = e.parse_diesel(self.raws()["diesel_de"])
        self.assertEqual(rows[0]["grade"], "automotive_gas_oil")
        self.assertEqual(rows[0]["taxes"], "with_taxes")
        self.assertEqual(rows[0]["unit"], "currency_not_explicit_per_1000_litres")
        self.assertNotIn("eur_per_litre", rows[0])

    def test_user_cited_unit_convention_requires_independent_mapping(self):
        evidence = {
            "unit": "EUR_per_1000_litres",
            "basis": "user_attested_official_convention_and_independently_verified_mapping",
            "citation": "https://eur-lex.europa.eu/eli/dec/1999/566/oj/eng/pdf",
        }
        rows = e.parse_diesel(self.raws()["diesel_de"], evidence)
        self.assertEqual(rows[0]["value"], 1000)
        self.assertEqual(rows[0]["unit"], "EUR_per_1000_litres")
        self.assertEqual(rows[0]["eur_per_litre"], 1)
        with self.assertRaises(ValueError):
            e.parse_diesel(
                self.mutated_wob("BD1", "FR_price_with_tax_diesel"), evidence
            )
        with self.assertRaises(ValueError):
            e.parse_diesel(
                self.raws()["diesel_de"], dict(evidence, unit="EUR_per_litre")
            )

    def test_wob_wrong_grade_country_tax_unit_or_date(self):
        for cell, value in [
            ("BD1", "FR_price_with_tax_diesel"),
            ("BD2", "Euro-super 95 (I)"),
            ("BD3", "t"),
            ("A1", "Prices without taxes"),
            ("BB4", "FR_"),
            ("A4", "not a date"),
        ]:
            with self.subTest(cell=cell), self.assertRaises(ValueError):
                e.parse_diesel(self.mutated_wob(cell, value))

    def test_wob_duplicate_and_missing_week(self):
        rows = e.parse_diesel(self.raws()["diesel_de"])
        with self.assertRaises(ValueError):
            e.parse_diesel(self.mutated_wob("A5", date(2017, 12, 25)))
        full = e.coverage(rows, "2018-01", "2018-01", date(2026, 10, 24))
        missing = e.coverage(
            rows[:3] + rows[4:], "2018-01", "2018-01", date(2026, 10, 24)
        )
        self.assertEqual(full["observed_months"], 1)
        self.assertEqual(missing["observed_months"], 0)
        self.assertEqual(missing["missing_periods"], ["2018-01"])

    def test_partial_october_not_complete_or_admitted(self):
        rows = e.parse_fx(self.raws()["eurusd"])
        cov = e.coverage(rows, "2026-10", "2026-10", date(2026, 10, 24))
        self.assertEqual(cov["partial_months"], 1)
        self.assertEqual(cov["observed_months"], 0)
        self.assertEqual(cov["admitted_months"], 0)

    def test_output_isolation_no_overwrite_and_determinism(self):
        paths = {
            k: FIX / name
            for k, name in {
                "eurusd": "SYNTHETIC_ecb.csv",
                "brent_usd": "SYNTHETIC_brent.xls",
                "diesel_de": "SYNTHETIC_diesel.xlsx",
            }.items()
        }
        with self.assertRaises(ValueError):
            e.run(
                paths,
                e.ROOT / "artifacts/not-private",
                date(2026, 10, 24),
                [],
                fixture=True,
            )
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / "a", Path(temp) / "b"
            e.run(paths, a, date(2026, 10, 24), [], fixture=True)
            e.run(paths, b, date(2026, 10, 24), [], fixture=True)
            for name in [
                "summary.json",
                "inventory.json",
                "eurusd.quarantined.json",
                "brent_usd.quarantined.json",
                "diesel_de.quarantined.json",
            ]:
                self.assertEqual((a / name).read_bytes(), (b / name).read_bytes())
            with self.assertRaises(ValueError):
                e.run(paths, a, date(2026, 10, 24), [], fixture=True)
            summary = json.loads((a / "summary.json").read_text())
            self.assertTrue(all(not r["admitted"] for r in summary["series"]))
            self.assertNotIn(str(temp), json.dumps(summary))

    def test_bad_metadata_fails_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            paths = {
                k: FIX / name
                for k, name in {
                    "eurusd": "SYNTHETIC_ecb.csv",
                    "brent_usd": "SYNTHETIC_brent.xls",
                    "diesel_de": "SYNTHETIC_diesel.xlsx",
                }.items()
            }
            bad = Path(temp) / "bad.csv"
            bad.write_bytes(b"invalid")
            paths["eurusd"] = bad
            with self.assertRaises(ValueError):
                e.run(paths, out, date(2026, 10, 24), [], fixture=True)
            self.assertFalse(out.exists())

    def test_original_hash_drift_and_fixture_real_boundary(self):
        paths = {
            k: FIX / name
            for k, name in {
                "eurusd": "SYNTHETIC_ecb.csv",
                "brent_usd": "SYNTHETIC_brent.xls",
                "diesel_de": "SYNTHETIC_diesel.xlsx",
            }.items()
        }
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "out"
            with self.assertRaisesRegex(ValueError, "hash drift"):
                e.run(paths, out, date(2026, 10, 24), [])
            self.assertFalse(out.exists())
            changed = Path(temp) / "SYNTHETIC_ecb.csv"
            changed.write_bytes(paths["eurusd"].read_bytes().replace(b"1.1", b"9.9"))
            paths["eurusd"] = changed
            with self.assertRaisesRegex(ValueError, "hash drift"):
                e.run(paths, out, date(2026, 10, 24), [], fixture=True)
            self.assertFalse(out.exists())

    def test_copyright_notice_and_source_country_flags_fail_closed(self):
        raw = self.mutated_wob("B1115", "No licence claim")
        b = openpyxl.load_workbook(io.BytesIO(raw))
        b.active["B1117"] = "No licence claim"
        stream = io.BytesIO()
        b.save(stream)
        b.close()
        with self.assertRaisesRegex(ValueError, "notice"):
            e.parse_diesel(stream.getvalue())

    def test_eia_duplicate_month_refused(self):
        raw = self.raws()["brent_usd"]
        b, c, s = e.open_eia(raw)
        original = s.cell

        def cell(row, col):
            return original(3, 0) if row == 4 and col == 0 else original(row, col)

        with (
            patch.object(e, "open_eia", return_value=(b, c, s)),
            patch.object(s, "cell", side_effect=cell),
        ):
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                e.parse_brent(raw)


if __name__ == "__main__":
    unittest.main()
