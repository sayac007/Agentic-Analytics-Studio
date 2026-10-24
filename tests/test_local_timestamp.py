"""Qualified local-time evidence on synthetic fixtures, never a real approval."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from attention.econometrics import ROOT, admit
from attention.import_trends import (
    LOCAL_TIME_LIMITATIONS,
    build_import,
    inspect_pending,
    sha,
    validate_local_time,
)
from attention.transform import timestamp

FIX = ROOT / "tests/fixtures/trends"
spec = importlib.util.spec_from_file_location(
    "local_time_fixture", ROOT / "tests/fixtures/econometrics/generate.py"
)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def fixture():
    raw = (FIX / "SYNTHETIC_extended.csv").read_bytes()
    meta = json.loads((FIX / "SYNTHETIC_extended_metadata.json").read_text())
    meta.update(
        version="1.2.0",
        retrieved_at="2026-10-23T18:20:44+02:00",
        timestamp_evidence_type="local_file_creation_time",
        timestamp_evidence_limitations=LOCAL_TIME_LIMITATIONS,
        local_timestamp_basis_accepted=True,
    )
    return raw, meta


class LocalTimestampTests(unittest.TestCase):
    def test_qualified_local_time_is_not_google_delivery_proof(self):
        raw, m = fixture()
        rows, report = build_import(raw, m, True)
        self.assertEqual(
            timestamp(m["retrieved_at"]).isoformat(), "2026-10-23T16:20:44+00:00"
        )
        self.assertEqual(
            report["timestamp_evidence"]["type"], "local_file_creation_time"
        )
        self.assertFalse(report["timestamp_evidence"]["verified_google_download_time"])
        self.assertEqual(
            report["timestamp_evidence"]["limitations"], LOCAL_TIME_LIMITATIONS
        )
        self.assertEqual(
            rows[-1]["period_completeness"], "partial_or_unverified_period"
        )
        self.assertEqual(len(rows), 274)

    def test_explicit_local_basis_acceptance_required_even_with_private_rights(self):
        raw, base = fixture()
        for flag in (False, None, 1):
            m = copy.deepcopy(base)
            m["local_timestamp_basis_accepted"] = flag
            with (
                self.subTest(flag=flag),
                self.assertRaisesRegex(ValueError, "human acceptance"),
            ):
                build_import(raw, m, True)

    def test_malformed_or_source_side_evidence_refused(self):
        raw, base = fixture()
        for key, value in [
            ("timestamp_evidence_type", "verified_google_download_time"),
            ("timestamp_evidence_type", "unknown"),
            ("timestamp_evidence_limitations", ""),
            ("timestamp_evidence_limitations", []),
            ("retrieved_at", "2026-10-23 18:20:44"),
            ("retrieved_at", "2026-10-32T18:20:44+02:00"),
        ]:
            m = copy.deepcopy(base)
            m[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                build_import(raw, m, True)
        del base["timestamp_evidence_type"]
        with self.assertRaises(ValueError):
            build_import(raw, base, True)

    def test_berlin_offset_and_dst_checked(self):
        _, m = fixture()
        for value in (
            "2026-10-23T18:20:44+01:00",
            "2026-10-23T18:20:44+03:00",
            "2026-10-23T18:20:44Z",
        ):
            m["retrieved_at"] = value
            with (
                self.subTest(value=value),
                self.assertRaisesRegex(ValueError, "Berlin"),
            ):
                validate_local_time(m)
        m["retrieved_at"] = "2026-12-01T18:20:44+01:00"
        validate_local_time(m)
        m["retrieved_at"] = "2026-12-01T18:20:44+02:00"
        with self.assertRaises(ValueError):
            validate_local_time(m)

    def test_hash_geo_rights_and_scale_still_fail_closed(self):
        raw, base = fixture()
        for mode in ("hash", "geo", "rights", "scale"):
            m = copy.deepcopy(base)
            if mode == "hash":
                m["raw_sha256"] = "0" * 64
            if mode == "geo":
                m["geography"] = "US"
            if mode == "rights":
                m["rights"]["private_analysis_confirmed"] = False
            if mode == "scale":
                m["normalization"]["rescaled"] = True
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                build_import(raw, m, True)

    def test_legacy_interfaces_and_partial_request_rules_unchanged(self):
        raw = (FIX / "SYNTHETIC_monthly.csv").read_bytes()
        m = json.loads((FIX / "SYNTHETIC_metadata.json").read_text())
        _, r = build_import(raw, m, True)
        self.assertNotIn("timestamp_evidence", r)
        m["request_window"]["end"] = "2018-12-15"
        m["normalization"]["window"]["end"] = "2018-12-15"
        m["source_url"] = m["source_url"].replace("2018-12-31", "2018-12-15")
        with self.assertRaisesRegex(ValueError, "whole calendar months"):
            build_import(raw, m, True)
        raw = (FIX / "SYNTHETIC_extended.csv").read_bytes()
        m = json.loads((FIX / "SYNTHETIC_extended_metadata.json").read_text())
        self.assertEqual(len(build_import(raw, m, True)[0]), 274)

    def test_pending_inspection_does_not_admit_actual_basis(self):
        raw, m = fixture()
        m["origin"] = "observed"
        m["export_method"] = "official_ui_manual_csv"
        m["local_timestamp_basis_accepted"] = False
        r = inspect_pending(raw, m)
        self.assertFalse(r["empirical_admission"])
        self.assertEqual(r["normalized_csvs"], [])
        self.assertIn("local_timestamp_basis_accepted", r["unresolved_fields"])
        self.assertIn("human acceptance", r["admission_validation"])

    def test_separate_admission_acceptance_binds_the_amendment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = list(helper.generate(root / "fixture"))
            raw, m = fixture()
            meta = root / "synthetic_local_meta.json"
            meta.write_text(json.dumps(m))
            out = root / "local_import"
            run = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "attention.import_trends",
                    "--csv",
                    str(paths[0]),
                    "--metadata",
                    str(meta),
                    "--output-dir",
                    str(out),
                    "--fixture",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            a = json.loads(paths[3].read_text())
            a["metadata_sha256"] = sha(meta.read_bytes())
            paths[1] = meta
            paths[2] = out
            for accepted, digest in [(False, "0" * 64), (True, "0" * 64)]:
                a["local_timestamp_basis_accepted"] = accepted
                a["local_timestamp_amendment_sha256"] = digest
                paths[3].write_text(json.dumps(a))
                with self.assertRaisesRegex(ValueError, "Separate human acceptance"):
                    admit(*paths, fixture=True)
            # Simulated approval applies to fictional fixtures only, not the actual user file.
            a["local_timestamp_amendment_sha256"] = sha(
                (ROOT / "docs/LOCAL_TIMESTAMP_ADMISSION.md").read_bytes()
            )
            paths[3].write_text(json.dumps(a))
            _, p = admit(*paths, fixture=True)
            self.assertEqual(p["label"], "SYNTHETIC_FIXTURE_ONLY")
            self.assertFalse(p["timestamp_evidence"]["verified_google_download_time"])

    def test_public_decision_is_pending_and_protocol_is_frozen(self):
        r = json.loads(
            (ROOT / "data/organic_attention/task01g1_status.json").read_text()
        )
        self.assertFalse(r["human_basis_acceptance"])
        self.assertFalse(r["real_diagnostics_executed"])
        self.assertEqual(r["real_value_artifacts_generated"], [])
        self.assertEqual(
            r["amendment_sha256"],
            sha((ROOT / "docs/LOCAL_TIMESTAMP_ADMISSION.md").read_bytes()),
        )
