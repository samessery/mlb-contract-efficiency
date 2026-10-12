# Do MLB Contracts Reward the Right Skills?

Team-level test of whether Major League Baseball payrolls reward the statistics that best explain winning in the Statcast era. Revisits the Moneyball question (Hakes and Sauer, 2006; 2015) with 330 team-seasons, 2015 to 2025.

Originally written as my senior capstone at Providence College (Fall 2025). This repo contains the analysis-ready data, a Python replication, and a set of SQL queries over the same panel.

## Question

If the labor market is efficient, the skills that drive wins should also be the skills that drive pay. I estimate two team fixed-effects models with the same regressors and compare coefficients:

1. `WinPct ~ xwOBA + ISO + FIP + xERA + DEF`
2. `ln(Payroll) ~ xwOBA + ISO + FIP + xERA + DEF`

Standard errors are clustered by team (30 clusters). The panel is strongly balanced: 30 franchises x 11 seasons.

## Data

| Source | Used for |
|---|---|
| FanGraphs team leaderboards | xwOBA, ISO, FIP, xERA, defensive runs saved above average (DEF) and other batting, pitching, fielding metrics |
| SteveTheUmp.com / Baseball Reference | Opening Day payroll, wins, games |

`data/team_season_2015_2025.csv` is the merged panel (one row per team-season). Franchises are coded under their current name.

## Results (team fixed effects, clustered SEs)

| Metric | Wins: coef | p | Payroll: coef | p |
|---|---|---|---|---|
| xwOBA | 1.557 | <0.001 | 12.194 | <0.001 |
| ISO | 0.977 | <0.001 | -6.147 | 0.015 |
| FIP | -0.073 | <0.001 | 0.106 | 0.544 |
| xERA | -0.024 | 0.058 | -0.307 | 0.048 |
| DEF | 0.0007 | <0.001 | -0.0004 | 0.694 |

Within R-squared: 0.697 (wins), 0.118 (payroll).

- **Overall offense is priced.** xwOBA is large, positive, and significant in both models. A 10-point rise in team xwOBA is associated with about 0.016 higher win percentage (roughly 2.5 wins per 162 games).
- **Power is not.** ISO strongly predicts winning but has a negative payroll coefficient.
- **Pitching and defense are weakly priced.** FIP and DEF predict wins but show no significant payroll premium. xERA is marginal in the win model (p = 0.058).

### Robustness and caveats

- **VIFs:** FIP 7.08, xERA 6.54, xwOBA 2.44, ISO 2.34, DEF 1.23 (mean 3.93). FIP and xERA are highly correlated, so their individual coefficients should be read together.
- **Year fixed effects** (`results/fe_*_yearFE.csv`): xwOBA stays strongly significant in both models, but the ISO payroll coefficient falls to -4.01 (p = 0.064) and xERA to -0.23 (p = 0.072). The "power is underpriced" result is suggestive, not firm.
- **One-year-lead payroll with team and year effects:** xwOBA remains significant (p < 0.001). ISO and xERA are not significant. This differs from the capstone paper, which described no significant metrics in the lagged specification, so that paragraph should be read against `results/fe_log_payroll_lead_yearFE.csv`.
- **2020:** payroll for the 60-game season appears prorated, which makes 2020 a low outlier in payroll. The main models do not adjust for it.
- These are associations from team-level data, not player-level causal estimates.

## Revisions since the capstone

The paper is unchanged. Re-running the analysis from the raw data in Python, and checking it against Stata output, changed how I would describe some results:

- The lagged-payroll robustness check is less null than the capstone paper describes (see the caveats above).
- 2020 payroll is prorated for the 60-game season and the original models do not adjust for it.
- Within-season association is a different question from forecasting. The `mlb-win-forecasting` repo tests the forecasting version and finds that these skill metrics add little beyond last year's win percentage.

## Repository layout

```
data/       analysis-ready panel (CSV)
python/     data prep, fixed-effects replication, figures, SQL runner
sql/        queries.sql (window functions, joins, aggregations)
results/    regression tables, VIFs, wins-vs-pay comparison
figures/    scatter plots and correlation heatmap
```

## How to run

```bash
pip install -r requirements.txt
python python/fixed_effects.py     # regressions, VIFs, robustness (writes results/)
python python/figures.py           # extra figures
python python/run_sql.py           # loads SQLite and runs every query in sql/queries.sql
```

The Python estimates match Stata's xtreg output exactly (coefficients, clustered standard errors, p-values), using Stata's small-sample convention for clustered errors.

## SQL examples

`sql/queries.sql` answers questions such as: which franchises most consistently beat their payroll rank (Tampa Bay, Cleveland, and Milwaukee lead), whether power-heavy offenses are paid more (payroll flattens after the third ISO quartile), and which teams won 90+ games on below-average payrolls.

## How this repo fits with my other baseball work

The common thread is **inefficiency**: payroll buys wins at a fairly stable rate, but how much teams get for their money varies, and the same win is worth different amounts to different teams.

| Repo | Question |
|---|---|
| `mlb-contract-efficiency` (this one) | Does the labor market pay for the skills that win? |
| `mlb-competitive-balance` | Do payroll dispersion and the luxury tax move competitive balance? Includes revisions to the original paper. |
| `mlb-efficiency-frontier` | How far below the best-practice frontier do teams fall, and does the gap persist or rotate? |
| `mlb-win-forecasting` | Do skill metrics and payroll forecast next year's wins beyond regression to the mean? |
| `mlb-playoff-value` | What is one extra win worth, by team quality and playoff format? |
| `mlb-player-salary-structure` | How does pay respond to production across a career, and who captures the surplus? |

## Author

Samuel Essery, B.S. Quantitative Economics, Providence College.
