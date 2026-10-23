"""Deterministic acquisition reports; all reads offline unless fetch is requested."""

import csv
import io
import json
import importlib.metadata as metadata
from pathlib import Path
import re
import statistics as st
import urllib.parse
import urllib.request
from .extract import LICENSE_SHA, PROFILES, month, periods, parse, sha
from contracts.validate import validate_release
from jsonschema import ValidationError


def encoded(value):
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n"
    ).encode()


def csv_bytes(rows, fields):
    stream = io.StringIO(newline="")
    w = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return stream.getvalue().encode()


def local(root, name):
    if not isinstance(name, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]+\.(xlsx|xls|pdf)", name
    ):
        raise ValueError("Noncanonical raw filename")
    p = (Path(root) / name).resolve()
    if not p.is_relative_to(Path(root).resolve()):
        raise ValueError("Raw path escapes root")
    return p


def official(url):
    u = urllib.parse.urlsplit(url)
    if (
        u.scheme != "https"
        or u.netloc != "www.kba.de"
        or not (
            u.path.startswith("/SharedDocs/Downloads/DE/")
            or u.path == "/DE/Service/Hinweise/Datenlizenz/datenlizenz_pdf.pdf"
        )
        or u.fragment
    ):
        raise ValueError("Not an official primary download URL")


def catalog(path):
    c = json.loads(Path(path).read_text())
    if (
        c["catalog_version"] != "1.0.0"
        or c["publisher"] != "Kraftfahrt-Bundesamt, Flensburg"
    ):
        raise ValueError("Unknown catalog")
    if c["license_evidence"]["sha256"] != LICENSE_SHA:
        raise ValueError("Unknown license evidence")
    ids = set()
    months = set()
    files = set()
    for r in c["sources"]:
        month(r["period"])
        official(r["url"])
        local("/tmp", r["file"])
        if r["id"] in ids or r["period"] in months or r["file"] in files:
            raise ValueError("Duplicate month/source or unresolved vintage conflict")
        ids.add(r["id"])
        months.add(r["period"])
        files.add(r["file"])
        if r["id"] != "fz10-" + r["period"] or not re.fullmatch(
            "[0-9a-f]{64}", r["sha256"]
        ):
            raise ValueError("Invalid source identity/hash")
        if (
            r["rights_verified"] is not True
            or r["redistribution_allowed"] is not True
            or r["license_identifier"] != "dl-de/by-2-0"
            or r["license_url"] != "https://www.govdata.de/dl-de/by-2-0"
        ):
            raise ValueError("Unverified rights")
        if not r["version"] or r["revision_history"] != "not_verified":
            raise ValueError("Unsupported vintage assertion")
    return c


def fetch(catalog_path, raw_dir):
    """TLS verified, no alternate data sources, no replacement after hash drift."""
    c = catalog(catalog_path)
    if c.get("catalog_scope") == "table_only_test_fixtures":
        raise ValueError("Test fixtures cannot be fetched as original sources")
    Path(raw_dir).mkdir(parents=True, exist_ok=True)
    for r in [c["license_evidence"]] + c["sources"]:
        official(r["url"])
        p = local(raw_dir, r["file"])
        if p.exists():
            b = p.read_bytes()
        else:
            with urllib.request.urlopen(r["url"], timeout=40) as response:
                official(response.geturl())
                b = response.read()
            if sha(b) != r["sha256"]:
                raise ValueError("Remote vintage/hash drift: " + r["file"])
            # Exclusive creation; never overwrite an existing vintage.
            with p.open("xb") as f:
                f.write(b)
        if sha(b) != r["sha256"]:
            raise ValueError("Cached hash mismatch: " + r["file"])


