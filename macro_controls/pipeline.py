"""Offline normalization and conservative coverage; never fills missing observations."""

import argparse
import calendar
import csv
from datetime import date, datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/german_macro"
WINDOWS = (("2018-01", "2025-12"), ("2021-01", "2025-12"))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def months(start, end):
    period(start, "M")
    period(end, "M")
    y, m = map(int, start.split("-"))
    result = []
    while f"{y:04d}-{m:02d}" <= end:
        result.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return result


def period(value, frequency):
    patterns = {
        "M": r"[0-9]{4}-(0[1-9]|1[0-2])",
        "Q": r"[0-9]{4}-Q[1-4]",
        "D": r"[0-9]{4}-[0-9]{2}-[0-9]{2}",
    }
    if (
        frequency not in patterns
        or not isinstance(value, str)
        or not re.fullmatch(patterns[frequency], value)
    ):
        raise ValueError(
            "Invalid period or unsupported frequency (event series are not daily data)"
        )
    if frequency == "D":
        date.fromisoformat(value)
    else:
        date.fromisoformat(value[:4] + "-01-01")
    return value


def https(value):
    if not isinstance(value, str):
        raise ValueError("HTTPS source required")
    u = urlsplit(value)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.fragment:
        raise ValueError("HTTPS source required without credentials/fragment")


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})",
        value,
    ):
        raise ValueError("Offset-aware retrieval timestamp required")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_catalog(catalog):
    if set(catalog) != {"version", "scope", "series"} or catalog["version"] != "1.0.0":
        raise ValueError("Unknown macro catalog contract")
    if catalog["scope"] not in (
        "blocked_research",
        "SYNTHETIC_FIXTURE_ONLY",
        "reviewed_observations",
    ):
        raise ValueError("Invalid scope")
    seen, source_ids = set(), set()
    for s in catalog["series"]:
        required = {
            "id",
            "series_id",
            "provider",
            "definition",
            "country",
            "frequency",
            "unit",
            "seasonal_adjustment",
            "source_url",
            "metadata_status",
            "rights",
            "blockers",
            "candidate_series_id",
            "evidence",
            "definition_details",
        }
        if set(s) != required or not re.fullmatch(r"[a-z][a-z0-9_]+", s["id"]):
            raise ValueError("Catalog fields or stable ID invalid")
        if s["id"] in seen:
            raise ValueError("Duplicate catalog ID")
        seen.add(s["id"])
        https(s["source_url"])
        for name in (
            "provider",
            "definition",
            "country",
            "unit",
            "seasonal_adjustment",
        ):
            if not isinstance(s[name], str) or not s[name].strip():
                raise ValueError("Incomplete definition")
        if s["frequency"] not in ("M", "Q", "D", "unverified"):
            raise ValueError("Invalid native frequency")
        if s["metadata_status"] not in (
            "not_verified",
            "verified",
            "synthetic_fixture",
        ):
            raise ValueError("Invalid metadata status")
        r = s["rights"]
        if set(r) != {"status", "url", "attribution", "note"} or r["status"] not in (
            "not_verified",
            "reviewed_reuse",
            "synthetic_fixture",
        ):
            raise ValueError("Invalid rights evidence")
        https(r["url"])
        if not r["attribution"].strip() or not r["note"].strip():
            raise ValueError("Missing rights documentation")
        if s["metadata_status"] == "not_verified":
            if s["series_id"] is not None or not s["blockers"]:
                raise ValueError("Unverified candidates cannot become admitted series")
        elif (
            not isinstance(s["series_id"], str)
            or not s["series_id"].strip()
            or not s["evidence"]
        ):
            raise ValueError("Verified series requires exact identifier and evidence")
        else:
            if s["series_id"] in source_ids:
                raise ValueError("Duplicate source series identifier")
            source_ids.add(s["series_id"])
            if (
                s["frequency"] == "unverified"
                or s["unit"] == "unverified"
                or s["seasonal_adjustment"] == "unverified"
            ):
                raise ValueError(
                    "Verified source needs exact frequency/unit/adjustment"
                )
        if (
            catalog["scope"] == "blocked_research"
            and s["metadata_status"] != "not_verified"
        ):
            raise ValueError("Blocked report cannot masquerade as reviewed data")
        if (
            catalog["scope"] == "SYNTHETIC_FIXTURE_ONLY"
            and s["metadata_status"] != "synthetic_fixture"
        ):
            raise ValueError("Fixture catalog cannot contain observed metadata")
        if (
            catalog["scope"] == "reviewed_observations"
            and s["metadata_status"] != "verified"
        ):
            raise ValueError(
                "Reviewed catalog cannot contain fixture/unverified metadata"
            )
    return catalog


