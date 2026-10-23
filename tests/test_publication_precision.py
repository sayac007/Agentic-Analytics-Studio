"""Provenance-only fixtures: no generation, estimation or historical data invention."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from jsonschema import ValidationError
import contracts.validate as v
from support import graph, artifact
from kba.pipeline import admission, catalog, release_record

ROOT = Path(__file__).resolve().parents[1]


class PublicationPrecision(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.g = graph(self.root)["generator"]
        self.g.update(
            schema_version="0.2.1",
            admission_regime="retrospective_immutable_reference",
            reference_kind="observed_kba",
        )
        self.g["reference_columns"]["observed_registrations"]["class"] = "observed"
        pp = [
            line.split(",")[0]
            for line in (self.root / "reference.csv").read_text().splitlines()[1:]
        ]
        self.g["release_records"] = [
            dict(
                period=p,
                source_url="https://example.org/shape-only.xlsx",
                sha256="a" * 64,
                version="shape-only-not-observed",
                license_identifier="shape-only",
                license_url="https://example.org/shape-license",
                rights_verified=True,
                publication_date=dict(precision="day", value="2026-01-15"),
                retrieved_at="2026-10-22",
                available_as_of=None,
            )
            for p in pp
        ]

    def test_day_month_unknown_release_cases(self):
        for pub in [
            dict(precision="day", value="2026-01-15"),
            dict(precision="month", value="2026-01"),
            dict(precision="unknown", value=None),
        ]:
            with self.subTest(pub=pub):
                g = copy.deepcopy(self.g)
                for r in g["release_records"]:
                    r["publication_date"] = pub
                self.assertEqual(v.validate_generator(g, self.root), 60)

    def test_real_release_examples_preserve_catalog_precision(self):
        examples = json.loads(
            (ROOT / "contracts/examples/release-precision.json").read_text()
        )
        for name, record in examples.items():
            v.validate_release(record)
        self.assertEqual(
            examples["month"]["publication_date"],
            dict(precision="month", value="2025-02"),
        )
        self.assertIsNone(examples["unknown"]["publication_date"]["value"])

    def test_precision_cannot_claim_a_placeholder_day(self):
        for pub in [
            dict(precision="month", value="2026-01-01"),
            dict(precision="day", value="2026-01"),
            dict(precision="unknown", value="2026-01-01"),
            dict(precision="unknown", value=""),
            dict(precision="month", value="2026-13"),
            dict(precision="day", value="2026-02-30"),
        ]:
            with self.subTest(pub=pub), self.assertRaises(ValidationError):
                v.validate_release(
                    dict(self.g["release_records"][0], publication_date=pub)
                )

    def test_legacy_020_observed_records_remain_accepted(self):
        g = copy.deepcopy(self.g)
        g["schema_version"] = "0.2.0"
        g.pop("admission_regime")
        for r in g["release_records"]:
            r["published_on"] = r.pop("publication_date")["value"]
            r.pop("retrieved_at")
            r.pop("available_as_of")
        before = json.dumps(g, sort_keys=True)
        self.assertEqual(v.validate_generator(g, self.root), 60)
        self.assertEqual(before, json.dumps(g, sort_keys=True))
        g["schema_version"] = "0.2.1"
        g["admission_regime"] = "retrospective_immutable_reference"
        self.assertEqual(v.validate_generator(g, self.root), 60)
        g.update(
            admission_regime="historical_point_in_time", as_of="2026-02-01T00:00:00Z"
        )
        with self.assertRaisesRegex(ValueError, "availability evidence"):
            v.validate_generator(g, self.root)

    def test_020_does_not_silently_accept_new_record_semantics(self):
        g = copy.deepcopy(self.g)
        g["schema_version"] = "0.2.0"
        g.pop("admission_regime")
        with self.assertRaises(ValidationError):
            v.validate_generator(g, self.root)

    def test_new_version_requires_explicit_regime_and_cutoff(self):
        g = copy.deepcopy(self.g)
        g.pop("admission_regime")
        with self.assertRaises(ValidationError):
            v.validate_generator(g, self.root)
        g = copy.deepcopy(self.g)
        g["admission_regime"] = "historical_point_in_time"
        with self.assertRaises(ValidationError):
            v.validate_generator(g, self.root)
        g = copy.deepcopy(self.g)
        g["as_of"] = "2026-02-01T00:00:00Z"
        with self.assertRaises(ValidationError):
            v.validate_generator(g, self.root)

    def test_publication_retrieval_and_url_do_not_prove_historical_availability(self):
        g = copy.deepcopy(self.g)
        g.update(
            admission_regime="historical_point_in_time", as_of="2026-02-01T00:00:00Z"
        )
        for precision, value in [
            ("day", "2026-01-15"),
            ("month", "2026-01"),
            ("unknown", None),
        ]:
            for r in g["release_records"]:
                r["publication_date"] = dict(precision=precision, value=value)
            with (
                self.subTest(precision=precision),
                self.assertRaisesRegex(
                    ValueError, "availability evidence|day-precision"
                ),
            ):
                v.validate_generator(g, self.root)

    def evidence(self):
        (self.root / "proof.txt").write_text(
            "Shape-only availability assertion; not real historical evidence.\n"
        )
        return dict(
            timestamp="2026-01-20T12:00:00Z",
            source_sha256="a" * 64,
            evidence=artifact(self.root, "proof.txt"),
            evidence_url="https://example.org/shape-only-archive",
            scope="exact_source_vintage",
        )

    def test_point_in_time_requires_hash_bound_checked_evidence_and_cutoff(self):
        g = copy.deepcopy(self.g)
        g.update(
            admission_regime="historical_point_in_time", as_of="2026-02-01T00:00:00Z"
        )
        for r in g["release_records"]:
            r["available_as_of"] = self.evidence()
        self.assertEqual(v.validate_generator(g, self.root), 60)
        g["as_of"] = "2026-01-19T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "cutoff"):
            v.validate_generator(g, self.root)
        g["as_of"] = "2026-02-01T00:00:00Z"
        g["release_records"][0]["available_as_of"]["source_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "different source vintage"):
            v.validate_generator(g, self.root)

    def test_point_in_time_also_requires_documented_publication_day(self):
        for pub in [
            dict(precision="month", value="2026-01"),
            dict(precision="unknown", value=None),
        ]:
            r = copy.deepcopy(self.g["release_records"][0])
            r["available_as_of"] = self.evidence()
            r["publication_date"] = pub
            with (
                self.subTest(pub=pub),
                self.assertRaisesRegex(ValueError, "day-precision"),
            ):
                v.validate_release(r, self.root, "2026-02-01T00:00:00Z")

    def test_evidence_hash_checked_even_in_retrospective_mode(self):
        r = copy.deepcopy(self.g["release_records"][0])
        r["available_as_of"] = self.evidence()
        (self.root / "proof.txt").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "checksum"):
            v.validate_release(r, self.root)

    def test_evidence_time_and_publication_chronology(self):
        r = copy.deepcopy(self.g["release_records"][0])
        r["available_as_of"] = self.evidence()
        for change in [
            dict(timestamp="2026-01-14T00:00:00Z"),
            dict(timestamp="2026-10-23T00:00:00Z"),
            dict(evidence_url="file:///proof.txt"),
        ]:
            x = copy.deepcopy(r)
            x["available_as_of"].update(change)
            with self.assertRaises(ValueError):
                v.validate_release(x, self.root)
        r["available_as_of"] = None
        r["publication_date"]["value"] = "2026-10-23"
        with self.assertRaises(ValueError):
            v.validate_release(r, self.root)

    def test_estimator_cannot_receive_new_provenance_or_regime_fields(self):
        from support import template

        for field, value in [
            ("publication_date", {"precision": "unknown", "value": None}),
            ("available_as_of", None),
            ("admission_regime", "retrospective_immutable_reference"),
            ("retrieved_at", "2026-10-22"),
        ]:
            m = template()
            m[field] = value
            with self.subTest(field=field), self.assertRaises(ValidationError):
                v.validate_manifest(m)


class KbaAdmissionRegimes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = {
            s["id"]: s for s in catalog(ROOT / "data/kba/sources.json")["sources"]
        }
        import csv

        with (ROOT / "data/kba/derived/observations.csv").open() as f:
            cls.rows = list(csv.DictReader(f))
        for r in cls.rows:
            r["value"] = int(r["value"])

    def tesla(self):
        return copy.deepcopy([r for r in self.rows if r["series"] == "brand:TESLA"])

    def test_all_four_real_series_have_distinct_regimes_and_no_padding(self):
        for name, n, start in [
            ("brand:TESLA", 96, "2018-01"),
            ("brand:TOYOTA", 96, "2018-01"),
            ("brand:VW", 96, "2018-01"),
            ("market:BEV", 60, "2021-01"),
        ]:
            rows = [r for r in self.rows if r["series"] == name]
            r = admission(rows, self.sources, "2018-01", "2025-12")
            self.assertEqual(r["verified_count"], n)
            self.assertEqual(r["checked_period"]["start"], start)
            self.assertEqual(
                r["admission_regimes"]["retrospective_immutable_reference"]["status"],
                "admitted",
            )
            self.assertEqual(
                r["admission_regimes"]["historical_point_in_time"]["status"], "blocked"
            )
            self.assertEqual(r["status_regime"], "retrospective_immutable_reference")

    def test_hash_license_definition_and_month_problems_block_both_modes(self):
        for problem in ["hash", "license", "definition", "source_period", "continuity"]:
            rows = self.tesla()
            sources = copy.deepcopy(self.sources)
            s = sources[rows[0]["source"]]
            if problem == "hash":
                rows[0]["vintage"] = "b" * 64
            if problem == "license":
                s["rights_verified"] = False
            if problem == "definition":
                rows[0]["powertrain"] = "BEV_only"
            if problem == "source_period":
                s["period"] = "2018-02"
            if problem == "continuity":
                rows.pop(1)
            r = admission(
                rows, sources, "2018-01", "2025-12", as_of="2026-10-22T23:59:59Z"
            )
            with self.subTest(problem=problem):
                self.assertTrue(
                    all(
                        x["status"] == "blocked"
                        for x in r["admission_regimes"].values()
                    )
                )

    def test_retrieval_only_is_not_promoted_to_availability(self):
        r = release_record(self.sources["fz10-2025-12"])
        self.assertEqual(r["retrieved_at"], "2026-10-22")
        self.assertIsNone(r["available_as_of"])
        r = admission(
            self.tesla(),
            self.sources,
            "2018-01",
            "2025-12",
            as_of="2026-10-22T23:59:59Z",
        )
        self.assertEqual(
            r["admission_regimes"]["historical_point_in_time"]["status"], "blocked"
        )

    def test_unresolved_duplicate_vintage_catalog_fails(self):
        c = json.loads((ROOT / "data/kba/sources.json").read_text())
        c["sources"].append(dict(c["sources"][0], sha256="b" * 64))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "catalog.json"
            p.write_text(json.dumps(c))
            with self.assertRaises(ValueError):
                catalog(p)
