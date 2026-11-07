import hashlib
import json
import unittest

from multibrand import data, fuel_tv, fuel_tv_trend


class FuelTvSavedResultsTest(unittest.TestCase):
    """Checks both saved time-varying runs without refitting."""

    def check(self, folder, protocol, expected):
        out = data.ROOT / folder
        man = json.loads((out / "manifest.json").read_text())
        proto = hashlib.sha256((data.ROOT / protocol).read_bytes()).hexdigest()
        self.assertEqual(proto, expected)
        self.assertEqual(man["protocol_sha256"], proto)
        for name, digest in man["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((out / name).read_bytes()).hexdigest(), digest, name)

    def test_saved_runs_and_reports(self):
        from scripts import multibrand_fuel_tv_report as rep
        self.check("results/multibrand_fuel_tv", "docs/MULTIBRAND_FUEL_TV_PROTOCOL.md", fuel_tv.PROTOCOL_SHA256)
        self.check("results/multibrand_fuel_tv_trend", "docs/MULTIBRAND_FUEL_TV_TREND_PROTOCOL.md",
                   fuel_tv_trend.PROTOCOL_SHA256)
        self.assertEqual((rep.V0 / "README.md").read_text(), rep.build_v0())
        self.assertEqual((rep.V1 / "README.md").read_text(), rep.build_v1())


if __name__ == "__main__":
    unittest.main()