def admitted(s, fixture):
    validate_catalog(
        {
            "version": "1.0.0",
            "scope": "SYNTHETIC_FIXTURE_ONLY" if fixture else "reviewed_observations",
            "series": [s],
        }
    )
    if fixture:
        if (
            s["metadata_status"] != "synthetic_fixture"
            or s["rights"]["status"] != "synthetic_fixture"
        ):
            raise ValueError("Fixture mode requires synthetic metadata and rights")
        if not s["series_id"].startswith("SYNTHETIC."):
            raise ValueError("Fixture identity required")
    elif (
        s["metadata_status"] != "verified" or s["rights"]["status"] != "reviewed_reuse"
    ):
        raise ValueError(
            "Source metadata/rights not verified; download and normalization blocked"
        )
    if s["frequency"] not in ("M", "Q", "D"):
        raise ValueError("Native frequency not verified")


def normalize(raw, s, provenance, fixture=False):
    """ECB SDMX-CSV core columns or explicitly reviewed handoff of that same shape.

    No Destatis/Bundesbank live layout is claimed to have been tested. No auto unit
    conversion, revision selection, geography substitution, interpolation or as-of use.
    """
    admitted(s, fixture)
    required = {"raw_sha256", "retrieved_at", "release_or_vintage", "source_url"}
    if set(provenance) != required or provenance["raw_sha256"] != digest(raw):
        raise ValueError("Raw hash/provenance mismatch")
    if provenance["source_url"] != s["source_url"]:
        raise ValueError("Source URL mismatch")
    timestamp(provenance["retrieved_at"])
    if (
        not isinstance(provenance["release_or_vintage"], str)
        or not provenance["release_or_vintage"].strip()
    ):
        raise ValueError(
            "Vintage description required; unknown publication is explicit"
        )
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    columns = {
        "KEY",
        "FREQ",
        "REF_AREA",
        "UNIT",
        "TIME_PERIOD",
        "OBS_VALUE",
        "OBS_STATUS",
    }
    if (
        not reader.fieldnames
        or not columns.issubset(reader.fieldnames)
        or len(reader.fieldnames) != len(set(reader.fieldnames))
    ):
        raise ValueError("Unexpected CSV layout")
    result, seen = [], set()
    for row in reader:
        if None in row or None in row.values():
            raise ValueError("Malformed row")
        expected = {
            "KEY": s["series_id"],
            "FREQ": s["frequency"],
            "REF_AREA": s["country"],
            "UNIT": s["unit"],
        }
        if any(row[k] != v for k, v in expected.items()):
            raise ValueError("Series ID/frequency/country/unit drift")
        if row.get("UNIT_MULT", "0") != "0":
            raise ValueError(
                "Unexpected unit multiplier; explicit reviewed conversion required"
            )
        if row.get("ADJUSTMENT", s["seasonal_adjustment"]) != s["seasonal_adjustment"]:
            raise ValueError("Seasonal adjustment drift")
        p = period(row["TIME_PERIOD"], s["frequency"])
        if p in seen:
            raise ValueError(
                "Duplicate/revised observation: resolve vintage upstream, never average"
            )
        seen.add(p)
        flag = row["OBS_STATUS"]
        if flag not in ("A", "P", "E", "M"):
            raise ValueError("Unknown observation status")
        v = row["OBS_VALUE"]
        if v == "":
            if flag != "M":
                raise ValueError("Empty value requires explicit missing status")
            value = None
        else:
            if not re.fullmatch(
                r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", v
            ):
                raise ValueError("Invalid numeric value")
            value = float(v)
            if not math.isfinite(value) or flag == "M":
                raise ValueError("Nonfinite or inconsistent missing status")
            if s["unit"].startswith("index_") and value <= 0:
                raise ValueError("Index must be positive")
        result.append(
            dict(
                series_id=s["series_id"],
                candidate_id=s["id"],
                provider=s["provider"],
                definition=s["definition"],
                country=s["country"],
                frequency=s["frequency"],
                unit=s["unit"],
                seasonal_adjustment=s["seasonal_adjustment"],
                observation_period=p,
                value=value,
                **provenance,
                transformation="none_native",
                rights=s["rights"],
                quality_status={
                    "A": "observed",
                    "P": "provisional",
                    "E": "estimated",
                    "M": "missing",
                }[flag],
                source_class="synthetic" if fixture else "observed",
                historical_as_of="not_established",
            )
        )
    if not result:
        raise ValueError("No observations")
    return sorted(result, key=lambda r: r["observation_period"])


