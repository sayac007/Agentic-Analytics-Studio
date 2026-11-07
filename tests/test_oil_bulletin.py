import datetime as dt
from decimal import Decimal
import tempfile
import unittest
from pathlib import Path

import openpyxl

from fuel_oil import oil_bulletin


def make_workbook(path, rows, unit="1000 l"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = oil_bulletin.SHEET
    ws.append(["title", "CTR", "DE_price_with_tax_euro95", "DE_price_with_tax_diesel", "FR_price_with_tax_euro95"])
    ws.append([None, None, "Euro-super 95", "Diesel", "Euro-super 95"])
    ws.append(["Date", None, unit, unit, unit])
    for row in rows:
        ws.append(row)
    wb.save(path)


class OilBulletinTest(unittest.TestCase):
    def test_calendar_day_weighting_without_filling(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / "wob.xlsx"
            # Mondays: 2026-01-26 covers Jan 26 - Feb 1; Feb 23 covers to Mar 1.
            make_workbook(book, [
                [dt.datetime(2026, 1, 26), "DE_", 1000, 1700, 9999],
                [dt.datetime(2026, 2, 2), "DE_", 2000, 1700, 9999],
                [dt.datetime(2026, 2, 9), "DE_", 2000, None, 9999],
                [dt.datetime(2026, 2, 16), "DE_", 2000, 1700, 9999],
                [dt.datetime(2026, 2, 23), "DE_", 2000, 1700, 9999],
            ])
            weekly = oil_bulletin.read_weekly(book)
            self.assertEqual(weekly[0]["euro95"], Decimal("1"))
            self.assertIsNone(weekly[2]["diesel"])
            months = oil_bulletin.monthly(weekly, "2026-01", "2026-03")
            self.assertEqual([m["period"] for m in months], ["2026-01", "2026-02", "2026-03"])
            # January: only Jan 26-31 covered -> no value
            self.assertEqual(months[0]["euro95_eur_per_litre"], "")
            self.assertEqual(months[0]["euro95_days_covered"], 6)
            # February: 1 day at 1.0 plus 27 days at 2.0 -> 55/28
            self.assertEqual(months[1]["euro95_eur_per_litre"], "1.9643")
            # One missing diesel week leaves February diesel empty
            self.assertEqual(months[1]["diesel_eur_per_litre"], "")
            self.assertEqual(months[1]["diesel_days_covered"], 21)
            self.assertEqual(months[2]["euro95_days_covered"], 1)
            self.assertEqual(months[2]["euro95_eur_per_litre"], "")

    def test_rejects_unexpected_unit(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / "wob.xlsx"
            make_workbook(book, [[dt.datetime(2026, 1, 5), "DE_", 1800, 1700, 1]], unit="t")
            with self.assertRaises(ValueError):
                oil_bulletin.read_weekly(book)

    def test_rejects_duplicate_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / "wob.xlsx"
            d = dt.datetime(2026, 1, 5)
            make_workbook(book, [[d, "DE_", 1800, 1700, 1], [d, "DE_", 1800, 1700, 1]])
            with self.assertRaises(ValueError):
                oil_bulletin.read_weekly(book)


if __name__ == "__main__":
    unittest.main()
