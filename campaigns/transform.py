"""Deterministic documented-activity indicators; missing evidence stays unknown."""

import argparse
import calendar
import csv
from datetime import date, timedelta
import io
import json
from pathlib import Path
import re

CATEGORIES = {
    "paid_media",
    "owned_media",
    "earned_media_pr",
    "sales_promotion",
    "product_event",
    "unknown",
}
QUALITIES = {"verified", "partial", "unverified", "excluded"}
METRICS = ["verified_paid_activity", "active_day_share", "active_campaign_count"]
ROOT = Path(__file__).resolve().parents[1]


def day(value):
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None
    ):
        raise ValueError("Expected exact ISO day")
    return date.fromisoformat(value)


def month(value):
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", value) is None
    ):
        raise ValueError("Expected exact ISO month")
    day(value + "-01")
    return value


def check_date(spec):
    precision, value = spec["precision"], spec["value"]
    if precision == "unknown":
        if value is not None:
            raise ValueError("Unknown dates must be null")
    elif precision == "day":
        day(value)
    elif precision == "month":
        month(value)
    elif precision == "year":
        if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}", value) is None:
            raise ValueError("Expected year")
        day(value + "-01-01")
    else:
        raise ValueError("Unknown date precision")


def eligible(event):
    return (
        event["category"] == "paid_media"
        and event["evidence_class"] == "verified"
        and event["decision"] == "include_paid_indicator"
        and event["geography"]["germany_status"] == "explicit"
    )


def validate(ledger):
    if ledger["ledger_version"] != "1.0.0":
        raise ValueError("Unknown ledger version")
    first, last, asof = map(
        day,
        [ledger["window"]["start"], ledger["window"]["end"], ledger["research_as_of"]],
    )
    if first > last or asof < first:
        raise ValueError("Invalid research window")
    sources = {s["id"]: s for s in ledger["sources"]}
    if len(sources) != len(ledger["sources"]):
        raise ValueError("Duplicate source ID")
    ids = set()
    for event in ledger["events"]:
        if event["id"] in ids:
            raise ValueError("Duplicate event; do not count one campaign twice")
        ids.add(event["id"])
        if (
            event["category"] not in CATEGORIES
            or event["evidence_class"] not in QUALITIES
        ):
            raise ValueError("Unknown category/quality")
        if event["decision"] not in {
            "include_paid_indicator",
            "context_only",
            "exclude",
            "hold",
        }:
            raise ValueError("Unknown decision")
        if not event["source_ids"] or any(
            s not in sources for s in event["source_ids"]
        ):
            raise ValueError("Missing source linkage")
        for bound in ["start", "end"]:
            check_date(event[bound])
            if (
                event[bound]["precision"] != "unknown"
                and not event[bound]["source_ids"]
            ):
                raise ValueError("Known dates need their own source linkage")
            if any(s not in event["source_ids"] for s in event[bound]["source_ids"]):
                raise ValueError("Date evidence not linked")
        a, b = event["start"], event["end"]
        if (
            a["precision"] == "day"
            and b["precision"] == "day"
            and day(a["value"]) > day(b["value"])
        ):
            raise ValueError("Reversed dates")
        if (
            eligible(event)
            and complete_run(event)
            and day(event["end"]["value"]) > asof
        ):
            raise ValueError("A future schedule is not a completed documented run")
        for observation in event["observed_ad_days"]:
            if day(observation["value"]) > asof:
                raise ValueError("Future snapshots cannot be observed activity")
            if observation["source_id"] not in event["source_ids"]:
                raise ValueError("Snapshot without linked source")
        for observation in event["observed_ad_months"]:
            month(observation["value"])
            if observation["source_id"] not in event["source_ids"]:
                raise ValueError("Observed month without source")
        if event["campaign_identity_verified"] and not event.get("campaign_id"):
            raise ValueError("Identified campaigns require a stable campaign ID")
        if event["decision"] == "include_paid_indicator":
            if (
                not eligible(event)
                or not event["paid_media_evidence"]
                or not event["geography"]["germany_evidence"]
            ):
                raise ValueError(
                    "Only explicitly evidenced German paid activity is eligible"
                )
            if not any(
                sources[s]["http_status"] == 200
                and sources[s]["content_status"]
                in {"article_read", "official_content_read", "archived_content_read"}
                for s in event["source_ids"]
            ):
                raise ValueError(
                    "A search result or application shell is not campaign evidence"
                )
            if not event["documented_claim"]:
                raise ValueError("No supported claim")
    return ledger


def complete_run(event):
    return (
        event["interval_status"] == "documented_run"
        and event["start"]["precision"] == "day"
        and event["end"]["precision"] == "day"
        and event["start"]["role"] == "campaign_start"
        and event["end"]["role"] == "campaign_end"
    )