def monthly_rows(rows):
    """Select native monthly observations only; quarterly data never enter this table."""
    return [dict(r) for r in rows if r["frequency"] == "M"]


def daily_monthly_mean(rows):
    """Calendar-day mean only with explicit observations for EVERY day, no carry-forward.

    Business-day series / event tables require a different separately reviewed rule.
    Incomplete months produce null, including an absent last day or missing leap day.
    """
    groups = {}
    identity = None
    for r in rows:
        period(r["observation_period"], "D")
        if r["frequency"] != "D":
            raise ValueError(
                "Requires daily observations, not event/quarter/month data"
            )
        key = (
            r["series_id"],
            r["unit"],
            r["country"],
            r["raw_sha256"],
            r["release_or_vintage"],
        )
        if identity is not None and key != identity:
            raise ValueError("Cannot mix series/units/vintages")
        identity = key
        p = r["observation_period"]
        g = groups.setdefault(p[:7], {})
        if p in g:
            raise ValueError("Duplicate daily observation")
        if r["value"] is not None and not math.isfinite(r["value"]):
            raise ValueError("Nonfinite daily value")
        g[p] = r
    out = []
    for month, g in sorted(groups.items()):
        y, m = map(int, month.split("-"))
        expected = {
            f"{month}-{d:02d}" for d in range(1, calendar.monthrange(y, m)[1] + 1)
        }
        complete = set(g) == expected and all(
            r["value"] is not None for r in g.values()
        )
        r = dict(next(iter(g.values())))
        r.update(
            observation_period=month,
            frequency="M",
            value=math.fsum(g[p]["value"] for p in sorted(g)) / len(expected)
            if complete
            else None,
            transformation="calendar_day_arithmetic_mean_no_fill",
            source_class="synthetic" if r["source_class"] == "synthetic" else "proxy",
            quality_status="derived_complete"
            if complete
            else "incomplete_daily_coverage",
            input_quality_statuses=sorted({r["quality_status"] for r in g.values()}),
        )
        out.append(r)
    return out


def cpi_yoy(rows):
    """100*(I[t]/I[t-12]-1), calendar-matched same-base immutable native index."""
    by_period, identity = {}, None
    for r in rows:
        period(r["observation_period"], "M")
        if r["frequency"] != "M" or not r["unit"].startswith("index_"):
            raise ValueError("Monthly same-base index required")
        key = (r["series_id"], r["unit"], r["raw_sha256"], r["release_or_vintage"])
        if identity is not None and key != identity:
            raise ValueError("Mixed index bases/series/vintages")
        identity = key
        if r["observation_period"] in by_period:
            raise ValueError("Duplicate CPI observation")
        if r["value"] is not None and (
            not math.isfinite(r["value"]) or r["value"] <= 0
        ):
            raise ValueError("Invalid index")
        by_period[r["observation_period"]] = r
    out = []
    for p, original in sorted(by_period.items()):
        lag = f"{int(p[:4]) - 1:04d}{p[4:]}"
        previous = by_period.get(lag)
        valid = (
            original["value"] is not None
            and previous is not None
            and previous["value"] is not None
        )
        r = dict(original)
        r.update(
            series_id=original["series_id"] + ":derived_yoy",
            unit="percent_yoy",
            value=100 * (original["value"] / previous["value"] - 1) if valid else None,
            transformation="100*(I[t]/I[same_month_previous_year]-1)",
            source_class="synthetic"
            if original["source_class"] == "synthetic"
            else "proxy",
            quality_status="derived" if valid else "missing_calendar_lag_or_value",
            input_periods=[lag, p],
            input_quality_statuses=[
                previous["quality_status"] if previous else "absent",
                original["quality_status"],
            ],
        )
        out.append(r)
    return out