def extract(c, raw_dir):
    if sha(local(raw_dir, c["license_evidence"]["file"]).read_bytes()) != LICENSE_SHA:
        raise ValueError("License evidence hash mismatch")
    rows = []
    locations = []
    for r in sorted(c["sources"], key=lambda r: r["period"]):
        raw = local(raw_dir, r["file"]).read_bytes()
        if len(raw) != r["bytes"]:
            raise ValueError("Raw length mismatch")
        parsed = parse(raw, r)
        for key in ["sheet", "publication", "revision", "exclusions", "license_cell"]:
            if parsed[key] != r[key]:
                raise ValueError("Catalog/extraction metadata conflict: " + key)
        for o in parsed["observations"]:
            row = dict(
                period=r["period"],
                value=o["value"],
                series=o["series"],
                source=r["id"],
                vintage=r["sha256"],
                powertrain=o["powertrain"],
            )
            rows.append(row)
            locations.append(
                dict(
                    period=r["period"],
                    series=o["series"],
                    source=r["id"],
                    sheet=parsed["sheet"],
                    cell=o["cell"],
                    raw_sha256=r["sha256"],
                    cumulative_value=o.get("cumulative_value"),
                    cumulative_cell=o.get("cumulative_cell"),
                )
            )
    return sorted(rows, key=lambda r: (r["series"], r["period"])), locations


def validate_rows(rows):
    groups = {}
    seen = set()
    for r in rows:
        month(r["period"])
        if (
            isinstance(r["value"], bool)
            or not isinstance(r["value"], int)
            or r["value"] < 0
        ):
            raise ValueError("Invalid count")
        key = (r["series"], r["period"])
        if key in seen:
            raise ValueError("Duplicate/conflicting observation or vintage")
        seen.add(key)
        groups.setdefault(r["series"], []).append(r)
    return {s: sorted(v, key=lambda r: r["period"]) for s, v in groups.items()}


def coverage(rows, start, end):
    pp = sorted(r["period"] for r in rows)
    if len(pp) != len(set(pp)):
        raise ValueError("Duplicate months")
    expected = periods(start, end)
    present = set(pp)
    if any(p not in expected for p in pp):
        raise ValueError("Observation outside declared target")
    runs = []
    current = []
    for p in expected:
        if p in present:
            current.append(p)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    longest = max(runs, key=lambda x: (len(x), x[-1]), default=[])
    return dict(
        first_verified=pp[0] if pp else None,
        last_verified=pp[-1] if pp else None,
        verified_count=len(pp),
        missing_months=[p for p in expected if p not in present],
        longest_contiguous=dict(
            start=longest[0] if longest else None,
            end=longest[-1] if longest else None,
            months=len(longest),
        ),
    )


def release_record(source):
    """Map existing, unchanged KBA provenance; never infer missing publication days."""
    return dict(
        period=source["period"],
        source_url=source["url"],
        sha256=source["sha256"],
        version=source["version"],
        license_identifier=source["license_identifier"],
        license_url=source["license_url"],
        rights_verified=source["rights_verified"],
        publication_date={k: source["publication"][k] for k in ["precision", "value"]},
        retrieved_at=source["retrieved_on"],
        available_as_of=source.get("available_as_of"),
    )


