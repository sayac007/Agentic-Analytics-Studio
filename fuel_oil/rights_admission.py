"""Source-specific rights decisions; evidence review is never inferred from a URL."""

import argparse
from collections import Counter
from datetime import date, datetime
import json
from pathlib import Path
import re

from fuel_oil.fetch_fuel_oil import encoded, sha, safe_url

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/fuel_oil"
IDENTITIES = {
    "eurusd": ("EXR.M.USD.EUR.SP00.A", "USD_per_EUR"),
    "brent_usd": ("RBRTE", "USD_per_barrel"),
    "diesel_de": ("DE_price_with_tax_diesel", "EUR_per_1000_litres"),
}
RIGHTS = (
    "private_analysis",
    "public_raw_redistribution",
    "public_derived_redistribution",
)
STATES = {"permitted", "blocked", "not_verified"}
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


def evidence_bytes(record, root):
    relative = record.get("evidence_file")
    if relative is None:
        if record["evidence_hash"] is not None:
            raise ValueError("Hash without a policy artifact")
        return None
    if (
        not isinstance(relative, str)
        or not re.fullmatch(r"[a-zA-Z0-9_./-]+", relative)
        or any(p in ("", ".", "..") for p in relative.split("/"))
    ):
        raise ValueError("Noncanonical policy path")
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError("Policy evidence escapes root")
    raw = path.read_bytes()
    if sha(raw) != record["evidence_hash"]:
        raise ValueError("Policy evidence hash drift")
    return raw