def lag(values, months):
    if months < 0:
        raise ValueError("Lag must be nonnegative")
    return [values[i - months] if i >= months else None for i in range(len(values))]


def transform(ledger):
    validate(ledger)
    first, last, asof = map(
        day,
        [ledger["window"]["start"], ledger["window"]["end"], ledger["research_as_of"]],
    )
    pp = []
    y, m = first.year, first.month
    while (y, m) <= (last.year, last.month):
        pp.append(f"{y:04}-{m:02}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    activity = {p: set() for p in pp}
    run_days = {p: set() for p in pp}
    identities = {p: {} for p in pp}
    for e in ledger["events"]:
        if not eligible(e):
            continue
        seen_days = set()
        if complete_run(e):
            start = max(day(e["start"]["value"]), first)
            end = min(day(e["end"]["value"]), last, asof)
            while start <= end:
                p = start.strftime("%Y-%m")
                run_days[p].add(start)
                seen_days.add(start)
                start += timedelta(days=1)
        for observation in e["observed_ad_days"]:
            d = day(observation["value"])
            if first <= d <= min(last, asof):
                seen_days.add(d)
        for d in seen_days:
            p = d.strftime("%Y-%m")
            activity[p].add(e["id"])
            if e["campaign_identity_verified"]:
                identities[p].setdefault(d, set()).add(e["campaign_id"])
        for observation in e["observed_ad_months"]:
            p = observation["value"]
            if p in activity and p <= asof.strftime("%Y-%m"):
                activity[p].add(e["id"])
    rows = []
    for p in pp:
        year, mo = map(int, p.split("-"))
        rows.append(
            dict(
                period=p,
                verified_paid_activity=1 if activity[p] else None,
                active_day_share=len(run_days[p]) / calendar.monthrange(year, mo)[1]
                if run_days[p]
                else None,
                active_campaign_count=max(map(len, identities[p].values()))
                if identities[p]
                else None,
                supporting_event_ids="|".join(sorted(activity[p])),
            )
        )
    for metric in METRICS:
        for shift in range(4):
            for row, value in zip(rows, lag([r[metric] for r in rows], shift)):
                row[f"{metric}_lag{shift}"] = value
    return rows


def csv_bytes(rows):
    fields = (
        ["period"]
        + METRICS
        + ["supporting_event_ids"]
        + [f"{m}_lag{k}" for m in METRICS for k in range(4)]
    )
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                k: (
                    ""
                    if v is None
                    else format(v, ".12g")
                    if isinstance(v, float)
                    else v
                )
                for k, v in row.items()
            }
        )
    return stream.getvalue().encode()


def summary(ledger, rows):
    paid = [e for e in ledger["events"] if eligible(e)]
    return dict(
        candidate_events=len(ledger["events"]),
        campaign_candidates=sum(
            e["candidate_kind"] == "campaign_candidate" for e in ledger["events"]
        ),
        verified_german_paid_activity_records=len(paid),
        individually_identified_verified_german_paid_campaigns=len(
            {e["campaign_id"] for e in paid if e["campaign_identity_verified"]}
        ),
        verified_german_paid_records_with_complete_run=sum(
            complete_run(e) for e in paid
        ),
        verified_activity_months=[
            r["period"] for r in rows if r["verified_paid_activity"] == 1
        ],
        unknown_activity_months=sum(r["verified_paid_activity"] is None for r in rows),
        confirmed_inactive_months=sum(r["verified_paid_activity"] == 0 for r in rows),
        total_months=len(rows),
        adequately_varying_measured_media_series=False,
        adequacy_reason="Nonexhaustive activity evidence is not observed zeros, spend or exposure; no sufficiently varying measured series established",
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--ledger", type=Path, default=ROOT / "data/tesla_campaigns/evidence.json"
    )
    p.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/tesla_campaigns/monthly_indicators.csv",
    )
    p.add_argument(
        "--summary", type=Path, default=ROOT / "data/tesla_campaigns/summary.json"
    )
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    ledger = json.loads(a.ledger.read_text())
    rows = transform(ledger)
    outputs = {
        a.output: csv_bytes(rows),
        a.summary: (
            json.dumps(summary(ledger, rows), indent=2, sort_keys=True) + "\n"
        ).encode(),
    }
    for path, raw in outputs.items():
        if a.check:
            if path.read_bytes() != raw:
                raise ValueError("Stale or tampered campaign output: " + str(path))
        else:
            path.write_bytes(raw)
    print(json.dumps(summary(ledger, rows), sort_keys=True))


if __name__ == "__main__":
    main()
