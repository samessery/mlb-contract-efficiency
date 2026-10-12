"""Python replication of the capstone's team fixed-effects regressions.

Model 1: WinPct   ~ xwOBA + ISO + FIP + xERA + DEF  (team FE, SEs clustered by team)
Model 2: lnPayroll ~ same regressors
Also runs the additional checks requested in feedback: VIFs and a one-year-lead payroll specification.

Standard errors use Stata's xtreg, fe vce(cluster) convention (G/(G-1) scaling, t with G-1 df),
so output matches Stata.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

X_COLS = ["xwOBA", "ISO", "FIP", "xERA", "DEF"]

df = pd.read_csv("data/team_season_2015_2025.csv")
panel = df.set_index(["Team", "Season"]).sort_index()
panel["lnPayroll_lead"] = panel.groupby(level="Team")["lnPayroll"].shift(-1)
G = panel.index.get_level_values("Team").nunique()


def fe_model(y, data, extra_year_fe=False):
    d = data.dropna(subset=[y])
    m = PanelOLS(d[y], d[X_COLS], entity_effects=True,
                 time_effects=extra_year_fe).fit(cov_type="clustered", cluster_entity=True)
    se = m.std_errors * np.sqrt(G / (G - 1))
    t = m.params / se
    p = pd.Series(2 * stats.t.sf(np.abs(t), G - 1), index=t.index)
    out = pd.DataFrame({"coef": m.params, "se": se, "t": t, "p": p})
    return out, m


tables = {}
for label, y, yfe in [("win_pct", "WinPct", False), ("log_payroll", "lnPayroll", False),
                      ("win_pct_yearFE", "WinPct", True), ("log_payroll_yearFE", "lnPayroll", True),
                      ("log_payroll_lead_yearFE", "lnPayroll_lead", True)]:
    tbl, m = fe_model(y, panel, yfe)
    tbl.round(4).to_csv(f"results/fe_{label}.csv")
    tables[label] = (tbl, m)
    print(f"\n=== {y} (within R2 = {m.rsquared_within:.3f}, N = {m.nobs}) ===")
    print(tbl.round(4))

# Side-by-side: does the market pay for what wins? (sign and significance)
rows = []
for v in X_COLS:
    w, pay = tables["win_pct"][0].loc[v], tables["log_payroll"][0].loc[v]
    rows.append({"metric": v, "win_coef": w.coef, "win_p": w.p, "pay_coef": pay.coef, "pay_p": pay.p})
pd.DataFrame(rows).round(4).to_csv("results/wins_vs_pay_comparison.csv", index=False)

# Multicollinearity check (pooled design matrix with constant)
Xc = sm.add_constant(df[X_COLS])
vif = pd.Series([variance_inflation_factor(Xc.values, i + 1) for i in range(len(X_COLS))],
                index=X_COLS).round(2)
vif.to_csv("results/vif.csv", header=["VIF"])
print("\nVIF:\n", vif.to_string(), f"\nMean VIF: {vif.mean():.2f}")
