"""German retail fuel prices from the EU Weekly Oil Bulletin price history.

Reads the official history workbook (sheet ``Prices with taxes``), keeps only the
German Euro-super 95 and automotive diesel columns and writes

* ``weekly.csv``  - every published German weekly value, unchanged except the unit
  (EUR per 1000 litres -> EUR per litre, exact decimal division);
* ``monthly.csv`` - calendar-day weighted monthly approximation (each Monday value
  covers seven days); months with any uncovered day stay empty.

No interpolation, no filling of missing weeks, no deflation. Empty or non-numeric
cells stay missing and are counted. Source: European Commission, DG Energy,
Weekly Oil Bulletin; own calculation. Outputs are written to a caller-chosen
directory: public redistribution of the derived values is **not approved** in this
repository (see docs/ENERGY_RIGHTS_ADMISSION.md), so do not commit them.
"""
import argparse
import calendar
import csv
import datetime as dt
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
from pathlib import Path

SHEET = "Prices with taxes"
COLUMNS = {"euro95": "DE_price_with_tax_euro95", "diesel": "DE_price_with_tax_diesel"}
EXPECTED_UNIT = "1000 l"


def _number(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    try:
        return Decimal(str(value).strip().replace(",", ""))
    except Exception:
        return None


def read_weekly(path):
    """Return weekly German rows sorted by date; validates header and unit row."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    if SHEET not in wb.sheetnames:
        raise ValueError(f"Sheet {SHEET!r} missing")
    rows = wb[SHEET].iter_rows(values_only=True)
    header = list(next(rows))
    next(rows)  # product description row
    units = list(next(rows))
    index = {}
    for key, name in COLUMNS.items():
        if header.count(name) != 1:
            raise ValueError(f"Column {name} must occur exactly once")
        index[key] = header.index(name)
        if str(units[index[key]]).strip() != EXPECTED_UNIT:
            raise ValueError(f"Unexpected unit for {name}: {units[index[key]]!r}")
    out, seen = [], set()
    for row in rows:
        date = row[0]
        if not isinstance(date, dt.datetime):
            continue
        day = date.date()
        if day in seen:
            raise ValueError(f"Duplicate bulletin date {day}")
        seen.add(day)
        record = {"date": day.isoformat()}
        for key, i in index.items():
            value = _number(row[i]) if i < len(row) else None
            record[key] = None if value is None or value <= 0 else value / 1000
        out.append(record)
    out.sort(key=lambda r: r["date"])
    return out


def monthly(weekly, start, end):
    """Calendar-day weighted monthly approximation, same convention as
    ``fuel_oil.import_energy``: a bulletin value dated Monday d covers d..d+6.
    A month gets a value only if **every** calendar day is covered by a
    non-missing weekly value; otherwise it stays empty (no bridging of gaps)."""
    days = {key: {} for key in COLUMNS}
    for r in weekly:
        start_day = dt.date.fromisoformat(r["date"])
        for key in COLUMNS:
            if r[key] is None:
                continue
            for k in range(7):
                day = start_day + dt.timedelta(days=k)
                if day in days[key]:
                    raise ValueError(f"Overlapping weekly intervals at {day}")
                days[key][day] = r[key]
    y, m = map(int, start.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= end:
        period = f"{y:04d}-{m:02d}"
        month_days = [dt.date(y, m, d) for d in range(1, calendar.monthrange(y, m)[1] + 1)]
        record = {"period": period,
                  "bulletins_dated_in_month": sum(r["date"].startswith(period) for r in weekly)}
        for key in COLUMNS:
            covered = [days[key][d] for d in month_days if d in days[key]]
            complete = len(covered) == len(month_days)
            record[f"{key}_eur_per_litre"] = (
                str((sum(covered) / len(covered)).quantize(Decimal("0.0001"), ROUND_HALF_EVEN))
                if complete else "")
            record[f"{key}_days_covered"] = len(covered)
        record["days_in_month"] = len(month_days)
        out.append(record)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def _write(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def run(workbook, output, start, end):
    weekly = read_weekly(workbook)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    weekly_rows = [{"date": r["date"],
                    **{f"{k}_eur_per_litre": "" if r[k] is None else str(r[k]) for k in COLUMNS}}
                   for r in weekly if start <= r["date"][:7] <= end]
    _write(out / "weekly.csv", weekly_rows)
    month_rows = monthly(weekly, start, end)
    _write(out / "monthly.csv", month_rows)
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    summary = {"workbook_sha256": digest(workbook), "start": start, "end": end,
               "weekly_rows": len(weekly_rows), "months": len(month_rows),
               "months_missing_euro95": sum(not r["euro95_eur_per_litre"] for r in month_rows),
               "months_missing_diesel": sum(not r["diesel_eur_per_litre"] for r in month_rows),
               "outputs_sha256": {n: digest(out / n) for n in ("weekly.csv", "monthly.csv")}}
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--workbook", required=True)
    p.add_argument("--output", required=True, help="private directory outside Git")
    p.add_argument("--start", default="2018-01")
    p.add_argument("--end", required=True)
    a = p.parse_args()
    print(json.dumps(run(a.workbook, a.output, a.start, a.end), indent=2, sort_keys=True))
