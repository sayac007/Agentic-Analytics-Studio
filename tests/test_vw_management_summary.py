"""Every key number quoted in the Volkswagen management summary must follow from the repo's data/results."""
import csv
import math
import unittest
from pathlib import Path

from scripts import vw_summary_figure as fig

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "docs/management-summary-volkswagen/README.md").read_text(encoding="utf-8")


def de(v, digits=1):
    return f"{v:.{digits}f}".replace(".", ",")


def thousands(n):
    return f"{n:,}".replace(",", ".")


def pct(log_points):
    v = round((math.exp(log_points) - 1) * 100)
    return f"{'+' if v >= 0 else '−'}{abs(v)} %"


def coef(eq, term):
    with (ROOT / "results/multibrand/coefficients.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["spec"] == "primary" and r["equation"] == eq and r["term"] == term:
                return r
    raise KeyError((eq, term))


class VwSummaryNumbersTest(unittest.TestCase):
    def test_annual_shares_and_counts(self):
        s = fig.annual_shares()
        self.assertIn(thousands(s["2026"]["VW-Konzern"][0]), DOC)
        self.assertIn(thousands(s["2025"]["VW-Konzern"][0]), DOC)
        self.assertIn(thousands(s["2026"]["VW-Konzern"][1]), DOC)
        self.assertIn(de(s["2025"]["VW-Konzern"][2]) + " %", DOC)
        self.assertIn(de(s["2026"]["VW-Konzern"][2]) + " %", DOC)
        self.assertIn(de(s["2025"]["Tesla"][2]) + " %", DOC)
        self.assertIn(de(s["2026"]["Tesla"][2]) + " %", DOC)

    def test_policy_table_matches_model(self):
        rows = {"innovation_premium": "Innovationsprämie", "grant_2023_all": "Umweltbonus reduziert, alle Käufer",
                "grant_2023_private": "Umweltbonus nur Privatkunden", "pre_cut_2022_12": "Vorziehmonat vor Kürzung",
                "pre_business_end_2023_08": "Vorziehmonat vor Ende Gewerbeförderung",
                "tax_package_2025_07": "Steuerpaket", "grant_2026": "E-Auto-Förderung 2026"}
        lines = DOC.splitlines()
        for term, label in rows.items():
            line = next(l for l in lines if l.startswith(f"| {label}"))
            for eq in ("log_market", "alr_VW_Group"):
                r = coef(eq, term)
                status = "gesichert" if r["excludes_zero"] == "True" else "nicht gesichert"
                self.assertIn(f"{pct(float(r['median']))}, {status}", line, (term, eq))

    def test_quarter_end_and_fuel(self):
        self.assertIn("+0,71", DOC)
        self.assertEqual(round(float(coef("alr_Tesla", "quarter_end")["median"]), 2), 0.71)
        self.assertEqual(round(float(coef("alr_VW_Group", "quarter_end")["median"]), 2), -0.09)
        with (ROOT / "results/multibrand/irf_fuel_shock.csv").open(newline="") as fh:
            r = next(r for r in csv.DictReader(fh) if r["spec"] == "primary" and r["variable"] == "alr_VW_Group"
                     and r["h"] == "cum_0_11")
        self.assertIn(f"−{de(-float(r['median']), 2)} Log-Punkte, Intervall −{de(-float(r['lower95']), 2)} "
                      f"bis +{de(float(r['upper95']), 2)}", DOC)

    def test_october_forecast(self):
        with (ROOT / "results/multibrand/predictions.csv").open(newline="") as fh:
            r = next(r for r in csv.DictReader(fh) if r["spec"] == "primary" and r["outcome"] == "VW_Group"
                     and r["target"] == "2026-10" and r["horizon"] == "1")
        self.assertIn(thousands(round(float(r["prediction_median"]))), DOC)
        self.assertIn(thousands(int(float(r["actual"]))), DOC)


if __name__ == "__main__":
    unittest.main()
