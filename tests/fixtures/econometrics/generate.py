"""Create one deterministic, explicitly fictional CLI fixture outside the checkout."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def generate(root):
    from attention.import_trends import periods, sha
    import numpy as np

    if root.exists():
        raise ValueError("Fixture directory must be new")
    root.mkdir(parents=True)
    raw = ROOT / "tests/fixtures/trends/SYNTHETIC_extended.csv"
    meta = ROOT / "tests/fixtures/trends/SYNTHETIC_extended_metadata.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "attention.import_trends",
            "--csv",
            str(raw),
            "--metadata",
            str(meta),
            "--output-dir",
            str(root / "import"),
            "--fixture",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    kba = root / "SYNTHETIC_kba.csv"
    with kba.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["period", "value", "series", "source", "vintage", "powertrain"])
        for t, p in enumerate(periods()):
            mm = int(p[5:])
            value = round(
                2000
                + 8 * t
                + 150 * np.sin(2 * np.pi * t / 12)
                + 220 * (mm in (3, 6, 9, 12))
                + 30 * np.cos(1.7 * t)
                + 15 * np.sin(0.31 * t)
            )
            w.writerow(
                [
                    p,
                    value,
                    "brand:TESLA",
                    "synthetic_fixture",
                    "synthetic_fixture",
                    "all",
                ]
            )
    record = {
        "origin": "synthetic",
        "status": "synthetic_fixture_only",
        "raw_sha256": sha(raw.read_bytes()),
        "metadata_sha256": sha(meta.read_bytes()),
        "kba_sha256": sha(kba.read_bytes()),
        "protocol_sha256": sha(
            (ROOT / "docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md").read_bytes()
        ),
    }
    (root / "SYNTHETIC_admission.json").write_text(json.dumps(record, indent=2) + "\n")
    return raw, meta, root / "import", root / "SYNTHETIC_admission.json", kba


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    generate(p.parse_args().output)
