"""Hash-bound complete monthly KBA data, calendars, and dated policy design."""
import calendar
import csv
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.special import logit, softmax
from dateutil.easter import easter

ROOT = Path(__file__).resolve().parents[1]
PERIODS = tuple(f"{y}-{m:02}" for y in range(2021, 2027) for m in range(1, 13)
                if (y, m) <= (2026, 9))
CALENDAR = ("sin_12", "cos_12", "quarter_end", "national_weekdays")
POLICY = ("grant_cut_2023_01", "business_end_2023_09", "post_end_2024_01",
          "grant_2026_01", "transition_2023_12", "transition_2024_01")
# Publication precision remains in policy_chronology.json; historical 2023 rules
# precede every 2025/26 evaluation origin, not a reconstructed real-time vintage.
KNOWN_BY = ("2024-12-31", "2024-12-31", "2023-12-18",
            "2026-01-19", "2023-12-18", "2023-12-18")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_observed():
    audit = json.loads((ROOT / "data/task04_regimes/data_audit.json").read_text())
    allowed = {"data/competition/brand_monthly_2021_2026.csv",
               "data/competition/kba_checks.json", "data/competition/kba_sources.json"}
    if set(audit["inputs_sha256"]) != allowed:
        raise ValueError("Unexpected input identity")
    for name, expected in audit["inputs_sha256"].items():
        if sha(ROOT / name) != expected:
            raise ValueError("KBA source hash mismatch: " + name)
    checks = {r["period"]: r for r in json.loads((ROOT / "data/competition/kba_checks.json").read_text())}
    with (ROOT / "data/competition/brand_monthly_2021_2026.csv").open(newline="") as fp:
        rows = list(csv.DictReader(fp))
    records = audit["monthly"]
    if tuple(x["period"] for x in records) != PERIODS:
        raise ValueError("Need exactly 69 chronological months, no filling")
    for r in records:
        selected = [v for v in rows if v["period"] == r["period"] and
                    v["powertrain"] == "BEV" and v["brand"] in {"TESLA", "VW"}]
        if len(selected) != 2 or len({v["brand"] for v in selected}) != 2:
            raise ValueError("Duplicate/missing brand month")
        brands = {v["brand"]: int(v["monthly"]) for v in selected}
        total = checks[r["period"]]["market_total"]
        if (r["BEV_official"], r["Pkw_official"], r["Tesla"], r["VW"]) != (
                total["monthly_electric"], total["monthly_all"], brands["TESLA"], brands["VW"]):
            raise ValueError("Audit values do not match original bound extraction")
    values = np.array([[r[k] for k in ("BEV_official", "Tesla", "VW", "Pkw_official")]
                       for r in records], dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any() or np.any(values != np.floor(values)):
        raise ValueError("Invalid observed count")
    rest = values[:, 0] - values[:, 1] - values[:, 2]
    if (rest <= 0).any() or (values[:, 0] >= values[:, 3]).any():
        raise ValueError("Invalid group partition or market denominator")
    y = np.column_stack([np.log(values[:, 0]), np.log(values[:, 1] / rest),
                         np.log(values[:, 2] / rest)])
    return records, values, y


def calendars(periods=PERIODS):
    rows = []
    for i, p in enumerate(periods):
        year, month = map(int, p.split("-"))
        sunday = easter(year)
        holidays = {date(year, 1, 1), date(year, 5, 1), date(year, 10, 3),
                    date(year, 12, 25), date(year, 12, 26)}
        holidays |= {sunday + timedelta(days=d) for d in (-2, 1, 39, 50)}
        days = [date(year, month, d) for d in range(1, calendar.monthrange(year, month)[1]+1)]
        working = sum(d.weekday() < 5 and d not in holidays for d in days)
        # Absolute month fixes Fourier phase in training and future.
        t = (year - 2021) * 12 + month - 1
        rows.append([np.sin(2*np.pi*t/12), np.cos(2*np.pi*t/12),
                     float(month % 3 == 0), working])
    return np.array(rows, dtype=float)


def policy(periods=PERIODS, origin=None, portal=False):
    x = np.array([[p >= "2023-01", p >= "2023-09", p >= "2024-01",
                   p >= ("2026-05" if portal else "2026-01"),
                   p == "2023-12", p == "2024-01"] for p in periods], dtype=float)
    if origin is not None:
        year, month = map(int, origin.split("-"))
        cutoff = date(year, month, calendar.monthrange(year, month)[1]).isoformat()
        for j, known in enumerate(KNOWN_BY):
            for i, p in enumerate(periods):
                if p > origin and known > cutoff:
                    x[i, j] = 0.0
    return x


def system(model, sd, ntrain, *, portal=False, logit_market=False, periods=PERIODS):
    if model not in ("M0", "M1", "M2") or not 1 <= ntrain <= len(periods):
        raise ValueError("Invalid fixed model or training prefix")
    if sd <= 0 or not np.isfinite(sd):
        raise ValueError("State SD must be finite and positive")
    cal = calendars(periods)
    cal[:, 3] -= cal[:ntrain, 3].mean()
    pol = policy(periods, periods[ntrain-1], portal)
    m = np.column_stack([cal, pol]) if model == "M2" else cal
    names = [f"market:{n}" for n in CALENDAR + (POLICY if model == "M2" else ())]
    names += [f"{g}:{n}" for g in ("Tesla", "VW") for n in CALENDAR]
    d = 4 + len(names)
    H = np.zeros((len(periods), 3, d))
    H[:, 0, 0] = H[:, 1, 2] = H[:, 2, 3] = 1.0
    H[:, 0, 4:4+m.shape[1]] = m
    offset = 4 + m.shape[1]
    H[:, 1, offset:offset+4] = cal
    H[:, 2, offset+4:offset+8] = cal
    F = np.eye(d); F[0, 1] = 1
    q = np.zeros(d)
    if model != "M0":
        q[:4] = [sd**2, .01**2, sd**2, sd**2]
    mean = np.zeros(d)
    mean[0] = logit(.2) if logit_market else np.log(50000)
    prior_sd = [1.5, .05, 2, 2] + [.5, .5, 1, .05]
    if model == "M2":
        prior_sd += [.5, .5, .5, .5, 1, 1]
    prior_sd += [.5, .5, 1, .05] * 2
    P = np.diag(np.square(prior_sd))
    for k in range(3):
        active = H[:ntrain, k, 4:]
        active = active[:, np.any(active != 0, axis=0)]
        # Exact-zero policy columns are proper-prior-only, not fitted effects.
        X = np.column_stack([np.ones(ntrain), np.arange(ntrain)]) if k == 0 else np.ones((ntrain, 1))
        X = np.column_stack([X, active])
        if ntrain >= 48 and np.linalg.matrix_rank(X) != X.shape[1]:
            raise ValueError("Rank-deficient observed design")
    return H, F, np.diag(q), mean, P, names


def observed_coordinates(values, logit_market=False):
    total, tesla, vw, cars = values.T
    rest = total-tesla-vw
    return np.column_stack([logit(total/cars) if logit_market else np.log(total),
                            np.log(tesla/rest), np.log(vw/rest)])


def counts(coordinates, car_total=None):
    coordinates = np.asarray(coordinates)
    shares = softmax(np.concatenate([coordinates[..., 1:], np.zeros_like(coordinates[..., :1])], axis=-1), axis=-1)
    market = np.exp(coordinates[..., 0]) if car_total is None else car_total/(1+np.exp(-coordinates[..., 0]))
    return np.concatenate([market[..., None], market[..., None]*shares], axis=-1)
