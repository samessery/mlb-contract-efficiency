"""Load the panel into SQLite and run every query in sql/queries.sql."""
import re
import sqlite3
import pandas as pd

con = sqlite3.connect("mlb.db")
pd.read_csv("data/team_season_2015_2025.csv").to_sql("team_season", con, if_exists="replace", index=False)
sql = open("sql/queries.sql").read()
for block in [b.strip() for b in sql.split(";") if b.strip()]:
    title = re.match(r"--\s*(.*)", block)
    print("\n##", title.group(1) if title else "query")
    print(pd.read_sql_query(block, con).to_string(index=False))
