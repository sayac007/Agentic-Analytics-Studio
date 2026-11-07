"""Figures for results/multibrand from saved CSVs only (no fitting)."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/multibrand"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"
BAND = "#b7d3f6"


def rows(name):
    with (OUT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def irf_figure():
    data = [r for r in rows("irf_fuel_shock.csv") if r["spec"] == "primary" and r["h"] != "cum_0_11"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), facecolor=SURFACE)
    for ax, (var, title) in zip(axes, (("log_market", "BEV market (log)"),
                                       ("alr_Tesla", "Tesla vs Rest (log ratio)"))):
        sel = [r for r in data if r["variable"] == var]
        h = [int(r["h"]) for r in sel]
        ax.fill_between(h, [float(r["lower95"]) for r in sel], [float(r["upper95"]) for r in sel],
                        color=BAND, linewidth=0, label="95 % band")
        ax.plot(h, [float(r["median"]) for r in sel], color=BLUE, linewidth=2, label="Posterior median")
        ax.axhline(0, color=MUTED, linewidth=1)
        style(ax)
        ax.set_title(title, loc="left", color=INK, fontsize=11)
        ax.set_xlabel("Months after a one-SD Euro-super 95 price shock", color=MUTED, fontsize=9)
        ax.set_xticks(range(0, 13, 3))
    axes[0].legend(frameon=False, fontsize=9, labelcolor=MUTED, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "irf_fuel_shock.png", dpi=160, metadata={"Software": "Matplotlib"})
    plt.close(fig)


def tesla_figure():
    pred = [r for r in rows("predictions.csv") if r["outcome"] == "Tesla" and r["horizon"] == "1"]
    bv = sorted((r for r in pred if r["spec"] == "primary"), key=lambda r: r["target"])
    m2 = {r["target"]: float(r["prediction_median"]) for r in pred if r["spec"] == "M2"}
    t = [r["target"] for r in bv]
    x = range(len(t))
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=SURFACE)
    ax.fill_between(x, [float(r["lower95"]) for r in bv], [float(r["upper95"]) for r in bv],
                    color=BAND, linewidth=0, label="BVARX 95 % interval")
    ax.plot(x, [float(r["actual"]) for r in bv], color=INK, linewidth=2, label="Actual (KBA)")
    ax.plot(x, [float(r["prediction_median"]) for r in bv], color=BLUE, linewidth=2, marker="o",
            markersize=4, label="BVARX one-month-ahead")
    xm = [i for i, p in enumerate(t) if p in m2]
    ax.plot(xm, [m2[t[i]] for i in xm], color=ORANGE, linewidth=2, marker="o", markersize=4,
            label="Task 04 M2 one-month-ahead")
    style(ax)
    ax.set_xticks(list(x)[::3])
    ax.set_xticklabels(t[::3])
    ax.set_ylabel("Tesla BEV registrations per month", color=MUTED, fontsize=9)
    ax.set_title("Tesla Germany: one-month-ahead forecasts, January 2025 – October 2026",
                 loc="left", color=INK, fontsize=11)
    ax.legend(frameon=False, fontsize=9, labelcolor=MUTED, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "tesla_forecasts_h1.png", dpi=160, metadata={"Software": "Matplotlib"})
    plt.close(fig)


if __name__ == "__main__":
    irf_figure()
    tesla_figure()
    print("Wrote irf_fuel_shock.png and tesla_forecasts_h1.png")