def admission(
    rows,
    sources,
    start,
    end,
    train_months=None,
    design_columns=6,
    as_of=None,
    evidence_root=None,
):
    cov = coverage(rows, start, end)
    n = cov["longest_contiguous"]["months"]
    train = n - 12 if train_months is None else train_months
    reasons = []
    if train < 48 or n - train < 12:
        reasons.append("insufficient_contiguous_training_or_holdout")
    if train - design_columns < 20:
        reasons.append("insufficient_residual_degrees_of_freedom")
    # Admission concerns the entire declared observed window, never silently drop gaps.
    actual_start = cov["first_verified"]
    actual_end = cov["last_verified"]
    if rows and cov["verified_count"] != len(periods(actual_start, actual_end)):
        reasons.append("internal_month_gap")
    metadata = []
    pit = []
    precision = {"day": 0, "month": 0, "unknown": 0}
    if as_of is None:
        pit.append("historical_as_of_cutoff_not_specified")
    for row in rows:
        src = sources.get(row["source"])
        if (
            src is None
            or src["sha256"] != row["vintage"]
            or src.get("rights_verified") is not True
        ):
            metadata.append("source_vintage_or_rights_unverified")
            continue
        try:
            official(src["url"])
            if src.get("parser_profile") not in PROFILES:
                raise ValueError("Unreviewed definition/parser profile")
            if (
                src.get("redistribution_allowed") is not True
                or src.get("license_identifier") != "dl-de/by-2-0"
                or src.get("license_url") != "https://www.govdata.de/dl-de/by-2-0"
            ):
                raise ValueError("Unverified license")
            if src["period"] != row["period"]:
                raise ValueError("Reporting month conflict")
            if (
                row["series"] == "market:BEV"
                and (
                    row["powertrain"] != "BEV_only"
                    or row["period"] < "2021-01"
                    or src["parser_profile"]
                    not in ["fz10-xlsx-bev-v1", "fz10-xlsx-bev-202408-v1"]
                )
            ) or (row["series"].startswith("brand:") and row["powertrain"] != "all"):
                raise ValueError("Definition conflict")
            if row["series"] != "market:BEV" and not row["series"].startswith("brand:"):
                raise ValueError("Unknown series definition")
            release = release_record(src)
            validate_release(release, evidence_root)
            precision[release["publication_date"]["precision"]] += 1
            if release["publication_date"]["precision"] != "day":
                pit.append("historical_publication_day_precision_missing")
            if release["available_as_of"] is None:
                pit.append("exact_vintage_historical_availability_not_verified")
            elif as_of is not None:
                try:
                    validate_release(release, evidence_root, as_of)
                except ValueError:
                    pit.append("exact_vintage_not_evidenced_available_by_cutoff")
        except (KeyError, ValueError, TypeError, ValidationError, OSError):
            metadata.append("source_license_definition_or_date_provenance_invalid")
    if not rows:
        reasons.append("no_verified_observations")
    reasons = sorted(set(reasons + metadata))
    status = (
        "blocked"
        if metadata or "internal_month_gap" in reasons
        else "insufficient_coverage"
        if reasons
        else "admitted"
    )
    retro_reasons = reasons or [
        "verified_official_immutable_reference_rights_definition_and_length"
    ]
    regimes = {
        "retrospective_immutable_reference": dict(
            status=status, reasons=list(retro_reasons)
        ),
        "historical_point_in_time": dict(
            status="blocked" if reasons or pit else "admitted",
            reasons=sorted(set(reasons + pit))
            or ["exact_vintage_availability_evidenced_by_cutoff"],
            as_of=as_of,
        ),
    }
    return dict(
        **cov,
        status=status,
        reasons=retro_reasons,
        admission_contract_version="0.2.1",
        status_regime="retrospective_immutable_reference",
        admission_regimes=regimes,
        publication_precision=precision,
        checked_period=dict(start=actual_start, end=actual_end),
        provenance_status="verified" if not metadata and rows else "blocked",
        vintage_status="hash_bound_single_snapshot"
        if not metadata and rows
        else "blocked",
        source_status="verified_raw_hash_and_parser"
        if not metadata and rows
        else "not_verified",
        license_status="dl-de/by-2-0" if not metadata and rows else "not_verified",
        engineering_candidate_split=dict(
            train_months=max(0, train),
            holdout_months=12,
            train_start=cov["longest_contiguous"]["start"],
            train_end=(
                periods(
                    cov["longest_contiguous"]["start"], cov["longest_contiguous"]["end"]
                )[train - 1]
                if 0 < train <= n
                else None
            ),
            holdout_start=(
                periods(
                    cov["longest_contiguous"]["start"], cov["longest_contiguous"]["end"]
                )[train]
                if 0 <= train < n
                else None
            ),
            holdout_end=cov["longest_contiguous"]["end"],
            residual_df=max(0, train - design_columns),
            design_columns=design_columns,
        ),
        scientific_validation=False,
    )


