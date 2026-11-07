"""Eurostat HICP (prc_hicp_minr, ECOICOP ver. 2) monthly indices for Germany.

Parses the JSON-stat 2.0 responses of the Eurostat dissemination API for unit
I25 (index 2025=100) and writes ``data/hicp_de/monthly.csv``. No rebasing,
no filling. Source: Eurostat (CC BY 4.0); own selection.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

API = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr"
       "?format=JSON&geo=DE&coicop18={code}&sinceTimePeriod=2018-01")
SERIES = {"electricity": "CP0451", "new_cars": "CP07111", "all_items": "TOTAL"}
UNIT = "I25"


def parse(payload, code):
    ids, size = payload["id"], payload["size"]
    cats = [sorted(payload["dimension"][k]["category"]["index"].items(), key=lambda x: x[1]) for k in ids]
    if list(payload["dimension"]["coicop18"]["category"]["index"]) != [code]:
        raise ValueError("Unexpected COICOP in response")
    if list(payload["dimension"]["geo"]["category"]["index"]) != ["DE"]:
        raise ValueError("Unexpected geography")
    stride = [1] * len(size)
    for i in range(len(size) - 2, -1, -1):
        stride[i] = stride[i + 1] * size[i + 1]
    out = {}
    for key, value in payload["value"].items():
        k, coords = int(key), []
        for s in stride:
            coords.append(k // s)
            k %= s
        labels = {ids[j]: cats[j][coords[j]][0] for j in range(len(ids))}
        if labels["unit"] == UNIT:
            if labels["time"] in out:
                raise ValueError("Duplicate period")
            out[labels["time"]] = value
    return dict(sorted(out.items()))


def run(raw_dir, output):
    raw_dir, output = Path(raw_dir), Path(output)
    series, hashes = {}, {}
    for name, code in SERIES.items():
        path = raw_dir / f"minr_{code}.json"
        hashes[code] = hashlib.sha256(path.read_bytes()).hexdigest()
        series[name] = parse(json.loads(path.read_text()), code)
    periods = sorted(set().union(*series.values()))
    output.mkdir(parents=True, exist_ok=True)
    with (output / "monthly.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["period"] + [f"{n}_index_2025" for n in SERIES])
        for p in periods:
            w.writerow([p] + [series[n].get(p, "") for n in SERIES])
    return {"raw_sha256": hashes, "periods": [periods[0], periods[-1]],
            "last_complete": {n: max(s) for n, s in series.items()},
            "monthly_sha256": hashlib.sha256((output / "monthly.csv").read_bytes()).hexdigest()}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--raw-dir", required=True)
    p.add_argument("--output", default="data/hicp_de")
    a = p.parse_args()
    print(json.dumps(run(a.raw_dir, a.output), indent=2))