def assess(record, source, root=ROOT, fixture=False):
    """Assess ONE source. Other sources and public permission never gate private use."""
    if record["id"] not in IDENTITIES:
        raise ValueError("Unknown source")
    expected_key, expected_unit = IDENTITIES[record["id"]]
    safe_url(record["source_notice_url"])
    reasons = []
    if (record["series_id"], record["unit"], record["raw_sha256"]) != (
        expected_key,
        expected_unit,
        source["sha256"],
    ):
        raise ValueError("Series/unit/raw hash binding mismatch")
    for field in RIGHTS:
        if record[field] not in STATES:
            raise ValueError("Unknown rights state")
    stamp = datetime.fromisoformat(record["reviewed_at"].replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Review timestamp must retain offset")
    if record["historical_point_in_time"] != "not_established":
        raise ValueError(
            "This retrospective task cannot establish historical availability"
        )
    if (
        record.get("public_redistribution_approval", "not_granted") != "not_granted"
        or record.get("task_01j_authorized", False) is not False
    ):
        raise ValueError(
            "Private admission does not authorise public release or Task 01J"
        )
    if record["evidence_type"] == "synthetic_fixture" and not fixture:
        raise ValueError("Fixture review cannot admit real data")
    raw = evidence_bytes(record, root)
    for supporting in record.get("supporting_evidence", []):
        evidence_bytes(supporting, root)
    if record["private_analysis"] != "permitted":
        reasons.append(
            "Private analytical use not verified/permitted for the specified scope"
        )
    if not all(
        record[k] is True
        for k in ("source_definition_verified", "unit_verified", "raw_sha256_verified")
    ):
        reasons.append("Source definition/unit/raw verification incomplete")
    if record["analysis_scope_verified"] is not True:
        reasons.append(
            "Policy coverage of exact source and intended analytical transformation unresolved"
        )
    qualified = (
        record.get("source_specific_review_status")
        == "qualified_private_scope_accepted"
    )
    if qualified and (
        record.get("admission_qualification")
        != "qualified_project_specific_private_use"
        or not record.get("unresolved_limitations")
        or record.get("legal_status") != "not_verified"
    ):
        raise ValueError(
            "Qualified acceptance must preserve its unresolved limitations"
        )
    if record.get("source_specific_review_status") != "verified" and not qualified:
        reasons.append(
            "Source-specific third-party/notice applicability review pending"
        )
    if record.get("human_admission_required") is not True:
        raise ValueError("Required human review cannot be disabled by a flag")
    if record["human_admission_required"]:
        decision = record.get("human_admission_decision")
        if not isinstance(decision, dict):
            reasons.append(
                "Explicit source-bound human private-admission decision missing"
            )
        elif (
            decision.get("scope"),
            decision.get("series_id"),
            decision.get("unit"),
            decision.get("raw_sha256"),
        ) != (
            "private_retrospective_only",
            expected_key,
            expected_unit,
            source["sha256"],
        ):
            raise ValueError("Human decision scope/series/unit/hash mismatch")
        elif not decision.get("reviewer") or not decision.get("evidence_hash"):
            raise ValueError("Human decision reviewer/evidence binding missing")
        else:
            decision_raw = evidence_bytes(decision, root)
            day = decision.get("decision_date")
            if day is not None:
                if (
                    set(day) != {"precision", "value"}
                    or day["precision"] != "day"
                    or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", day["value"])
                    or decision.get("exact_decision_time") is not None
                ):
                    raise ValueError(
                        "Human day precision cannot become an invented instant"
                    )
                date.fromisoformat(day["value"])
            if not fixture:
                if decision.get("evidence_format") != "structured_human_decision_v1":
                    raise ValueError(
                        "Real approval requires a source-bound structured human decision"
                    )
                approved = json.loads(decision_raw)
                evidence_bytes(approved["source_message"], root)
                entry = approved["decisions"][record["id"]]
                for field in (
                    "decision",
                    "scope",
                    "series_id",
                    "unit",
                    "raw_sha256",
                    "qualification",
                ):
                    if decision.get(field) != entry.get(field):
                        raise ValueError(
                            "Claimed decision disagrees with source-specific human evidence"
                        )
                if day != approved["decision_date"]:
                    raise ValueError("Human decision date disagrees with evidence")
                if (
                    decision.get("source_message_hash")
                    != approved["source_message"]["evidence_hash"]
                ):
                    raise ValueError("Human source message binding mismatch")
            if decision.get("decision") == "withhold_unconditional_admission":
                reasons.append(
                    "Human review withholds unconditional admission; third-party rights unresolved"
                )
            elif decision.get("decision") != "approve_private_retrospective":
                raise ValueError("Unsupported human admission decision")
            elif (
                qualified
                and decision.get("qualification")
                != "qualified_project_specific_private_use"
            ):
                raise ValueError(
                    "Qualified scope must be explicitly accepted by the human decision"
                )
            elif (
                decision.get("qualification")
                == "qualified_project_specific_private_use"
                and not qualified
            ):
                raise ValueError(
                    "Qualified human acceptance cannot become unqualified clearance"
                )
    if raw is None or record["evidence_type"] not in (
        "reviewed_primary_policy",
        "reviewed_human_supplied_primary_copy",
        "externally_reviewed_primary_policy_handoff",
        "synthetic_fixture",
    ):
        reasons.append(
            "No reviewed primary policy artifact supporting analytical admission"
        )
    if not record["source_specific_review_note"].strip():
        reasons.append("Source-specific exception review absent")
    return {
        "status": "blocked" if reasons else "admitted",
        "reasons": reasons,
        "scope": "private_retrospective_only",
        "historical_point_in_time": "not_established",
    }


def check(matrix, source_catalog, root=ROOT, fixture=False):
    if matrix["version"] != "1.0.0" or matrix["source_catalog_sha256"] != sha(
        encoded(source_catalog)
    ):
        raise ValueError("Rights/source catalog binding drift")
    records = matrix["series"]
    if {r["id"] for r in records} != set(IDENTITIES) or len(records) != 3:
        raise ValueError("Missing/duplicate source decision")
    outcomes = {}
    for r in records:
        result = assess(r, source_catalog["files"][r["id"]], root, fixture)
        if (
            r["analytical_admission"] != result["status"]
            or r["admission_reasons"] != result["reasons"]
        ):
            raise ValueError(
                "Declared admission does not match evidence-based source decision"
            )
        outcomes[r["id"]] = result
    gap = matrix["diesel_missingness"]
    if (
        gap["missing_months"] != GAPS
        or gap["counts_by_year"] != dict(Counter(p[:4] for p in GAPS))
        or gap["missing_2022_months"] != ["2022-01", "2022-04"]
    ):
        raise ValueError("Diesel gaps changed/filled")
    if (
        gap["interpolation"] != "none"
        or matrix["e10_status"] != "excluded_not_verified"
    ):
        raise ValueError("No filling or E10 substitution")
    return outcomes


def verify_private(matrix, source_catalog, private_dir, ids=None):
    """Read original and derived bytes only; never join outcomes or change values."""
    root = Path(private_dir)
    inventory = json.loads((root / "inventory.json").read_text())["artifacts"]
    selected = list(IDENTITIES) if ids is None else ids
    for id in selected:
        original = root / (id + Path(source_catalog["files"][id]["filename"]).suffix)
        digest = sha(original.read_bytes())
        if (
            digest != source_catalog["files"][id]["sha256"]
            or digest != inventory[id]["raw_sha256"]
        ):
            raise ValueError("Private source hash drift")
        normalized = root / (id + ".quarantined.json")
        if sha(normalized.read_bytes()) != inventory[id]["normalized_sha256"]:
            raise ValueError("Private normalized hash drift")
    rows, gaps = [], []
    if "diesel_de" in selected:
        monthly_path = root / "diesel_de.monthly_approx.quarantined.json"
        if (
            sha(monthly_path.read_bytes())
            != inventory["diesel_monthly_approx"]["normalized_sha256"]
        ):
            raise ValueError("Private monthly hash drift")
        rows = json.loads(monthly_path.read_text())["observations"]
        gaps = [
            r["period"] for r in rows if r["period"] <= "2026-09" and r["value"] is None
        ]
        if gaps != matrix["diesel_missingness"]["missing_months"]:
            raise ValueError("Private diesel missingness drift")
    # Counts are checked from the existing parsed real snapshots, without new transforms.
    for id in selected:
        native = json.loads((root / (id + ".quarantined.json")).read_text())[
            "observations"
        ]
        for end, expected in [("2025-12", 96), ("2026-09", 105)]:
            source_rows = rows if id == "diesel_de" else native
            count = sum(
                r["value"] is not None
                and not r.get("partial", r.get("partial_calendar_month", False))
                for r in source_rows
                if "2018-01" <= r["period"] <= end
            )
            if count != (expected - len(gaps) if id == "diesel_de" else expected):
                raise ValueError(
                    "Private source coverage differs from reviewed snapshot"
                )
    return inventory


def write_private_admissions(
    matrix, source_catalog, private_dir, output, root=ROOT, fixture=False
):
    """Write only supported independent admissions; never writes blocked pseudo-permits."""
    output = Path(output).resolve()
    if output.is_relative_to(ROOT.resolve()) or output.exists():
        raise ValueError("Use a NEW output directory outside the repository")
    decisions = check(matrix, source_catalog, root, fixture=fixture)
    admitted = [
        id for id, result in decisions.items() if result["status"] == "admitted"
    ]
    if not admitted:
        return []  # No success-looking admission directory for pending evidence.
    inv = verify_private(matrix, source_catalog, private_dir, ids=admitted)
    output.mkdir(parents=True)
    for id in admitted:
        record = next(r for r in matrix["series"] if r["id"] == id)
        artifact = {
            "source_id": id,
            "series_id": record["series_id"],
            "unit": record["unit"],
            "raw_sha256": record["raw_sha256"],
            "native_normalized_sha256": inv[id]["normalized_sha256"],
            "rights_matrix_sha256": sha(encoded(matrix)),
            "scope": "SYNTHETIC_FIXTURE_ONLY"
            if fixture
            else "private_retrospective_only",
            "public_raw_redistribution": record["public_raw_redistribution"],
            "public_derived_redistribution": record["public_derived_redistribution"],
            "historical_point_in_time": "not_established",
            "human_decision_evidence_hash": record["human_admission_decision"][
                "evidence_hash"
            ],
            "human_decision_date": record["human_admission_decision"].get(
                "decision_date"
            ),
            "human_decision_source_message_hash": record[
                "human_admission_decision"
            ].get("source_message_hash"),
            "admission_qualification": record.get(
                "admission_qualification", "private_retrospective_only"
            ),
            "legal_status": record.get("legal_status", "not_a_legal_guarantee"),
            "unresolved_limitations": record.get("unresolved_limitations", []),
            "conditions": record.get("conditions", []),
            "source_attribution": record.get("source_attribution"),
            "public_redistribution_approval": "not_granted",
            "task_01j_authorized": False,
        }
        if id == "diesel_de":
            artifact["monthly_approx_sha256"] = inv["diesel_monthly_approx"][
                "normalized_sha256"
            ]
            artifact["missing_months"] = GAPS
        (output / (id + ".admission.json")).write_bytes(encoded(artifact))
    return admitted


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    p.add_argument("--private-dir", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    try:
        matrix = json.loads((DATA / "rights_admission.json").read_text())
        source = json.loads((DATA / "real_sources.json").read_text())
        decisions = check(matrix, source)
        if a.private_dir:
            verify_private(matrix, source, a.private_dir)
        if a.output:
            if not a.private_dir:
                raise ValueError("Private source directory required")
            admitted = write_private_admissions(matrix, source, a.private_dir, a.output)
            print("Private source admissions written:", len(admitted))
        else:
            print(
                "Rights decisions verified:",
                ", ".join(f"{k}={v['status']}" for k, v in decisions.items()),
            )
    except Exception as e:
        p.exit(
            1,
            f"Rights/admission check refused ({type(e).__name__}); no private values or paths printed\n",
        )


if __name__ == "__main__":
    main()
