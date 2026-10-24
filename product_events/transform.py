"""Validate curated evidence and generate point-event indicators; unknown is not zero."""

import argparse
import calendar
from collections import Counter
import csv
from datetime import date
import io
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
import re

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/tesla_product_events"
TYPES = (
    "announcement",
    "orders_open",
    "first_delivery_de",
    "model_refresh",
    "variant_added",
    "variant_removed",
    "price_change",
    "financing_offer",
    "supply_disruption",
    "recall_notice",
    "recall_remedy",
)
ROLES = {
    "announcement": {"announced"},
    "orders_open": {"orders_opened"},
    "first_delivery_de": {"first_delivered_de"},
    "model_refresh": {"announced", "effective"},
    "variant_added": {"orders_opened", "observed_active"},
    "variant_removed": {"effective", "observed_active"},
    "price_change": {"effective"},
    "financing_offer": {"observed_active", "effective"},
    "supply_disruption": {"effective"},
    "recall_notice": {"announced"},
    "recall_remedy": {"remedy_available_from"},
}


def check_date(spec):
    p, v = spec["precision"], spec["value"]
    if p == "unknown":
        if v is not None:
            raise ValueError("Unknown date must be null")
    elif not isinstance(v, str):
        raise ValueError("Known date requires a string value")
    elif p == "day":
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v):
            raise ValueError("Exact day required")
        date.fromisoformat(v)
    elif p == "month":
        if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", v):
            raise ValueError("Exact month required")
        date.fromisoformat(v + "-01")
    elif p == "year":
        if not re.fullmatch(r"[0-9]{4}", v):
            raise ValueError("Exact year required")
        date.fromisoformat(v + "-01-01")


def bounds(spec):
    p, v = spec["precision"], spec["value"]
    if p == "unknown":
        return None
    if p == "day":
        return date.fromisoformat(v), date.fromisoformat(v)
    y = int(v[:4])
    if p == "year":
        return date(y, 1, 1), date(y, 12, 31)
    m = int(v[5:7])
    return date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1])


def unique(rows, key):
    values = [r[key] for r in rows]
    if len(values) != len(set(values)):
        raise ValueError("Duplicate " + key)
    return {r[key]: r for r in rows}


def validate(ledger):
    json.dumps(ledger, allow_nan=False)
    Draft202012Validator(
        json.loads((ROOT / "product_events/schema.json").read_text()),
        format_checker=FormatChecker(),
    ).validate(ledger)
    sources = unique(ledger["sources"], "source_id")
    parents = unique(ledger["parents"], "parent_id")
    taxonomy = unique(ledger["taxonomy"], "offering_id")
    unique(ledger["events"], "event_id")
    unique(ledger["availability_observations"], "snapshot_id")
    for s in sources.values():
        check_date(s["publication_date"])
        u = urlsplit(s["url"])
        if u.scheme != "https" or not u.hostname or u.username:
            raise ValueError("Public HTTPS source URL required")
        pub = s["publication_date"]
        if pub["precision"] != "unknown" and pub["role"] != "published":
            raise ValueError("Source publication is not an event announcement")
        if pub["precision"] == "day" and pub["value"] > s["accessed_on"]:
            raise ValueError("Publication cannot follow retrieval")
        if s["accessed_on"] > ledger["research_as_of"]:
            raise ValueError("Future retrieval")
    seen = set()
    for e in ledger["events"]:
        if e["parent_id"] not in parents or any(
            s not in sources for s in e["source_ids"]
        ):
            raise ValueError("Missing parent/source")
        if e["trim_id"] is not None and e["trim_id"] not in taxonomy:
            raise ValueError("Unknown trim taxonomy")
        if (
            e["trim_id"] is not None
            and taxonomy[e["trim_id"]]["model"] not in e["models"]
        ):
            raise ValueError("Trim taxonomy/model conflict")
        for key in ("date", "end_date"):
            check_date(e[key])
        a, b = e["date"], e["end_date"]
        aa, bb = bounds(a), bounds(b)
        if aa and bb and aa[0] > bb[1]:
            raise ValueError("Reversed event interval")
        if b["precision"] != "unknown" and b["role"] not in {"ended", "planned_end"}:
            raise ValueError("End date must retain its end role")
        key = (e["parent_id"], e["event_type"], a["value"], e["trim_id"])
        if key in seen:
            raise ValueError("Duplicate underlying milestone; merge supporting sources")
        seen.add(key)
        if e["status"] == "verified":
            if (
                e["geography"]["status"]
                not in {"explicit_de", "manufacturer_de_guidance"}
                or not e["geography"]["evidence"].strip()
            ):
                raise ValueError("Verified event needs explicit Germany evidence")
            if (
                e["provenance_category"] != "observed_event"
                or a["role"] not in ROLES[e["event_type"]]
            ):
                raise ValueError(
                    "Hypothesis/planned event cannot be a verified milestone"
                )
            if (
                a["precision"] in {"day", "month"}
                and not "2018-01" <= a["value"][:7] <= "2025-12"
            ):
                raise ValueError("Verified event outside research window")
        if e["price"]:
            p = e["price"]
            if p["model"] not in e["models"]:
                raise ValueError("Price model conflicts with event scope")
            if e["event_type"] != "price_change":
                raise ValueError("Financing/other events are not list-price changes")
            if (
                p["before"] is not None
                and p["after"] is not None
                and p["reported_change"] is not None
                and abs(p["after"] - p["before"] - p["reported_change"]) > 1e-8
            ):
                raise ValueError("Conflicting price arithmetic")
            if e["status"] == "verified" and (
                p["vat_basis"] == "unknown" or p["after"] is None
            ):
                raise ValueError(
                    "Verified comparable price needs VAT basis and quoted price"
                )
        if e["event_type"].startswith("recall_") != (e["recall"] is not None):
            raise ValueError("Recall semantics required only on recall records")
        if e["recall"]:
            r = e["recall"]
            if (
                e["event_type"] == "recall_remedy"
                and e["status"] == "verified"
                and r["remedy_category"] == "unknown"
            ):
                raise ValueError("Verified remedy needs remedy category")
            if (
                r["delivery_constraint"] == "documented"
                and not r["delivery_constraint_evidence"]
            ):
                raise ValueError("Recall does not itself prove delivery constraint")
    for snap in ledger["availability_observations"]:
        if any(s not in sources for s in snap["source_ids"]) or any(
            t not in taxonomy for t in snap["offering_ids"]
        ):
            raise ValueError("Snapshot provenance/taxonomy missing")
    return ledger


