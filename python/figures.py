"""Scatter plots with fitted lines: what wins vs. what gets paid."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv("data/team_season_2015_2025.csv")


def scatter(x, y, ylabel, fname, title):
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.scatter(df[x], df[y], s=14, alpha=0.65, color="navy")
    b, a = np.polyfit(df[x], df[y], 1)
    xs = np.linspace(df[x].min(), df[x].max(), 50)
    ax.plot(xs, a + b * xs, color="maroon", lw=2)
    ax.set(xlabel=x, ylabel=ylabel, title=title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"figures/{fname}", dpi=200)
    plt.close(fig)


scatter("ISO", "WinPct", "Winning percentage", "py_winpct_vs_iso.png", "Power (ISO) tracks winning")
scatter("ISO", "lnPayroll", "ln(Opening Day payroll)", "py_lnpayroll_vs_iso.png",
        "...but payroll does not reward it")
