"""Monthly design for the multi-brand BVARX: brand groups, fuel, prices, policy.

All inputs are versioned files in ``data/``; every loader validates completeness
and never fills gaps. Months are calendar months ``YYYY-MM``.
"""
import calendar
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

import numpy as np

from regimes.data import calendars

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data/competition_vintage_2026_11/brand_monthly_2021_2026_10.csv"
CHECKS = ROOT / "data/competition_vintage_2026_11/kba_checks.json"
FUEL = ROOT / "data/fuel_prices_de/monthly.csv"
HICP = ROOT / "data/hicp_de/monthly.csv"
CHRONOLOGY = ROOT / "data/policy_regimes_de/chronology.json"

GROUPS = {
    "Tesla": ("TESLA",),
    "VW_Group": ("VW", "AUDI", "SKODA", "SEAT", "PORSCHE"),
    "BMW_Group": ("BMW", "MINI"),
    "Mercedes": ("MERCEDES",),
    "Hyundai_Kia": ("HYUNDAI", "KIA"),
}
ENDOGENOUS = ("log_fuel", "log_market") + tuple(f"alr_{g}" for g in GROUPS)
POLICY = ("innovation_premium", "grant_2023_all", "grant_2023_private",
          "tax_package_2025_07", "grant_2026", "pre_cut_2022_12", "pre_business_end_2023_08")
PRICES = ("log_electricity", "log_new_cars")
EXOGENOUS = ("const", "sin_12", "cos_12", "quarter_end", "national_weekdays") + POLICY + PRICES


def months(start, end):
    y, m = map(int, start.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= end:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return tuple(out)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def counts(periods):
    """Market total, group counts and Rest per month; exact accounting check."""
    checks = {c["period"]: c["market_total"] for c in json.loads(CHECKS.read_text())}
    with PANEL.open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["powertrain"] == "BEV"]
    by = {(r["period"], r["brand"]): r["monthly"] for r in rows}
    out = []
    for p in periods:
        market = checks[p]["monthly_electric"]
        rec = {"period": p, "market": market}
        for g, brands in GROUPS.items():
            vals = [by.get((p, b), "") for b in brands]
            if not all(v.isdigit() for v in vals):
                raise ValueError(f"Missing brand count {g} {p}")
            rec[g] = sum(int(v) for v in vals)
            if rec[g] <= 0:
                raise ValueError(f"Non-positive group count {g} {p}")
        rec["Rest"] = market - sum(rec[g] for g in GROUPS)
        if rec["Rest"] <= 0:
            raise ValueError(f"Non-positive Rest {p}")
        out.append(rec)
    return out


def fuel(periods, column="euro95_bulletin_mean_eur_per_litre"):
    with FUEL.open(encoding="utf-8", newline="") as fh:
        rows = {r["period"]: r[column] for r in csv.DictReader(fh)}
    vals = [rows.get(p, "") for p in periods]
    if any(v == "" for v in vals):
        raise ValueError("Fuel series incomplete for requested months")
    return np.log(np.array([float(v) for v in vals]))


def prices(periods):
    with HICP.open(encoding="utf-8", newline="") as fh:
        rows = {r["period"]: r for r in csv.DictReader(fh)}
    out = []
    for p in periods:
        r = rows.get(p)
        if r is None or r["electricity_index_2025"] == "" or r["new_cars_index_2025"] == "":
            out.append([np.nan, np.nan])
        else:
            out.append([np.log(float(r["electricity_index_2025"])), np.log(float(r["new_cars_index_2025"]))])
    return np.array(out)


def _day_share(period, start, end):
    y, m = map(int, period.split("-"))
    first, last = date(y, m, 1), date(y, m, calendar.monthrange(y, m)[1])
    s = max(first, date.fromisoformat(start))
    e = min(last, date.fromisoformat(end)) if end else last
    return max(0, (e - s).days + 1) / last.day


def policy_table(periods, programmes=None):
    """All programmes (estimable or not) as monthly day shares."""
    chron = json.loads(CHRONOLOGY.read_text())
    progs = {p["id"]: p for p in chron["programmes"]}
    pulses = {p["id"]: p for p in chron["pulses"]}
    ids = programmes or tuple(progs) + tuple(pulses)
    table = np.zeros((len(periods), len(ids)))
    for j, i in enumerate(ids):
        for t, p in enumerate(periods):
            if i in progs:
                table[t, j] = _day_share(p, progs[i]["start"], progs[i]["end"])
            else:
                table[t, j] = float(p == pulses[i]["month"])
    return ids, table


def policy(periods, origin=None):
    """Estimable indicators; after ``origin`` a rule is zeroed unless known by then."""
    _, table = policy_table(periods, POLICY)
    if origin is None:
        return table
    if origin < "2024-01":
        # Unannounced programme ends (2023-12-17) would need separate handling.
        raise ValueError("Real-time policy masking is defined for origins from 2024-01 only")
    chron = json.loads(CHRONOLOGY.read_text())
    known = {p["id"]: p["known_by"] for p in chron["programmes"] + chron["pulses"]}
    y, m = map(int, origin.split("-"))
    cutoff = date(y, m, calendar.monthrange(y, m)[1]).isoformat()
    table = table.copy()
    for j, i in enumerate(POLICY):
        if known[i] > cutoff:
            for t, p in enumerate(periods):
                if p > origin:
                    table[t, j] = 0.0
    return table


def design(periods):
    """Endogenous matrix Y (log levels / ALRs) and full exogenous matrix X."""
    c = counts(periods)
    y = np.column_stack(
        [fuel(periods), np.log([r["market"] for r in c])]
        + [np.log([r[g] / r["Rest"] for r in c]) for g in GROUPS])
    cal = calendars(periods)
    x = np.column_stack([np.ones(len(periods)), cal, policy(periods), prices(periods)])
    return c, y, x


def inputs_sha256():
    return {str(p.relative_to(ROOT)): sha(p) for p in (PANEL, CHECKS, FUEL, HICP, CHRONOLOGY)}