def transform(ledger):
    validate(ledger)
    buckets = {f"{y:04}-{m:02}": [] for y in range(2018, 2026) for m in range(1, 13)}
    for e in ledger["events"]:
        d = e["date"]
        if e["status"] == "verified" and d["precision"] in {"day", "month"}:
            period = d["value"][:7]
            if period in buckets:
                buckets[period].append(e)
    rows = []
    for p, events in buckets.items():
        row = {"period": p}
        for kind in TYPES:
            selected = [e for e in events if e["event_type"] == kind]
            row[kind + "_parents"] = (
                len({e["parent_id"] for e in selected}) if selected else None
            )
        row.update(
            month_precision_event_ids="|".join(
                sorted(
                    e["event_id"] for e in events if e["date"]["precision"] == "month"
                )
            ),
            supporting_event_ids="|".join(sorted(e["event_id"] for e in events)),
            manufacturer_guidance_event_ids="|".join(
                sorted(
                    e["event_id"]
                    for e in events
                    if e["geography"]["status"] == "manufacturer_de_guidance"
                )
            ),
            coverage="nonexhaustive_event_evidence",
            model_availability_index=None,
            availability_coverage="insufficient_monthly_configurator_census",
        )
        rows.append(row)
    summary = {
        "lineage": "derived_indicator",
        "ledger_version": ledger["ledger_version"],
        "ledger_canonical_sha256": hashlib.sha256(
            json.dumps(ledger, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "monthly_csv_sha256": hashlib.sha256(csv_bytes(rows)).hexdigest(),
        "events": len(ledger["events"]),
        "parents": len(ledger["parents"]),
        "sources": len(ledger["sources"]),
        "by_type": dict(
            sorted(Counter(e["event_type"] for e in ledger["events"]).items())
        ),
        "by_status": dict(
            sorted(Counter(e["status"] for e in ledger["events"]).items())
        ),
        "verified_event_months": [
            r["period"] for r in rows if r["supporting_event_ids"]
        ],
        "months_without_verified_dated_event": sum(
            not r["supporting_event_ids"] for r in rows
        ),
        "months": len(rows),
        "confirmed_inactive_months": 0,
        "mai_observed_months": 0,
        "limitations": "Nonexhaustive point evidence, not absence or causal exposure; MAI unsupported by isolated snapshots.",
    }
    return rows, summary


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    w = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return stream.getvalue().encode()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    rows, summary = transform(json.loads((DATA / "evidence.json").read_text()))
    outputs = {
        DATA / "monthly_indicators.csv": csv_bytes(rows),
        DATA / "summary.json": (
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        ).encode(),
    }
    for path, raw in outputs.items():
        if a.check:
            if path.read_bytes() != raw:
                raise ValueError("Stale/tampered output: " + str(path))
        else:
            path.write_bytes(raw)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