def coverage(catalog):
    validate_catalog(catalog)
    if catalog["scope"] != "blocked_research":
        raise ValueError(
            "This report describes blocked real acquisition, not fixture coverage"
        )
    report = {
        "catalog_sha256": digest(encode(catalog)),
        "scope": "NO_REAL_OBSERVATIONS_ACQUIRED",
        "historical_as_of": "not_established",
        "series": [],
    }
    for s in catalog["series"]:
        report["series"].append(
            {
                "id": s["id"],
                "series_id": s["series_id"],
                "status": "blocked_not_verified",
                "native_frequency_verified": False,
                "blockers": s["blockers"],
                "windows": [
                    {
                        "start": a,
                        "end": b,
                        "expected_months": len(months(a, b)),
                        "verified_monthly_observations": 0,
                        "missing_or_unverified_months": len(months(a, b)),
                        "values_inferred": False,
                    }
                    for a, b in WINDOWS
                ],
            }
        )
    return report


def download(s, destination):
    """Reviewed official URL only; exclusive immutable raw write; no CI network calls."""
    admitted(s, fixture=False)
    https(s["source_url"])
    destination = Path(destination)
    if destination.exists():
        raise ValueError("Raw snapshot exists; never overwrite")

    # Do not follow redirects to an unreviewed host/URL.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Redirect requires source review")

    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(s["source_url"], timeout=30) as response:
        raw = response.read()
    retrieved_at = datetime.now().astimezone().isoformat()
    with destination.open("xb") as f:
        f.write(raw)
    return {
        "raw_sha256": digest(raw),
        "retrieved_at": retrieved_at,
        "source_url": s["source_url"],
        "release_or_vintage": "Retrieved immutable snapshot; publication date unknown; sha256="
        + digest(raw),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rebuild-report", action="store_true")
    parser.add_argument("--catalog", type=Path, default=DATA / "sources.json")
    parser.add_argument("--series")
    parser.add_argument("--raw", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--derive", choices=("cpi-yoy", "daily-mean"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        catalog = validate_catalog(json.loads(args.catalog.read_text()))
        if args.check or args.rebuild_report:
            expected = encode(coverage(catalog))
            path = DATA / "coverage.json"
            if args.rebuild_report:
                path.write_bytes(expected)
            elif path.read_bytes() != expected:
                raise ValueError("Coverage drift")
            print("Macro blocked-coverage report verified; no real values or models")
            return
        if args.series is None or args.raw is None or args.output is None:
            raise ValueError(
                "Provide --series, --raw, --output and --provenance (or --download)"
            )
        selected = [s for s in catalog["series"] if s["id"] == args.series]
        if len(selected) != 1:
            raise ValueError("Unknown series")
        s = selected[0]
        expected_scope = (
            "SYNTHETIC_FIXTURE_ONLY" if args.fixture else "reviewed_observations"
        )
        if catalog["scope"] != expected_scope:
            raise ValueError("Catalog scope not admitted")
        if args.output.exists():
            raise ValueError("Output exists; never overwrite")
        if args.download:
            if args.fixture:
                raise ValueError("No live downloads for fixtures")
            provenance = download(s, args.raw)
            # Preserve acquisition metadata even if parsing subsequently fails.
            with args.raw.with_suffix(args.raw.suffix + ".provenance.json").open(
                "xb"
            ) as f:
                f.write(encode(provenance))
        elif args.provenance:
            provenance = json.loads(args.provenance.read_text())
        else:
            raise ValueError("Provenance required")
        rows = normalize(args.raw.read_bytes(), s, provenance, fixture=args.fixture)
        derived = (
            cpi_yoy(rows)
            if args.derive == "cpi-yoy"
            else daily_monthly_mean(rows)
            if args.derive == "daily-mean"
            else []
        )
        payload = {
            "scope": catalog["scope"],
            "catalog_sha256": digest(args.catalog.read_bytes()),
            "native": rows,
            "monthly": monthly_rows(rows),
            "derived_monthly": derived,
        }
        with args.output.open("xb") as f:
            f.write(encode(payload))
        print("Normalized native observations; no model or outcome join")
    except (ValueError, OSError, KeyError, TypeError, csv.Error) as exc:
        parser.exit(1, f"Macro preparation refused: {exc}\n")


if __name__ == "__main__":
    main()
