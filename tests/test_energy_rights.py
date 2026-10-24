"""Synthetic transition tests plus integrity checks of the explicit human decision."""

import copy
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

from fuel_oil import rights_admission as r
from fuel_oil.fetch_fuel_oil import month_range


class EnergyRightsTests(unittest.TestCase):
    def setUp(self):
        self.matrix = json.loads((r.DATA / "rights_admission.json").read_text())
        self.catalog = json.loads((r.DATA / "real_sources.json").read_text())
        # Counterfactual pending baseline; never inherit real approvals into fixtures.
        for record in self.matrix["series"]:
            record.update(
                private_analysis="not_verified",
                analysis_scope_verified=False,
                source_specific_review_status="pending",
                human_admission_decision=None,
            )
        self.refresh(r.ROOT)

    def record(self, id="eurusd"):
        return next(x for x in self.matrix["series"] if x["id"] == id)

    def supported_fixture(self, root, id="eurusd"):
        # Isolate evidence roots too: unresolved sources keep their own copied proof.
        for item in self.matrix["series"]:
            for proof in [item] + item.get("supporting_evidence", []):
                if proof.get("evidence_file"):
                    target = Path(root) / proof["evidence_file"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    original = r.ROOT / proof["evidence_file"]
                    if original.exists():
                        target.write_bytes(original.read_bytes())
                    else:
                        self.assertTrue(target.exists())
        path = Path(root) / "SYNTHETIC_policy.txt"
        path.write_text(
            "SYNTHETIC POLICY FIXTURE: test authorization only, not real rights"
        )
        rec = self.record(id)
        rec.update(
            private_analysis="permitted",
            public_raw_redistribution="blocked",
            public_derived_redistribution="not_verified",
            analysis_scope_verified=True,
            source_specific_review_status="verified",
            evidence_type="synthetic_fixture",
            evidence_file=path.name,
            evidence_hash=r.sha(path.read_bytes()),
            source_specific_review_note="SYNTHETIC reviewed source-specific no-exception scenario",
        )
        rec["human_admission_decision"] = {
            "decision": "approve_private_retrospective",
            "scope": "private_retrospective_only",
            "series_id": rec["series_id"],
            "unit": rec["unit"],
            "raw_sha256": rec["raw_sha256"],
            "reviewer": "SYNTHETIC_REVIEWER",
            "evidence_file": path.name,
            "evidence_hash": r.sha(path.read_bytes()),
        }
        return rec

    def refresh(self, root, fixture=False):
        for rec in self.matrix["series"]:
            result = r.assess(rec, self.catalog["files"][rec["id"]], root, fixture)
            rec.update(
                analytical_admission=result["status"],
                admission_reasons=result["reasons"],
            )
        self.matrix["source_catalog_sha256"] = r.sha(r.encoded(self.catalog))

    def test_current_human_decisions_admit_only_ecb_and_qualified_diesel(self):
        actual = json.loads((r.DATA / "rights_admission.json").read_text())
        results = r.check(actual, self.catalog)
        self.assertEqual(
            {k: v["status"] for k, v in results.items()},
            {"eurusd": "admitted", "brent_usd": "blocked", "diesel_de": "admitted"},
        )
        self.assertEqual(
            self.record("diesel_de")["public_raw_redistribution"], "not_verified"
        )
        by = {x["id"]: x for x in actual["series"]}
        self.assertEqual(by["brent_usd"]["legal_status"], "not_verified")
        self.assertEqual(
            by["brent_usd"]["underlying_source"]["name"], "Refinitiv (LSEG)"
        )
        self.assertEqual(
            by["diesel_de"]["admission_qualification"],
            "qualified_project_specific_private_use",
        )
        self.assertTrue(by["diesel_de"]["unresolved_limitations"])
        self.assertTrue(
            all(
                x["historical_point_in_time"] == "not_established"
                for x in self.matrix["series"]
            )
        )

    def test_changed_flag_and_general_handoff_are_not_source_admission(self):
        rec = self.record()
        rec["private_analysis"] = "permitted"
        rec["analysis_scope_verified"] = True
        result = r.assess(rec, self.catalog["files"]["eurusd"])
        self.assertEqual(result["status"], "blocked")
        self.assertIn(
            "Source-specific third-party/notice applicability review pending",
            result["reasons"],
        )
        self.assertIn(
            "Explicit source-bound human private-admission decision missing",
            result["reasons"],
        )

    def test_refinitiv_withholding_cannot_be_overridden_by_admission_flags(self):
        actual = json.loads((r.DATA / "rights_admission.json").read_text())
        rec = next(x for x in actual["series"] if x["id"] == "brent_usd")
        rec.update(
            private_analysis="permitted",
            analysis_scope_verified=True,
            source_specific_review_status="verified",
        )
        self.assertEqual(
            r.assess(rec, self.catalog["files"]["brent_usd"])["status"], "blocked"
        )
        rec["human_admission_decision"]["decision"] = "approve_private_retrospective"
        with self.assertRaisesRegex(ValueError, "disagrees"):
            r.assess(rec, self.catalog["files"]["brent_usd"])

    def test_qualified_diesel_cannot_drop_limits_or_invent_decision_time(self):
        actual = json.loads((r.DATA / "rights_admission.json").read_text())
        rec = next(x for x in actual["series"] if x["id"] == "diesel_de")
        bad = copy.deepcopy(rec)
        bad["unresolved_limitations"] = []
        with self.assertRaisesRegex(ValueError, "Qualified"):
            r.assess(bad, self.catalog["files"]["diesel_de"])
        for field, value in [
            ("legal_status", "cleared"),
            ("public_redistribution_approval", "granted"),
            ("task_01j_authorized", True),
            ("source_specific_review_status", "verified"),
        ]:
            bad = copy.deepcopy(rec)
            bad[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.assess(bad, self.catalog["files"]["diesel_de"])
        bad = copy.deepcopy(rec)
        bad["human_admission_decision"]["exact_decision_time"] = "2026-10-24T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "precision"):
            r.assess(bad, self.catalog["files"]["diesel_de"])

    def test_human_decision_and_exception_review_are_both_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self.supported_fixture(tmp)
            rec["human_admission_decision"] = None
            self.assertEqual(
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)[
                    "status"
                ],
                "blocked",
            )
            rec = self.supported_fixture(tmp)
            rec["source_specific_review_status"] = "pending"
            self.assertEqual(
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)[
                    "status"
                ],
                "blocked",
            )
            rec["human_admission_decision"]["unit"] = "EUR_per_USD"
            with self.assertRaisesRegex(ValueError, "Human decision"):
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)

    def test_external_handoff_is_preserved_and_not_personal_page_access(self):
        proof = self.matrix["external_handoff"]
        self.assertFalse(proof["codex_accessed_policy_pages"])
        self.assertEqual(
            r.sha((r.ROOT / proof["evidence_file"]).read_bytes()),
            proof["evidence_hash"],
        )
        self.assertIn(
            "not a copy of the complete legal texts",
            (r.ROOT / proof["evidence_file"]).read_text().replace("**", ""),
        )
        self.assertTrue(
            all(
                x["general_policy_status"] == "externally_reviewed"
                for x in self.matrix["series"]
            )
        )

    def test_reviewed_fixture_transition_does_not_need_public_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self.supported_fixture(tmp)
            self.assertEqual(
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)[
                    "status"
                ],
                "admitted",
            )
            rec["private_analysis"] = "blocked"
            self.assertEqual(
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)[
                    "status"
                ],
                "blocked",
            )

    def test_fixture_review_cannot_enter_real_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self.supported_fixture(tmp)
            with self.assertRaises(ValueError):
                r.assess(rec, self.catalog["files"]["eurusd"], tmp)

    def test_independent_admission_diesel_does_not_block_ecb(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.supported_fixture(tmp)
            # Other unresolved evidence remains untouched, including all diesel gaps.
            self.refresh(tmp, fixture=True)
            result = r.check(self.matrix, self.catalog, tmp, fixture=True)
            self.assertEqual(result["eurusd"]["status"], "admitted")
            self.assertEqual(result["brent_usd"]["status"], "blocked")
            self.assertEqual(result["diesel_de"]["status"], "blocked")

    def test_source_series_unit_and_hash_are_bound(self):
        for field, value in [
            ("series_id", "RWTI"),
            ("unit", "EUR_per_USD"),
            ("raw_sha256", "0" * 64),
        ]:
            rec = copy.deepcopy(self.record())
            rec[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                r.assess(rec, self.catalog["files"]["eurusd"])

    def test_incomplete_definition_unit_or_scope_does_not_admit(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = copy.deepcopy(self.supported_fixture(tmp))
            for field in (
                "source_definition_verified",
                "unit_verified",
                "raw_sha256_verified",
                "analysis_scope_verified",
            ):
                rec = copy.deepcopy(original)
                rec[field] = False
                self.assertEqual(
                    r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)[
                        "status"
                    ],
                    "blocked",
                )

    def test_evidence_hash_drift_and_empty_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self.supported_fixture(tmp)
            rec["source_specific_review_note"] = ""
            self.assertEqual(
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)[
                    "status"
                ],
                "blocked",
            )
            (Path(tmp) / rec["evidence_file"]).write_text("changed")
            with self.assertRaisesRegex(ValueError, "hash drift"):
                r.assess(rec, self.catalog["files"]["eurusd"], tmp, fixture=True)

    def test_path_traversal_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            rec = self.supported_fixture(tmp)
            for path in ("../escape", "/tmp/escape", "a//b", "a/./b", "a%2fb", "a\\b"):
                bad = dict(rec, evidence_file=path)
                with self.assertRaises(ValueError):
                    r.evidence_bytes(bad, tmp)
            link = Path(tmp) / "escape.txt"
            link.symlink_to("/etc/hosts")
            with self.assertRaises(ValueError):
                r.evidence_bytes(dict(rec, evidence_file=link.name), tmp)

    def test_unknown_states_and_historical_claims_fail(self):
        for key, value in [
            ("private_analysis", "probably_permitted"),
            ("historical_point_in_time", "established"),
            ("reviewed_at", "2026-10-24T10:00:00"),
            ("human_admission_required", False),
        ]:
            rec = copy.deepcopy(self.record())
            rec[key] = value
            with self.assertRaises(ValueError):
                r.assess(rec, self.catalog["files"]["eurusd"])

    def test_public_matrix_has_no_values_paths_or_fabricated_decision_time(self):
        def visit(value):
            if isinstance(value, dict):
                if set(value) == {"precision", "value"}:
                    self.assertEqual(value["precision"], "day")
                    date.fromisoformat(value["value"])
                    return
                self.assertFalse(
                    {
                        "observations",
                        "value",
                        "private_path",
                        "local_path",
                        "credentials",
                    }
                    & set(value)
                )
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(self.matrix)
        text = json.dumps(self.matrix)
        self.assertNotIn("/workspace/", text)
        self.assertNotIn("/home/", text)
        actual = json.loads((r.DATA / "rights_admission.json").read_text())
        for x in actual["series"]:
            decision = x["human_admission_decision"]
            self.assertEqual(
                decision["decision_date"], {"precision": "day", "value": "2026-10-24"}
            )
            self.assertIsNone(decision["exact_decision_time"])
            self.assertEqual(
                r.sha((r.ROOT / decision["evidence_file"]).read_bytes()),
                decision["evidence_hash"],
            )
            self.assertFalse(x["task_01j_authorized"])

    def test_matrix_rejects_self_declared_admitted_and_source_drift(self):
        self.record()["analytical_admission"] = "admitted"
        with self.assertRaises(ValueError):
            r.check(self.matrix, self.catalog)
        self.matrix = json.loads((r.DATA / "rights_admission.json").read_text())
        self.catalog["files"]["eurusd"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            r.check(self.matrix, self.catalog)

    def test_all_13_gaps_and_2022_loss_retained(self):
        gap = self.matrix["diesel_missingness"]
        self.assertEqual(len(gap["missing_months"]), 13)
        self.assertEqual(
            gap["counts_by_year"],
            {"2018": 2, "2019": 3, "2020": 3, "2021": 3, "2022": 2},
        )
        self.assertEqual(gap["missing_2022_months"], ["2022-01", "2022-04"])
        self.assertEqual(gap["complete_2022_months"], 10)
        gap["missing_months"].pop()
        with self.assertRaises(ValueError):
            r.check(self.matrix, self.catalog)

    def test_no_success_artifact_for_blocked_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "admissions"
            result = r.write_private_admissions(
                self.matrix, self.catalog, Path(tmp) / "absent_private", output
            )
            self.assertEqual(result, [])
            self.assertFalse(output.exists())

    def test_independent_writer_needs_only_own_private_files_and_no_values_leak(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.supported_fixture(root)
            private = root / "private"
            private.mkdir()
            raw = b"SYNTHETIC ECB SOURCE"
            source = self.catalog["files"]["eurusd"]
            source["sha256"] = r.sha(raw)
            self.record()["raw_sha256"] = source["sha256"]
            self.record()["human_admission_decision"]["raw_sha256"] = source["sha256"]
            (private / "eurusd.csv").write_bytes(raw)
            rows = [
                {"period": p, "value": 1.2} for p in month_range("2018-01", "2026-09")
            ]
            native = r.encoded({"observations": rows})
            (private / "eurusd.quarantined.json").write_bytes(native)
            (private / "inventory.json").write_bytes(
                r.encoded(
                    {
                        "artifacts": {
                            "eurusd": {
                                "raw_sha256": r.sha(raw),
                                "normalized_sha256": r.sha(native),
                            }
                        }
                    }
                )
            )
            self.refresh(root, fixture=True)
            output = root / "admitted"
            ids = r.write_private_admissions(
                self.matrix, self.catalog, private, output, root, fixture=True
            )
            self.assertEqual(ids, ["eurusd"])
            self.assertEqual(
                [p.name for p in output.iterdir()], ["eurusd.admission.json"]
            )
            text = (output / "eurusd.admission.json").read_text()
            payload = json.loads(text)
            self.assertEqual(payload["scope"], "SYNTHETIC_FIXTURE_ONLY")
            self.assertNotIn(str(private), text)
            self.assertNotIn("observations", payload)
            self.assertNotIn("value", payload)
            with self.assertRaises(ValueError):
                r.write_private_admissions(
                    self.matrix, self.catalog, private, output, root, fixture=True
                )
            # Corrupt own input fails; missing diesel input did not block valid ECB.
            (private / "eurusd.csv").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                r.write_private_admissions(
                    self.matrix, self.catalog, private, root / "new", root, fixture=True
                )

    def test_previous_catalog_coverage_and_import_contract_remain_unchanged(self):
        from fuel_oil.import_energy import check_public_metadata
        from fuel_oil.fetch_fuel_oil import blocked_coverage

        check_public_metadata()
        source = json.loads((r.DATA / "sources.json").read_text())
        self.assertEqual(
            r.encoded(blocked_coverage(source)), (r.DATA / "coverage.json").read_bytes()
        )


if __name__ == "__main__":
    unittest.main()
