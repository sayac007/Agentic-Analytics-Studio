"""Offline KBA checks use attributed real source snapshots, never invented history."""

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import openpyxl

from kba.extract import count, month, parse, periods, publication, sha
from kba.pipeline import (
    admission,
    audit,
    catalog,
    coverage,
    describe,
    extract,
    fetch,
    local,
    official,
    run,
    reconcile,
    select,
    validate_rows,
    verify,
)

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests/fixtures/kba"
CAT = FIX / "sources.json"
PLAN = ROOT / "data/kba/acquisition-plan.json"


class KbaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = catalog(CAT)
        cls.sources = {r["period"]: r for r in cls.c["sources"]}
        cls.plan = json.loads(PLAN.read_text())

    def record(self, period="2025-01"):
        return copy.deepcopy(self.sources[period])

    def altered(self, changes, period="2025-01"):
        r = self.record(period)
        w = openpyxl.load_workbook(FIX / r["file"])
        for sheet, cell, value in changes:
            w[sheet][cell] = value
        b = io.BytesIO()
        w.save(b)
        raw = b.getvalue()
        r["sha256"] = sha(raw)
        return raw, r

    def test_all_representative_profiles_and_exact_tesla_values(self):
        expected = {"2018-01": 63, "2020-01": 367, "2025-01": 1277}
        for period, r in self.sources.items():
            with self.subTest(period=period):
                parsed = parse((FIX / r["file"]).read_bytes(), r)
                self.assertEqual(parsed["sheet"], r["sheet"])
                values = {o["series"]: o["value"] for o in parsed["observations"]}
                if period in expected:
                    self.assertEqual(values["brand:TESLA"], expected[period])
                self.assertEqual("market:BEV" in values, period >= "2021-01")
        p = parse((FIX / "2025-01.xlsx").read_bytes(), self.record())
        self.assertEqual(
            next(o["value"] for o in p["observations"] if o["series"] == "market:BEV"),
            34498,
        )

    def test_shifted_august_profile_is_explicit(self):
        r = self.record("2024-08")
        raw = (FIX / r["file"]).read_bytes()
        parse(raw, r)
        r["parser_profile"] = "fz10-xlsx-bev-v1"
        with self.assertRaises(ValueError):
            parse(raw, r)

    def test_unknown_profile_or_sheet_fails(self):
        r = self.record()
        r["parser_profile"] = "guess"
        with self.assertRaises(KeyError):
            parse((FIX / r["file"]).read_bytes(), r)
        raw, r = self.altered([])
        w = openpyxl.load_workbook(io.BytesIO(raw))
        w[r["sheet"]].title = "Unknown"
        b = io.BytesIO()
        w.save(b)
        r["sha256"] = sha(b.getvalue())
        with self.assertRaises(ValueError):
            parse(b.getvalue(), r)

    def test_month_title_and_monthly_column_are_all_checked(self):
        for cell in ["B6", "D9", "AK9"]:
            with self.subTest(cell=cell):
                raw, r = self.altered([("FZ 10.1", cell, "Februar 2025")])
                with self.assertRaises(ValueError):
                    parse(raw, r)

    def test_exact_brand_identity_no_model_or_similar_brand(self):
        for cell, value in [("B394", "TESLAX ZUSAMMEN"), ("C394", "MODEL Y")]:
            raw, r = self.altered([("FZ 10.1", cell, value)])
            with self.assertRaises(ValueError):
                parse(raw, r)

    def test_bev_cannot_be_total_or_phev(self):
        for v in ["mit Elektroantrieb", "mit Plug-in-Hybridantrieb", "Insgesamt"]:
            raw, r = self.altered([("FZ 10.1", "AK8", v)])
            with self.assertRaises(ValueError):
                parse(raw, r)

    def test_non_numeric_tesla_not_zero_filled(self):
        raw, r = self.altered([("FZ 10.1", "D394", "-")])
        p = parse(raw, r)
        self.assertNotIn("brand:TESLA", [o["series"] for o in p["observations"]])
        self.assertTrue(any(e["cell"] == "D394" for e in p["exclusions"]))
        for v in [True, -1, 1.25, "NaN", "1 277", "=1+2"]:
            raw, r = self.altered([("FZ 10.1", "D394", v)])
            with self.assertRaises(ValueError):
                parse(raw, r)

    def test_duplicate_brand_and_market_total_fail(self):
        for name in ["TESLA ZUSAMMEN", "NEUZULASSUNGEN INSGESAMT"]:
            raw, r = self.altered(
                [
                    ("FZ 10.1", "B450", name),
                    ("FZ 10.1", "D450", 1),
                    ("FZ 10.1", "AK450", 1),
                ]
            )
            with self.assertRaises(ValueError):
                parse(raw, r)

    def test_raw_and_license_hashes(self):
        r = self.record()
        raw = (FIX / r["file"]).read_bytes()
        with self.assertRaises(ValueError):
            parse(raw + b"changed", r)
        c = copy.deepcopy(self.c)
        c["license_evidence"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "c.json"
            p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                catalog(p)

    def test_publication_precision_and_corrected_vintage(self):
        self.assertEqual(publication("Februar 2025")["precision"], "month")
        self.assertEqual(publication("7. Juli 2025")["value"], "2025-07-07")
        self.assertEqual(publication(None)["precision"], "unknown")
        r = self.record("2025-06")
        p = parse((FIX / r["file"]).read_bytes(), r)
        self.assertEqual(p["revision"]["value"], "2025-07-21")
        r = self.record("2022-05")
        p = parse((FIX / r["file"]).read_bytes(), r)
        self.assertEqual(p["publication"]["value"], "2022-06")
        self.assertEqual(p["publication"]["precision"], "month")

    def test_month_validation(self):
        self.assertEqual(
            periods("2023-12", "2024-02"), ["2023-12", "2024-01", "2024-02"]
        )
        for v in [
            "2024-00",
            "2024-13",
            "0000-01",
            "2024-1",
            "2024-01\n",
            "２０２４-01",
        ]:
            with self.assertRaises(ValueError):
                month(v)

    def test_count_validation(self):
        self.assertEqual(count(123.0), 123)
        for v in [None, "-", 0.1, -1, float("nan"), float("inf"), True]:
            with self.assertRaises(ValueError):
                count(v)

    def test_vintage_and_duplicate_catalog_conflicts(self):
        for mode in ["same", "new_hash"]:
            c = copy.deepcopy(self.c)
            r = copy.deepcopy(c["sources"][0])
            if mode == "new_hash":
                r["sha256"] = "0" * 64
                r["id"] = "other"
                r["file"] = "other.xls"
            c["sources"].append(r)
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / "c.json"
                p.write_text(json.dumps(c))
                with self.assertRaises(ValueError):
                    catalog(p)

    def test_rights_fail_closed(self):
        c = copy.deepcopy(self.c)
        c["sources"][0]["rights_verified"] = False
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "c.json"
            p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                catalog(p)

    def test_paths_and_primary_domain(self):
        for p in ["../a.xls", "/tmp/a.xls", "a%2exls", "a/b.xls", "a\\b.xls"]:
            with self.assertRaises(ValueError):
                local(FIX, p)
        for u in [
            "http://www.kba.de/SharedDocs/Downloads/DE/a.xls",
            "https://www.kba.de.evil/SharedDocs/Downloads/DE/a.xls",
            "https://user@www.kba.de/SharedDocs/Downloads/DE/a.xls",
        ]:
            with self.assertRaises(ValueError):
                official(u)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.xls").symlink_to(FIX / "2018-01.xls")
            with self.assertRaises(ValueError):
                local(tmp, "a.xls")

    def rows(self, n=60):
        return [
            dict(
                period=p,
                value=100 + i,
                series="brand:EXAMPLE",
                source="source",
                vintage="a" * 64,
                powertrain="all",
            )
            for i, p in enumerate(periods("2020-01", "2024-12")[:n])
        ]

    def test_duplicates_and_conflicting_values_never_coalesced(self):
        rows = self.rows()
        rows.append(dict(rows[0], value=999))
        with self.assertRaises(ValueError):
            validate_rows(rows)

    def test_missing_month_and_longest_run(self):
        rows = self.rows()
        del rows[20]
        c = coverage(rows, "2020-01", "2024-12")
        self.assertEqual(c["missing_months"], ["2021-09"])
        self.assertEqual(c["longest_contiguous"]["months"], 39)
        with self.assertRaises(ValueError):
            describe(rows)

    def test_admission_gates_are_not_scientific_validation(self):
        rows = self.rows()
        source = copy.deepcopy(self.sources["2025-01"])
        source["publication"] = dict(precision="day", value="2026-01-01")
        sources = {}
        for row in rows:
            row["source"] = row["period"]
            sources[row["source"]] = dict(
                source, period=row["period"], sha256=row["vintage"]
            )
        a = admission(rows, sources, "2020-01", "2024-12")
        self.assertEqual(a["status"], "admitted")
        self.assertFalse(a["scientific_validation"])
        self.assertEqual(
            admission(rows[:-1], sources, "2020-01", "2024-12")["status"],
            "insufficient_coverage",
        )
        self.assertEqual(
            admission(rows, sources, "2020-01", "2024-12", design_columns=30)["status"],
            "insufficient_coverage",
        )
        for source in sources.values():
            source["publication"] = dict(precision="month", value="2026-01")
        self.assertEqual(
            admission(rows, sources, "2020-01", "2024-12")["status"], "admitted"
        )
        self.assertEqual(admission(rows, {}, "2020-01", "2024-12")["status"], "blocked")

    def test_selection_rules_are_descriptive_and_training_only(self):
        plan = copy.deepcopy(self.plan)
        plan["brand_selection_window"] = dict(start="2020-01", end="2023-12")
        groups = {}
        for name, level, swing in [
            ("CALM", 2000, 10),
            ("LARGE", 10000, 1000),
            ("SMALL", 100, 1),
            ("TESLA", 2000, 0),
        ]:
            groups["brand:" + name] = [
                dict(r, series="brand:" + name, value=level + swing * (i % 2))
                for i, r in enumerate(self.rows())
            ]
        result = select(groups, plan)
        self.assertEqual(result["C"], "brand:CALM")
        self.assertEqual(result["D"], "brand:LARGE")
        for rows in groups.values():
            for row in rows:
                if row["period"] >= "2024-01":
                    row["value"] = 99999999
        self.assertEqual(select(groups, plan), result)
        self.assertIsNone(select({}, plan)["C"])

    def test_small_descriptive_example(self):
        rows = self.rows(24)
        d = describe(rows)
        self.assertEqual(d["mean"], 111.5)
        self.assertEqual(d["linear_slope_count_per_month"], 1)
        self.assertEqual(d["mad"], 6)
        self.assertIsNone(
            d["largest_exploratory_12_month_mean_shift"]["causal_attribution"]
        )

    def test_deterministic_extract_full_validation_and_no_live_network(self):
        with patch(
            "urllib.request.urlopen", side_effect=AssertionError("Offline test")
        ):
            with tempfile.TemporaryDirectory() as tmp:
                a = Path(tmp) / "a"
                b = Path(tmp) / "b"
                run(CAT, PLAN, FIX, a)
                run(CAT, PLAN, FIX, b)
                self.assertEqual(
                    {p.name: p.read_bytes() for p in a.iterdir()},
                    {p.name: p.read_bytes() for p in b.iterdir()},
                )
                verify(CAT, PLAN, FIX, a)
                audit(CAT, PLAN, a)
                with self.assertRaises(FileExistsError):
                    run(CAT, PLAN, FIX, a)
                p = a / "observations.csv"
                p.write_bytes(p.read_bytes().replace(b"1277", b"1278", 1))
                with self.assertRaises(ValueError):
                    audit(CAT, PLAN, a)

    def test_cached_fetch_verifies_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            import shutil

            c = catalog(ROOT / "data/kba/sources.json")
            c["sources"] = [c["sources"][0]]
            p = Path(tmp) / "catalog.json"
            p.write_text(json.dumps(c))
            shutil.copyfile(FIX / "2018-01.xls", Path(tmp) / "2018-01.xls")
            shutil.copyfile(FIX / "kba-license.pdf", Path(tmp) / "kba-license.pdf")
            with patch(
                "urllib.request.urlopen", side_effect=AssertionError("No download")
            ):
                fetch(p, tmp)
        with self.assertRaises(ValueError):
            fetch(CAT, FIX)

    def test_catalog_metadata_cannot_override_workbook(self):
        c = copy.deepcopy(self.c)
        c["sources"][0]["publication"] = dict(
            value="2018-02-01", precision="day", raw="invented"
        )
        with self.assertRaises(ValueError):
            extract(c, FIX)

    def test_cumulative_conflict_is_reported_without_changing_months(self):
        rows = self.rows(12)
        loc = dict(
            series="brand:EXAMPLE",
            period="2020-12",
            source="source",
            cumulative_value=1,
            cumulative_cell="E99",
        )
        check = reconcile(rows, [loc])[0]
        self.assertEqual(check["status"], "conflict_no_auto_revision")
        self.assertEqual(check["delta"], sum(r["value"] for r in rows) - 1)
        self.assertEqual(rows[0]["value"], 100)

    def test_fixtures_have_no_cover_media_and_cannot_be_admitted(self):
        import zipfile

        for p in FIX.glob("*.xlsx"):
            with zipfile.ZipFile(p) as z:
                self.assertFalse(
                    any(
                        n.startswith(("xl/media/", "xl/drawings/"))
                        for n in z.namelist()
                    )
                )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            run(CAT, PLAN, FIX, out)
            reports = json.loads((out / "coverage.json").read_text())
            self.assertTrue(all(r["status"] == "blocked" for r in reports.values()))

    def test_committed_complete_normalized_series(self):
        audit(ROOT / "data/kba/sources.json", PLAN, ROOT / "data/kba/derived")
