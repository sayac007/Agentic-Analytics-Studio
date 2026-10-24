"""Generate explicitly SYNTHETIC study-interface fixtures, never official values."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import random

GAPS = [
    "2018-04",
    "2018-12",
    "2019-01",
    "2019-04",
    "2019-12",
    "2020-01",
    "2020-04",
    "2020-12",
    "2021-01",
    "2021-04",
    "2021-12",
    "2022-01",
    "2022-04",
]


def encode(value):
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def generate(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    energy = root / "energy"
    permits = root / "permits"
    energy.mkdir()
    permits.mkdir()
    rng = random.Random(19103)
    periods = [
        f"{year}-{month:02d}" for year in range(2018, 2026) for month in range(1, 13)
    ]
    y = [
        max(
            0,
            round(
                650
                + 8 * i
                + 140 * math.sin(2 * math.pi * (i % 12) / 12)
                + rng.gauss(0, 70)
            ),
        )
        for i in range(96)
    ]
    fx = [
        1.1 + 0.0005 * i + 0.06 * math.sin(i / 8) + rng.gauss(0, 0.008)
        for i in range(96)
    ]
    diesel = [
        1.3 + 0.003 * i + 0.08 * math.sin(i / 10) + rng.gauss(0, 0.025)
        for i in range(96)
    ]
    with (root / "SYNTHETIC_kba.csv").open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["period", "value", "series", "source", "vintage", "powertrain"])
        for p, v in zip(periods, y):
            w.writerow([p, v, "brand:TESLA", "SYNTHETIC", "SYNTHETIC", "all"])
    meta = {}
    native_hash = {}
    monthly_hash = None
    for id, key, unit in [
        ("eurusd", "EXR.M.USD.EUR.SP00.A", "USD_per_EUR"),
        ("diesel_de", "DE_price_with_tax_diesel", "EUR_per_1000_litres"),
    ]:
        raw = ("SYNTHETIC study-interface raw " + id + " v1\n").encode()
        name = f"SYNTHETIC_{id}.raw"
        (energy / name).write_bytes(raw)
        meta[id] = {"raw_file": name, "raw_sha256": sha(raw)}
        rows = (
            [
                {
                    "period": p,
                    "value": v,
                    "unit": unit,
                    "frequency": "monthly",
                    "series_id": key,
                }
                for p, v in zip(periods, fx)
            ]
            if id == "eurusd"
            else [
                {
                    "period": "2017-12-25",
                    "value": 1300,
                    "unit": unit,
                    "frequency": "weekly",
                    "series_id": key,
                }
            ]
        )
        b = encode(
            {
                "scope": "SYNTHETIC_FIXTURE_ONLY",
                "raw_sha256": sha(raw),
                "observations": rows,
            }
        )
        (energy / (id + ".quarantined.json")).write_bytes(b)
        native_hash[id] = sha(b)
        if id == "diesel_de":
            monthly = [
                {
                    "period": p,
                    "value": None if p in GAPS else v,
                    "unit": "EUR_per_litre",
                    "partial": False,
                    "quality": "SYNTHETIC monthly approximation",
                }
                for p, v in zip(periods, diesel)
            ]
            b = encode(
                {
                    "scope": "SYNTHETIC_FIXTURE_ONLY",
                    "raw_sha256": sha(raw),
                    "observations": monthly,
                }
            )
            (energy / "diesel_de.monthly_approx.quarantined.json").write_bytes(b)
            monthly_hash = sha(b)
    manifest = encode(
        {
            "scope": "SYNTHETIC_FIXTURE_ONLY",
            "sources": meta,
            "kba_sha256": sha((root / "SYNTHETIC_kba.csv").read_bytes()),
        }
    )
    (energy / "fixture_manifest.json").write_bytes(manifest)
    for id, key, unit in [
        ("eurusd", "EXR.M.USD.EUR.SP00.A", "USD_per_EUR"),
        ("diesel_de", "DE_price_with_tax_diesel", "EUR_per_1000_litres"),
    ]:
        a = {
            "scope": "SYNTHETIC_FIXTURE_ONLY",
            "source_id": id,
            "series_id": key,
            "unit": unit,
            "raw_sha256": meta[id]["raw_sha256"],
            "native_normalized_sha256": native_hash[id],
            "fixture_manifest_sha256": sha(manifest),
        }
        if id == "diesel_de":
            a.update(monthly_approx_sha256=monthly_hash, missing_months=GAPS)
        (permits / (id + ".admission.json")).write_bytes(encode(a))
    return root


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    generate(a.output)
