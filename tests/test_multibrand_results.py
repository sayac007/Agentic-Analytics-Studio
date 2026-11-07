import csv
import hashlib
import json
import unittest
from pathlib import Path

from multibrand import data, study

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/multibrand"


class MultibrandResultsTest(unittest.TestCase):
    """Checks the saved run without refitting."""

    def setUp(self):
        self.manifest = json.loads((OUT / "manifest.json").read_text())

    def test_protocol_and_hashes(self):
        proto = hashlib.sha256((ROOT / "docs/MULTIBRAND_BVAR_PROTOCOL.md").read_bytes()).hexdigest()
        self.assertEqual(proto, study.PROTOCOL_SHA256)
        self.assertEqual(self.manifest["protocol_sha256"], proto)
        for name, digest in self.manifest["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((OUT / name).read_bytes()).hexdigest(), digest, name)
        self.assertEqual(self.manifest["inputs_sha256"], data.inputs_sha256())

    def test_comparator_actuals_match_task04(self):
        with (OUT / "predictions.csv").open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        m2 = {(r["target"], r["horizon"], r["outcome"]): float(r["actual"]) for r in rows if r["spec"] == "M2"}
        prim = [r for r in rows if r["spec"] == "primary" and (r["target"], r["horizon"], r["outcome"]) in m2]
        self.assertEqual(len(prim), 2 * (21 + 19))
        for r in prim:
            self.assertEqual(float(r["actual"]), m2[(r["target"], r["horizon"], r["outcome"])])

    def test_report_matches_saved_results(self):
        from scripts import multibrand_report
        self.assertEqual((OUT / "README.md").read_text(), multibrand_report.build())


if __name__ == "__main__":
    unittest.main()
