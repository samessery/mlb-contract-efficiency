"""Build the analysis-ready team-season panel (30 teams x 2015-2025 = 330 rows).

Input : the Stata dataset assembled during the senior capstone
        (team batting/pitching/fielding metrics from FanGraphs, Opening Day payroll).
Output: data/team_season_2015_2025.csv
"""
import numpy as np
import pandas as pd

SRC = "Master copy.dta"  # path to the original Stata file (not tracked in the repo)
df = pd.read_stata(SRC).rename(columns={"Def": "DEF"})
df["Season"] = df["Season"].astype(int)
df["lnPayroll"] = np.log(df["Payroll"])
df["TeamID"] = df["Team"].astype("category").cat.codes + 1
df.to_csv("data/team_season_2015_2025.csv", index=False)
print(df.shape)
