"""Rebuild attributed table fixtures, excluding cover images and drawings.

python -m kba.fixtures --raw-dir CACHE --output NEW_DIRECTORY
These are transformed test files, never original downloads or benchmark inputs.
"""

import argparse
import copy
import io
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile
from .extract import sha
from .pipeline import catalog, encoded

PERIODS = {"2018-01", "2020-01", "2022-05", "2024-08", "2025-01", "2025-06", "2025-12"}


def table_only(raw):
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as src, zipfile.ZipFile(out, "w") as dst:
        for name in sorted(src.namelist()):
            if name.startswith(("xl/media/", "xl/drawings/")):
                continue
            b = src.read(name)
            if name.endswith(".rels"):
                root = ET.fromstring(b)
                for child in list(root):
                    if child.get("Type", "").endswith(("/drawing", "/image")):
                        root.remove(child)
                b = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            elif name.startswith("xl/worksheets/") and name.endswith(".xml"):
                # Preserve cell XML bytes; remove only drawing tags.
                import re

                b = re.sub(rb"<(?:\w+:)?drawing\b[^>]*/>", b"", b)
            elif name == "[Content_Types].xml":
                root = ET.fromstring(b)
                for child in list(root):
                    if child.get("PartName", "").startswith("/xl/drawings/"):
                        root.remove(child)
                b = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            zi = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            dst.writestr(zi, b)
    return out.getvalue()


def build(catalog_path, raw_dir, output):
    c = copy.deepcopy(catalog(catalog_path))
    c["catalog_scope"] = "table_only_test_fixtures"
    c["sources"] = [r for r in c["sources"] if r["period"] in PERIODS]
    root = Path(output)
    root.mkdir(parents=True, exist_ok=False)
    for r in c["sources"]:
        raw = (Path(raw_dir) / r["file"]).read_bytes()
        if sha(raw) != r["sha256"]:
            raise ValueError("Original source hash mismatch")
        if r["file"].endswith(".xlsx"):
            r["original_source_sha256"] = r["sha256"]
            raw = table_only(raw)
            r["fixture_transformation"] = (
                "Cover media/drawings removed; table cells unchanged; not original download"
            )
            r["sha256"] = sha(raw)
            r["bytes"] = len(raw)
        (root / r["file"]).write_bytes(raw)
    shutil.copyfile(
        Path(raw_dir) / c["license_evidence"]["file"],
        root / c["license_evidence"]["file"],
    )
    (root / "sources.json").write_bytes(encoded(c))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", default="data/kba/sources.json")
    p.add_argument("--raw-dir", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    build(a.catalog, a.raw_dir, a.output)