def describe(rows):
    if len(rows) < 24:
        raise ValueError("At least 24 verified months for characterization")
    pp = [r["period"] for r in rows]
    if pp != periods(pp[0], pp[-1]):
        raise ValueError("Characterization requires complete ordered window")
    y = [r["value"] for r in rows]
    n = len(y)
    mean = st.mean(y)
    sd = st.stdev(y)
    median = st.median(y)
    mad = st.median(abs(v - median) for v in y)
    slope = sum((i - (n - 1) / 2) * (v - mean) for i, v in enumerate(y)) / sum(
        (i - (n - 1) / 2) ** 2 for i in range(n)
    )
    monthly = {
        str(m): st.mean(r["value"] for r in rows if int(r["period"][5:]) == m)
        for m in range(1, 13)
    }
    q = [r["value"] for r in rows if int(r["period"][5:]) % 3 == 0]
    other = [r["value"] for r in rows if int(r["period"][5:]) % 3 != 0]
    shifts = [
        (
            abs(st.mean(y[i : i + 12]) - st.mean(y[i - 12 : i])),
            pp[i],
            st.mean(y[i : i + 12]) - st.mean(y[i - 12 : i]),
        )
        for i in range(12, n - 11)
    ]
    candidate = max(shifts)
    return dict(
        start=pp[0],
        end=pp[-1],
        n=n,
        mean=mean,
        sample_sd=sd,
        cv=sd / mean if mean else None,
        linear_slope_count_per_month=slope,
        annualized_slope_fraction=12 * slope / mean if mean else None,
        monthly_means=monthly,
        quarter_end_mean=st.mean(q),
        other_month_mean=st.mean(other),
        median=median,
        mad=mad,
        robust_outlier_months=[
            p
            for p, v in zip(pp, y)
            if mad > 0 and abs(0.6744897501960817 * (v - median) / mad) > 3.5
        ],
        robust_outlier_undefined=mad == 0,
        largest_exploratory_12_month_mean_shift=dict(
            at=candidate[1], delta_count=candidate[2], causal_attribution=None
        ),
    )


def select(groups, plan):
    w = plan["brand_selection_window"]
    expected = periods(w["start"], w["end"])
    eligible = []
    for s, rows in sorted(groups.items()):
        if not s.startswith("brand:") or s == "brand:TESLA":
            continue
        subset = [r for r in rows if w["start"] <= r["period"] <= w["end"]]
        if [r["period"] for r in subset] != expected:
            continue
        mean = st.mean(r["value"] for r in subset)
        if mean >= 1000:
            eligible.append(
                dict(
                    series=s, mean=mean, cv=st.stdev(r["value"] for r in subset) / mean
                )
            )
    if not eligible:
        return dict(
            C=None,
            D=None,
            eligible=[],
            status="blocked_no_complete_eligible_selection_window",
        )
    c = min(eligible, key=lambda r: (r["cv"], r["series"]))["series"]
    remaining = [r for r in eligible if r["series"] != c]
    d = (
        min(remaining, key=lambda r: (-r["mean"], r["series"]))["series"]
        if remaining
        else None
    )
    return dict(
        C=c,
        D=d,
        eligible=eligible,
        status="selected" if d else "blocked_no_second_brand",
    )


def reconcile(rows, locations):
    groups = validate_rows(rows)
    checks = []
    for loc in locations:
        if loc.get("cumulative_value") is None:
            continue
        year = loc["period"][:4]
        series = loc["series"]
        subset = [r for r in groups[series] if r["period"].startswith(year + "-")]
        if [r["period"] for r in subset] != periods(year + "-01", year + "-12"):
            continue
        total = sum(r["value"] for r in subset)
        checks.append(
            dict(
                series=series,
                year=year,
                sum_of_monthly=total,
                december_cumulative=loc["cumulative_value"],
                delta=total - loc["cumulative_value"],
                source=loc["source"],
                cumulative_cell=loc["cumulative_cell"],
                status="consistent"
                if total == loc["cumulative_value"]
                else "conflict_no_auto_revision",
            )
        )
    return sorted(checks, key=lambda r: (r["series"], r["year"]))


