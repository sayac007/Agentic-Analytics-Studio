"""Figure for docs/management-summary-volkswagen/: annual BEV shares of VW Group and Tesla.

Computed from data/competition_vintage_2026_11 (KBA FZ10). No model output.
python -m scripts.vw_summary_figure
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/competition_vintage_2026_11"
OUT = ROOT / "docs/management-summary-volkswagen/bev_share_vw_tesla.png"
GROUPS = {"VW-Konzern": ("VW", "AUDI", "SKODA", "SEAT", "PORSCHE"), "Tesla": ("TESLA",)}
YEARS = ("2021", "2022", "2023", "2024", "2025", "2026")
INK, MUTED, GRID, SURFACE, BLUE, GREY = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#2a78d6", "#b9b8b2"


def annual_shares():
    """{year: {group: (registrations, market, share_percent)}}; 2026 = Jan-Oct."""
    checks = {c["period"]: c["market_total"] for c in json.loads((DATA / "kba_checks.json").read_text())}
    with (DATA / "brand_monthly_2021_2026_10.csv").open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["powertrain"] == "BEV"]
    by = {(r["period"], r["brand"]): int(r["monthly"]) for r in rows if r["monthly"].isdigit()}
    out = {}
    for y in YEARS:
        periods = [p for p in checks if p.startswith(y)]
        market = sum(checks[p]["monthly_electric"] for p in periods)
        out[y] = {}
        for g, brands in GROUPS.items():
            regs = sum(by.get((p, b), 0) for p in periods for b in brands)
            out[y][g] = (regs, market, regs / market * 100)
    return out


def figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    s = annual_shares()
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    x = range(len(YEARS))
    for g, col, dy in (("Tesla", GREY, -14), ("VW-Konzern", BLUE, 9)):
        vals = [s[y][g][2] for y in YEARS]
        ax.plot(x, vals, color=col, linewidth=2.5, marker="o", markersize=7)
        for i, v in zip(x, vals):
            ax.annotate(f"{v:.1f} %".replace(".", ","), (i, v), textcoords="offset points", xytext=(0, dy),
                        ha="center", fontsize=9, color=INK)
        ax.annotate(g, (len(YEARS) - 1, vals[-1]), textcoords="offset points", xytext=(14, -3),
                    fontsize=10, fontweight="bold", color=INK)
    ax.set_xticks(list(x))
    ax.set_xticklabels([y if y != "2026" else "2026 (Jan–Okt)" for y in YEARS])
    ax.set_ylim(0, 50)
    ax.set_xlim(-0.3, len(YEARS) - 0.2)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f} %"))
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9, left=False)
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    ax.set_title("VW-Konzern-Anteil: Höchststand 2025 im Tesla-Tief, 2026 wieder 34 %", loc="left",
                 color=INK, fontsize=12)
    fig.text(0.01, 0.01, "Anteil an den Elektroauto-Neuzulassungen in Deutschland. "
             "Quelle: Kraftfahrt-Bundesamt FZ10, dl-de/by-2-0; eigene Berechnung.", fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160, metadata={"Software": "Matplotlib"})
    plt.close(fig)


if __name__ == "__main__":
    figure()
    print("Wrote", OUT.relative_to(ROOT))
