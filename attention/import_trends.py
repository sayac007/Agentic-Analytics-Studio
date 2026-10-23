"""Offline, private import of a single official Trends monthly CSV and sidecar."""

import argparse
import calendar
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, urlsplit

from attention.transform import month, timestamp

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/organic_attention"
NORMALIZATION = "google_trends_single_request_relative_0_100"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def periods(start="2018-01", end="2025-12"):
    month(start)
    month(end)
    if start > end:
        raise ValueError("Reversed window")
    y, m = map(int, start.split("-"))
    out = []
    last = tuple(map(int, end.split("-")))
    while (y, m) <= last:
        out.append(f"{y:04}-{m:02}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def validate_metadata(meta, raw, fixture=False):
    required = {
        "version",
        "origin",
        "measure_role",
        "export_method",
        "retrieved_at",
        "source_url",
        "query",
        "geography",
        "category",
        "search_property",
        "request_window",
        "frequency",
        "time_zone",
        "normalization",
        "raw_sha256",
        "csv_locale",
        "rights",
        "export_attestation",
    }
    extended = meta.get("version") == "1.1.0"
    if extended:
        required |= {"source_window", "analysis_windows"}
    if set(meta) != required or meta["version"] not in {"1.0.0", "1.1.0"}:
        raise ValueError("Unknown/missing provenance fields")
    expected_origin = "synthetic" if fixture else "observed"
    if meta["origin"] != expected_origin or meta["measure_role"] != "attention_proxy":
        raise ValueError("Observed and synthetic provenance cannot be interchanged")
    expected_method = "synthetic_test_fixture" if fixture else "official_ui_manual_csv"
    if (
        meta["export_method"] != expected_method
        or meta["export_attestation"] is not True
    ):
        raise ValueError("Requires explicit exporter attestation, not inferred origin")
    retrieved = timestamp(meta["retrieved_at"])
    if meta["raw_sha256"] != sha(raw):
        raise ValueError("Raw CSV hash mismatch")
    if meta["frequency"] != "monthly" or meta["time_zone"] != "UTC":
        raise ValueError(
            "Only native monthly UTC exports supported; no weekly resampling"
        )
    if (
        meta["geography"] != "DE"
        or type(meta["category"]) is not int
        or meta["category"] != 0
        or meta["search_property"] != "web"
    ):
        raise ValueError("Expected DE, category 0 and web search")
    request = meta["request_window"]
    all_history = extended and request == {"selection": "all_available_history"}
    if all_history:
        start = meta["source_window"]["start"] + "-01"
        end = meta["source_window"]["end"] + "-01"
        if meta["source_window"]["start"] != "2004-01":
            raise ValueError("All-history source must start at documented 2004-01")
    else:
        if set(request) != {"start", "end"}:
            raise ValueError("Exact request-window fields required")
        start, end = request["start"], request["end"]
    for v in (start, end):
        if not isinstance(v, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", v):
            raise ValueError("Exact request dates required")
        date.fromisoformat(v)
    if start > end or start[-2:] != "01":
        raise ValueError("Request must start at a whole calendar month")
    if (
        not extended
        and int(end[-2:]) != calendar.monthrange(int(end[:4]), int(end[5:7]))[1]
    ):
        raise ValueError("Request window must contain whole calendar months")
    if extended:
        domain = source_periods(meta)
        if domain[0] != start[:7] or domain[-1] != end[:7]:
            raise ValueError("Source window conflicts with request window")
        if end[:7] > retrieved.strftime("%Y-%m") or (
            not all_history and date.fromisoformat(end) > retrieved.date()
        ):
            raise ValueError("Source includes future periods")
        windows = meta["analysis_windows"]
        allowed = {
            "analysis_2018_2025": {"start": "2018-01", "end": "2025-12"},
            "common_2021_2025": {"start": "2021-01", "end": "2025-12"},
        }
        if "analysis_2018_2025" not in windows or not set(windows) <= set(allowed):
            raise ValueError("Declare the analysis window and optional common window")
        for name, window in windows.items():
            if window != allowed[name] or not set(periods(**window)) <= set(domain):
                raise ValueError("Analysis window conflicts with declared source")
            if window["end"] >= retrieved.strftime("%Y-%m"):
                raise ValueError("Analysis cannot contain current/partial periods")
    elif end[:7] >= retrieved.strftime("%Y-%m"):
        raise ValueError("Request includes future/incomplete periods at retrieval")
    norm = meta["normalization"]
    if (
        type(norm.get("min")) is not int
        or type(norm.get("max")) is not int
        or type(norm.get("rescaled")) is not bool
        or type(norm.get("combined_exports")) is not bool
    ):
        raise ValueError("Normalization bounds/flags have strict types")
    if norm != {
        "kind": NORMALIZATION,
        "window": meta["request_window"],
        "geography": "DE",
        "min": 0,
        "max": 100,
        "rescaled": False,
        "combined_exports": False,
    }:
        raise ValueError("Conflicting scale, normalization window or combined exports")
    q = meta["query"]
    if set(q) != {"kind", "value", "label", "topic_evidence_url"}:
        raise ValueError("Explicit query definition required")
    if not all(isinstance(q[k], str) and q[k].strip() for k in ("value", "label")):
        raise ValueError("Empty query/label")
    if q["kind"] == "search_term":
        if q["value"] != q["label"] or q["topic_evidence_url"] is not None:
            raise ValueError("Search term and CSV label must agree")
    elif q["kind"] == "topic":
        if (
            re.fullmatch(r"/(?:m|g)/[A-Za-z0-9_]+", q["value"]) is None
            or not isinstance(q["topic_evidence_url"], str)
            or not q["topic_evidence_url"].startswith("https://trends.google.com/")
        ):
            raise ValueError("Topic ID needs separately reviewed official evidence")
    else:
        raise ValueError("Unknown query kind")
    url = urlsplit(meta["source_url"])
    if (
        url.scheme != "https"
        or url.netloc != "trends.google.com"
        or url.path.rstrip("/") != "/trends/explore"
    ):
        raise ValueError("Expected official Trends Explore URL")
    params = parse_qs(url.query, keep_blank_values=True)
    for k, value in {
        "q": q["value"],
        "geo": "DE",
        "cat": "0",
        "date": "all" if all_history else start + " " + end,
    }.items():
        actual = params.get(k, ["0"] if extended and k == "cat" else None)
        if actual != [value]:
            raise ValueError("Source URL conflicts with query/geography/window")
    if params.get("gprop", [""]) != [""]:
        raise ValueError("Source property conflicts with web search")
    if meta["csv_locale"] not in {"en", "de"}:
        raise ValueError("Unsupported native CSV locale")
    rights = meta["rights"]
    if (
        set(rights)
        != {"private_analysis_confirmed", "redistribution", "evidence_url", "note"}
        or rights["private_analysis_confirmed"] is not True
        or rights["redistribution"] not in {"not_verified", "permitted"}
        or not isinstance(rights["evidence_url"], str)
        or not rights["evidence_url"].startswith("https://")
        or not isinstance(rights["note"], str)
        or not rights["note"].strip()
    ):
        raise ValueError("Explicit private-use/redistribution review required")
    return source_periods(meta)


def source_periods(meta):
    if meta.get("version") == "1.1.0":
        window = meta["source_window"]
        if set(window) != {"start", "end"}:
            raise ValueError("Exact source-month window required")
        return periods(**window)
    return periods(
        meta["request_window"]["start"][:7], meta["request_window"]["end"][:7]
    )


def parse_csv(raw, meta):
    try:
        rows = list(
            csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
        )
    except (UnicodeError, csv.Error) as e:
        raise ValueError("Malformed UTF-8/comma-separated CSV") from e
    rows = [
        r for r in rows if r
    ]  # Only empty physical lines; never drop malformed fields.
    locale = meta["csv_locale"]
    preamble = (
        "Category: All categories" if locale == "en" else "Kategorie: Alle Kategorien"
    )
    if rows and rows[0] == [preamble]:
        rows = rows[1:]
    geo = "Germany" if locale == "en" else "Deutschland"
    header = [
        "Month" if locale == "en" else "Monat",
        f"{meta['query']['label']}: ({geo})",
    ]
    if not rows or rows[0] != header:
        raise ValueError("Unexpected header, category, query, geography or frequency")
    domain = source_periods(meta)
    values, previous = {}, None
    for row in rows[1:]:
        if len(row) != 2:
            raise ValueError("Malformed row; exactly two columns required")
        period, text = row
        month(period)
        if period not in domain or (previous is not None and period <= previous):
            raise ValueError("Outside window, duplicate or unordered month")
        previous = period
        if text == "":
            value, status = None, "missing_in_export"
        elif text == "<1":
            value, status = None, "censored_below_one"
        else:
            if re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", text) is None:
                raise ValueError("Invalid native numeric index spelling")
            try:
                number = Decimal(text)
            except InvalidOperation as e:
                raise ValueError("Invalid index number") from e
            if not number.is_finite() or not 0 <= number <= 100:
                raise ValueError("Index must be finite and in [0,100]")
            value, status = float(number), "observed_index"
        values[period] = (value, status)
    return [
        dict(
            period=p,
            search_interest_index=values.get(p, (None,))[0],
            value_status=values[p][1] if p in values else "not_in_export",
        )
        for p in domain
    ]


def build_import(raw, meta, fixture=False):
    validate_metadata(meta, raw, fixture)
    rows = parse_csv(raw, meta)
    if meta["version"] == "1.1.0":
        current = timestamp(meta["retrieved_at"]).strftime("%Y-%m")
        request = meta["request_window"]
        truncated_end = (
            "end" in request
            and int(request["end"][-2:])
            < calendar.monthrange(int(request["end"][:4]), int(request["end"][5:7]))[1]
        )
        for r in rows:
            r["period_completeness"] = (
                "completed_calendar_month"
                if r["period"] < current
                and not (truncated_end and r["period"] == meta["source_window"]["end"])
                else "partial_or_unverified_period"
            )
    complete = [
        r
        for r in rows
        if r.get("period_completeness", "completed_calendar_month")
        == "completed_calendar_month"
    ]
    numeric = [r["period"] for r in complete if r["value_status"] == "observed_index"]
    censored = [
        r["period"] for r in complete if r["value_status"] == "censored_below_one"
    ]
    observed = sorted(numeric + censored)
    target = periods()
    known = set(observed)
    report = dict(
        status="synthetic_fixture"
        if fixture
        else "empirically_populated"
        if observed
        else "not_empirically_populated",
        origin=meta["origin"],
        measure_role="attention_proxy",
        raw_sha256=sha(raw),
        provenance=meta,
        numeric_index_months=numeric,
        censored_below_one_months=censored,
        real_observation_months=[] if fixture else observed,
        observed_zero_index_months=[
            r["period"] for r in complete if r["search_interest_index"] == 0
        ],
        coverage_2018_2025=dict(
            required_months=96,
            observed_months=[] if fixture else [p for p in target if p in known],
            unknown_months=96 if fixture else sum(p not in known for p in target),
        ),
        coverage_2021_2025=dict(
            required_months=60,
            observed_months=[] if fixture else [p for p in target[36:] if p in known],
            unknown_months=60 if fixture else sum(p not in known for p in target[36:]),
        ),
        interpolation=False,
        resampling="none_native_monthly",
        historical_point_in_time="not_verified",
        integrity_note="Exporter attestation and checksums do not prove Google origin or legal permission; human verification required. Fixture outputs are never empirical evidence.",
        scale_note="Request-relative sampled search-interest index; zero is not zero searches. <1 is censored, not 0 or 0.5. No spend, impressions or causal interpretation.",
    )
    if meta["version"] == "1.1.0":
        report.update(
            source_window=meta["source_window"],
            analysis_windows=meta["analysis_windows"],
            source_normalization=meta["normalization"],
            source_counts=window_counts(rows),
            derivation="Calendar row selection only; original request-wide index unchanged",
        )
    return rows, report


def window_counts(rows):
    return dict(
        rows=len(rows),
        numeric=sum(r["value_status"] == "observed_index" for r in rows),
        censored=sum(r["value_status"] == "censored_below_one" for r in rows),
        blank=sum(r["value_status"] == "missing_in_export" for r in rows),
        absent=sum(r["value_status"] == "not_in_export" for r in rows),
        partial_or_unverified=sum(
            r.get("period_completeness") == "partial_or_unverified_period" for r in rows
        ),
    )


def derive_windows(rows, meta):
    return {
        name: [
            r.copy() for r in rows if window["start"] <= r["period"] <= window["end"]
        ]
        for name, window in meta["analysis_windows"].items()
    }


def inspect_pending(raw, meta):
    """Structural inspection only: no normalized values or admission artifact."""
    if meta.get("version") != "1.1.0" or meta.get("origin") != "observed":
        raise ValueError("Pending inspection requires an observed 1.1.0 sidecar")
    if meta.get("raw_sha256") != sha(raw):
        raise ValueError("Pending sidecar must bind the original bytes")
    rows = parse_csv(raw, meta)
    for row in rows:
        row["period_completeness"] = "partial_or_unverified_period"
    unresolved = [
        k
        for k in ("retrieved_at", "source_url", "category", "search_property")
        if meta.get(k) is None
    ]
    if meta.get("export_attestation") is not True:
        unresolved.append("export_attestation")
    rights = meta.get("rights", {})
    if rights.get("private_analysis_confirmed") is not True:
        unresolved.append("rights.private_analysis_confirmed")
    if rights.get("redistribution") != "permitted":
        unresolved.append("rights.redistribution")
    try:
        validate_metadata(meta, raw)
        validation = "eligible_for_private_import_only"
    except (ValueError, TypeError, KeyError) as e:
        validation = str(e)
    return dict(
        status="pending_empirical_admission",
        raw_sha256=sha(raw),
        source_window=meta["source_window"],
        analysis_windows=meta["analysis_windows"],
        structural_counts=window_counts(rows),
        unresolved_fields=unresolved,
        admission_validation=validation,
        empirical_admission=False,
        normalized_csvs=[],
        row_observation_status="unverified_observation",
        last_period_completeness="partial_or_unverified_period",
        historical_point_in_time="not_verified",
        note="CSV labels/rows are inspected, not verified UI settings, retrieval or rights. No real values redistributed.",
    )


def csv_bytes(rows):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(
        out,
        fieldnames=list(rows[0]),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()


def blocked_coverage(access):
    evidence = json.loads(access)
    if evidence.get("empirical_collection_stopped") is not True or not any(
        r.get("id") == "trends_explore" and r.get("http_status") == 429
        for r in evidence.get("attempts", [])
    ):
        raise ValueError("Blocked report needs an actual recorded Trends 429")
    return dict(
        status="not_empirically_populated",
        real_observation_months=[],
        numeric_observation_count=0,
        coverage_2018_2025={
            "required_months": 96,
            "observed_months": [],
            "unknown_months": 96,
        },
        coverage_2021_2025={
            "required_months": 60,
            "observed_months": [],
            "unknown_months": 60,
        },
        acquisition="stopped_after_official_ui_http_429",
        access_log_sha256=sha(access),
        observed_csv=None,
        actual_frequency="not_observed",
        redistribution="not_verified_no_data",
        historical_point_in_time="not_verified",
        next_step="User official UI CSV export and private offline import; no invented observations.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Synthetic provenance only; never an empirical result",
    )
    parser.add_argument("--check-blocked", action="store_true")
    parser.add_argument(
        "--inspect-pending",
        action="store_true",
        help="Private structural report only, never empirical admission",
    )
    args = parser.parse_args()
    if args.check_blocked:
        if (
            args.csv
            or args.metadata
            or args.output_dir
            or args.fixture
            or args.inspect_pending
        ):
            parser.error("Blocked report check cannot be combined with an import")
        expected = blocked_coverage((DATA / "task01f_access.json").read_bytes())
        if json.loads((DATA / "real_data_coverage.json").read_text()) != expected:
            raise ValueError("Stale blocked-coverage report")
        print(json.dumps(expected, sort_keys=True))
        return
    if not args.csv or not args.metadata or not args.output_dir:
        parser.error("Supply --csv, --metadata and a new private --output-dir")
    out = args.output_dir.resolve()
    if out == ROOT or ROOT in out.parents or out.exists():
        raise ValueError(
            "Output must be a NEW directory outside the repository (private by default)"
        )
    raw = args.csv.read_bytes()
    # A known test fixture cannot become evidence just by changing its sidecar.
    if not args.fixture and (
        ROOT in args.csv.resolve().parents
        or any(
            sha(p.read_bytes()) == sha(raw)
            for p in (ROOT / "tests/fixtures/trends").glob("*.csv")
        )
    ):
        raise ValueError(
            "Repository/known synthetic fixtures cannot enter observed imports"
        )
    meta_raw = args.metadata.read_bytes()
    meta = json.loads(meta_raw)
    if args.inspect_pending:
        if args.fixture:
            parser.error("Pending inspection is not a fixture admission mode")
        report = inspect_pending(raw, meta)
        report["metadata_sha256"] = sha(meta_raw)
        out.mkdir(parents=True)
        (out / "pending.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        print(
            json.dumps({"status": report["status"], "output": str(out)}, sort_keys=True)
        )
        return
    rows, report = build_import(raw, meta, args.fixture)
    report["metadata_sha256"] = sha(meta_raw)
    report["monthly_csv"] = None
    report["monthly_csv_sha256"] = None
    out.mkdir(parents=True)
    if meta["version"] == "1.0.0" and (
        report["numeric_index_months"] or report["censored_below_one_months"]
    ):
        name = "fixture_monthly.csv" if args.fixture else "observed_monthly.csv"
        data = csv_bytes(rows)
        (out / name).write_bytes(data)
        report["monthly_csv"] = name
        report["monthly_csv_sha256"] = sha(data)
    if meta["version"] == "1.1.0":
        report["outputs"] = {}
        series = {"source": rows, **derive_windows(rows, meta)}
        for name, selected in series.items():
            filename = (
                ("fixture_" if args.fixture else "observed_") + name + "_monthly.csv"
            )
            data = csv_bytes(selected)
            (out / filename).write_bytes(data)
            report["outputs"][name] = dict(
                file=filename,
                sha256=sha(data),
                raw_sha256=sha(raw),
                window={"start": selected[0]["period"], "end": selected[-1]["period"]},
                counts=window_counts(selected),
            )
    (out / "coverage.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "raw_sha256": report["raw_sha256"],
                "output": str(out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