def parser_versions():
    expected = {"openpyxl": "3.1.5", "xlrd": "2.0.2", "et_xmlfile": "2.0.0"}
    actual = {name: metadata.version(name) for name in expected}
    if actual != expected:
        raise RuntimeError("Install pinned requirements-kba.lock parser versions")
    return actual


def products(catalog_path, plan_path, rows, locations):
    c = catalog(catalog_path)
    plan = json.loads(Path(plan_path).read_text())
    groups = validate_rows(rows)
    selection = select(groups, plan)
    candidates = {
        "A": "brand:TESLA",
        "B": "market:BEV",
        "C": selection["C"],
        "D": selection["D"],
    }
    sources = {r["id"]: r for r in c["sources"]}
    reports = {}
    for label, s in candidates.items():
        reports[label] = dict(
            series=s,
            **admission(
                groups.get(s, []), sources, plan["target_start"], plan["target_end"]
            ),
        )
    if c.get("catalog_scope") == "table_only_test_fixtures":
        for report in reports.values():
            report["status"] = "blocked"
            report["reasons"].append("table_only_test_fixture_not_benchmark_input")
            for regime in report["admission_regimes"].values():
                regime["status"] = "blocked"
                regime["reasons"].append("table_only_test_fixture_not_benchmark_input")
    reconciliation = reconcile(rows, locations)
    for report in reports.values():
        conflicts = [
            r["year"]
            for r in reconciliation
            if r["series"] == report["series"] and r["delta"] != 0
        ]
        if conflicts:
            report["status"] = "blocked"
            report["reasons"].append(
                "monthly_sum_differs_from_december_cumulative:" + ",".join(conflicts)
            )
            for regime in report["admission_regimes"].values():
                regime["status"] = "blocked"
                regime["reasons"].append(
                    "monthly_sum_differs_from_december_cumulative:"
                    + ",".join(conflicts)
                )
    for report in reports.values():
        report["baseline_id"] = report["series"]
        report["definition"] = "German passenger-car new registrations; " + (
            "BEV only, all brands"
            if report["series"] == "market:BEV"
            else "exact brand total, all powertrains"
        )
    # Fixed common descriptive window; never shift it to make a series look quieter.
    common_start = max(
        groups[s][0]["period"] for s in candidates.values() if s in groups
    )
    common_start = max(common_start, plan["comparison_window"]["start"])
    common_end = plan["comparison_window"]["end"]
    descriptive = {}
    for s in candidates.values():
        subset = [
            r for r in groups.get(s, []) if common_start <= r["period"] <= common_end
        ]
        if len(subset) >= 24 and [r["period"] for r in subset] == periods(
            common_start, common_end
        ):
            descriptive[s] = describe(subset)
    data = csv_bytes(
        rows, ["period", "value", "series", "source", "vintage", "powertrain"]
    )
    for report in reports.values():
        report["source_catalog_sha256"] = sha(Path(catalog_path).read_bytes())
        report["normalized_data_sha256"] = sha(data)
    outputs = {
        "observations.csv": data,
        "locations.json": encoded(locations),
        "selection.json": encoded(selection),
        "annual-reconciliation.json": encoded(reconciliation),
        "coverage.json": encoded(reports),
        "characterization.json": encoded(descriptive),
    }
    outputs["quality.json"] = encoded(
        dict(
            extractor_implementation="kba_fz10_v1",
            parser_packages=parser_versions(),
            catalog_sha256=sha(Path(catalog_path).read_bytes()),
            plan_sha256=sha(Path(plan_path).read_bytes()),
            normalized_sha256=sha(data),
            raw_sources=len(c["sources"]),
            observations=len(rows),
            class_="observed",
            grain="month",
            geography="DE",
            unit="passenger_car_new_registrations",
            missing_policy="No interpolation, forward fill or symbolic zero conversion",
            vintage_policy="One retrieved raw hash per reporting month; revision history not verified",
            column_lineage={
                k: dict(
                    class_="observed",
                    source="sources.json + locations.json",
                    transformation=v,
                )
                for k, v in dict(
                    period="Exact source reporting month",
                    value="Numeric integer published total only",
                    series="Exact brand total label or explicit BEV market total",
                    source="Source catalog identifier",
                    vintage="SHA-256 of unmodified workbook",
                    powertrain="all for brand D column; BEV_only for explicit market AK column",
                ).items()
            },
        )
    )
    outputs["inventory.json"] = encoded(
        {name: sha(b) for name, b in sorted(outputs.items())}
    )
    return outputs, reports


