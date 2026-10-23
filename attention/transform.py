"""Adapt synthetic YouTube API shapes; preserve unknown historical coverage."""

import argparse
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = ("owned", "earned", "community")


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})",
        value,
    ):
        raise ValueError("Timestamp needs an explicit timezone and exact day")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def month(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-(0[1-9]|1[0-2])", value
    ):
        raise ValueError("Expected YYYY-MM")
    datetime.fromisoformat(value + "-01")
    return value


def count(value):
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise ValueError("Invalid cumulative count")
    return int(value)


def adapt(dataset):
    """No empirical ingestion until access/retention/redistribution is reviewed."""
    status = dataset["status"]
    if dataset["version"] != "1.0.0" or status not in {
        "synthetic_fixture",
        "not empirically populated",
    }:
        raise ValueError("Unreviewed empirical ingestion or unknown version")
    if status == "not empirically populated" and (
        dataset["sources"] or dataset["batches"]
    ):
        raise ValueError("An unpopulated dataset cannot contain observations")
    sources = {s["id"]: s for s in dataset["sources"]}
    if len(sources) != len(dataset["sources"]):
        raise ValueError("Duplicate source")
    for s in sources.values():
        if s["category"] not in CATEGORIES:
            raise ValueError("Unknown attention category")
        if s["origin"] != "synthetic" or s["rights"] != "synthetic_fixture_only":
            raise ValueError("Fixture sources must be explicitly synthetic")
        g = s["geography"]
        if set(g) != {"audience_country", "content_germany", "language", "evidence"}:
            raise ValueError("Keep audience, content and language separate")
        if (
            g["audience_country"] not in {"DE", "unknown"}
            or (
                g["content_germany"] is not None
                and type(g["content_germany"]) is not bool
            )
            or g["language"] not in {"de", "other", "unknown"}
        ):
            raise ValueError("Invalid geographic evidence")
        if not isinstance(g["evidence"], str) or not g["evidence"].strip():
            raise ValueError(
                "Geographic coding needs explicit evidence, even if unknown"
            )
    records = {}
    for batch in dataset["batches"]:
        source = sources[batch["source_id"]]
        retrieved = timestamp(batch["retrieved_at"])
        if batch["resource"] not in {"videos", "commentThreads"}:
            raise ValueError("Unsupported resource; snapshots are not historical views")
        response = batch["response"]
        # Even a successful empty first page cannot establish a complete historical census.
        if "error" in response or not isinstance(response.get("items"), list):
            raise ValueError("Failed/malformed API response")
        for item in response["items"]:
            if batch["resource"] == "videos":
                kind, obj = "video_publication", item
                if obj["snippet"]["channelId"] != source["channel_id"]:
                    raise ValueError("Video outside frozen channel selection")
            elif batch["resource"] == "commentThreads":
                kind = "comment_publication"
                if item["snippet"]["channelId"] != source["channel_id"]:
                    raise ValueError("Comments outside frozen channel selection")
                obj = item["snippet"]["topLevelComment"]
            else:
                raise ValueError(
                    "Unsupported resource; snapshots are not historical views"
                )
            published = timestamp(obj["snippet"]["publishedAt"])
            if published > retrieved:
                raise ValueError("Publication after retrieval")
            if not isinstance(obj["id"], str) or not obj["id"]:
                raise ValueError("Missing stable content ID")
            # Validate counters but NEVER use them to form historical monthly views.
            if "viewCount" in obj.get("statistics", {}):
                count(obj["statistics"]["viewCount"])
            record = dict(
                id=obj["id"],
                kind=kind,
                source_id=source["id"],
                category="community"
                if kind == "comment_publication"
                else source["category"],
                published_at=published.isoformat(),
            )
            key = kind, obj["id"]
            if key in records and records[key] != record:
                raise ValueError("Conflicting duplicate identity/publication/category")
            records[key] = record
    return sorted(
        records.values(), key=lambda r: (r["published_at"], r["kind"], r["id"])
    )


def transform(dataset):
    records = adapt(dataset)
    start, end = map(month, (dataset["window"]["start"], dataset["window"]["end"]))
    if start > end:
        raise ValueError("Reversed window")
    tz = ZoneInfo(dataset["aggregation_timezone"])
    grouped = {}
    for r in records:
        period = timestamp(r["published_at"]).astimezone(tz).strftime("%Y-%m")
        grouped.setdefault((period, r["category"], r["kind"]), []).append(r)
    rows = []
    year, mo = map(int, start.split("-"))
    while f"{year:04}-{mo:02}" <= end:
        period = f"{year:04}-{mo:02}"
        row = {"period": period}
        for cat in CATEGORIES:
            for kind, suffix in (
                ("video_publication", "video_publications"),
                ("comment_publication", "comments_published"),
            ):
                selected = grouped.get((period, cat, kind), [])
                # Positive counts describe observed surviving selected content only.
                row[f"{cat}_{suffix}"] = len(selected) if selected else None
            row[f"{cat}_historical_views"] = None
        rows.append(row)
        year, mo = (year + 1, 1) if mo == 12 else (year, mo + 1)
    return rows, records


def csv_bytes(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def diagnostics(dataset, rows, records):
    observed = [
        r["period"]
        for r in rows
        if any(v is not None for k, v in r.items() if k != "period")
    ]
    shared = [r for r in rows if "2021-01" <= r["period"] <= "2025-12"]
    return dict(
        status=dataset["status"],
        lineage="synthetic" if records else "no_observations",
        window=dataset["window"],
        aggregation_timezone=dataset["aggregation_timezone"],
        months=len(rows),
        observed_months=observed,
        unknown_months=len(rows) - len(observed),
        shared_2021_2025_months=len(shared),
        shared_2021_2025_observed_months=[
            r["period"] for r in shared if r["period"] in observed
        ],
        distinct_observed_sources=len(
            {r["source_id"] for r in records if start_in_window(r, dataset)}
        ),
        real_historical_observations=0,
        historical_views_available=False,
        sentiment_available=False,
        zero_imputation=False,
        limitation="No empirical data populated; fixture counts are not Tesla observations. No absence/zero, reach, German audience, sentiment or historical view inference.",
    )


def start_in_window(record, dataset):
    p = (
        timestamp(record["published_at"])
        .astimezone(ZoneInfo(dataset["aggregation_timezone"]))
        .strftime("%Y-%m")
    )
    return dataset["window"]["start"] <= p <= dataset["window"]["end"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=ROOT / "data/organic_attention/observations.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "data/organic_attention/monthly_indicators.csv",
    )
    parser.add_argument(
        "--summary", type=Path, default=ROOT / "data/organic_attention/summary.json"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    dataset = json.loads(args.input.read_text())
    rows, records = transform(dataset)
    report = diagnostics(dataset, rows, records)
    outputs = {
        args.output: csv_bytes(rows),
        args.summary: (json.dumps(report, indent=2, sort_keys=True) + "\n").encode(),
    }
    for path, raw in outputs.items():
        if args.check:
            if path.read_bytes() != raw:
                raise ValueError("Stale/tampered attention artifact: " + str(path))
        else:
            path.write_bytes(raw)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
