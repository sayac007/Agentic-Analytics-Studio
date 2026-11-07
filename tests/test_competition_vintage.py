import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "data" / "competition"
VINTAGE = ROOT / "data" / "competition_vintage_2026_11"


class CompetitionVintageTest(unittest.TestCase):
    """The newer KBA vintage must extend, never rewrite, the frozen Task 04 inputs."""

    def test_panel_prefix_identical(self):
        old = (FROZEN / "brand_monthly_2021_2026.csv").read_text(encoding="utf-8").splitlines()
        new = (VINTAGE / "brand_monthly_2021_2026_10.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(new[:len(old)], old)
        added = {line.split(",")[0] for line in new[len(old):]}
        self.assertEqual(added, {"2026-10"})

    def test_catalog_and_checks_extend_frozen(self):
        for name in ("kba_sources.json", "kba_checks.json"):
            old = json.loads((FROZEN / name).read_text())
            new = json.loads((VINTAGE / name).read_text())
            old_items = old["sources"] if name == "kba_sources.json" else old
            new_items = new["sources"] if name == "kba_sources.json" else new
            self.assertEqual(new_items[:len(old_items)], old_items, name)
            self.assertEqual(len(new_items), len(old_items) + 1, name)

    def test_october_market_total(self):
        checks = json.loads((VINTAGE / "kba_checks.json").read_text())
        october = [c for c in checks if c["period"] == "2026-10"]
        self.assertEqual(len(october), 1)
        self.assertEqual(october[0]["market_total"]["monthly_electric"], 94086)


if __name__ == "__main__":
    unittest.main()