def run(catalog_path, plan_path, raw_dir, output):
    c = catalog(catalog_path)
    rows, locations = extract(c, raw_dir)
    outputs, reports = products(catalog_path, plan_path, rows, locations)
    root = Path(output)
    if root.exists():
        raise FileExistsError("Choose a new output directory")
    root.mkdir(parents=True)
    for name, b in outputs.items():
        (root / name).write_bytes(b)
    return reports


def verify(catalog_path, plan_path, raw_dir, output):
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        expected = Path(tmp) / "out"
        run(catalog_path, plan_path, raw_dir, expected)
        actual = Path(output)
        if {p.name for p in actual.iterdir()} != {p.name for p in expected.iterdir()}:
            raise ValueError("Output membership mismatch")
        for p in expected.iterdir():
            if p.read_bytes() != (actual / p.name).read_bytes():
                raise ValueError("Output/hash mismatch: " + p.name)


def audit(catalog_path, plan_path, output):
    """Offline normalized-data consistency; does not substitute for raw re-extraction."""
    c = catalog(catalog_path)
    sources = {r["id"]: r for r in c["sources"]}
    root = Path(output)
    fields = ["period", "value", "series", "source", "vintage", "powertrain"]
    with (root / "observations.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != fields:
            raise ValueError("Unexpected normalized columns")
        rows = list(reader)
    for row in rows:
        if set(row) != set(fields) or not re.fullmatch(r"0|[1-9][0-9]*", row["value"]):
            raise ValueError("Invalid normalized row")
        row["value"] = int(row["value"])
        src = sources.get(row["source"])
        if (
            src is None
            or row["vintage"] != src["sha256"]
            or row["period"] != src["period"]
        ):
            raise ValueError("Source/vintage/month conflict")
        if row["series"] == "market:BEV":
            if row["powertrain"] != "BEV_only" or row["period"] < "2021-01":
                raise ValueError("BEV definition conflict")
        elif not row["series"].startswith("brand:") or row["powertrain"] != "all":
            raise ValueError("Brand definition conflict")
    validate_rows(rows)
    if rows != sorted(rows, key=lambda r: (r["series"], r["period"])):
        raise ValueError("Unsorted normalized rows")
    locations = json.loads((root / "locations.json").read_text())
    by_key = {}
    for loc in locations:
        key = (loc["series"], loc["period"])
        if key in by_key:
            raise ValueError("Duplicate cell location")
        by_key[key] = loc
    if len(by_key) != len(rows):
        raise ValueError("Location count mismatch")
    for row in rows:
        loc = by_key.get((row["series"], row["period"]))
        src = sources[row["source"]]
        if (
            not loc
            or loc["source"] != row["source"]
            or loc["raw_sha256"] != src["sha256"]
            or loc["sheet"] != src["sheet"]
            or not re.fullmatch(
                ("AK" if row["series"] == "market:BEV" else "D") + r"[1-9][0-9]*",
                loc["cell"],
            )
        ):
            raise ValueError("Cell/source conflict")
    outputs, _ = products(catalog_path, plan_path, rows, locations)
    if {p.name for p in root.iterdir()} != set(outputs):
        raise ValueError("Output membership mismatch")
    for name, b in outputs.items():
        if (root / name).read_bytes() != b:
            raise ValueError("Output/hash mismatch: " + name)
