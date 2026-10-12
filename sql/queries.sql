-- 1. Ten best regular-season records and what they paid
SELECT Season, Team, Wins, ROUND(WinPct, 3) AS win_pct, ROUND(Payroll / 1e6, 1) AS payroll_m
FROM team_season ORDER BY WinPct DESC LIMIT 10;

-- 2. League average payroll and spread by season
SELECT Season, ROUND(AVG(Payroll) / 1e6, 1) AS avg_payroll_m,
       ROUND(MAX(Payroll) / 1e6, 1) AS max_payroll_m, ROUND(MIN(Payroll) / 1e6, 1) AS min_payroll_m
FROM team_season GROUP BY Season ORDER BY Season;

-- 3. Payroll rank vs. win rank within each season (positive gap = outperformed payroll)
WITH ranked AS (
  SELECT Season, Team, Wins, Payroll,
         RANK() OVER (PARTITION BY Season ORDER BY Payroll DESC) AS payroll_rank,
         RANK() OVER (PARTITION BY Season ORDER BY WinPct DESC)  AS win_rank
  FROM team_season)
SELECT Season, Team, payroll_rank, win_rank, payroll_rank - win_rank AS rank_gap
FROM ranked ORDER BY rank_gap DESC LIMIT 10;

-- 4. Most efficient franchises: average rank gap across 2015-2025
WITH ranked AS (
  SELECT Season, Team,
         RANK() OVER (PARTITION BY Season ORDER BY Payroll DESC) AS payroll_rank,
         RANK() OVER (PARTITION BY Season ORDER BY WinPct DESC)  AS win_rank
  FROM team_season)
SELECT Team, ROUND(AVG(payroll_rank - win_rank), 1) AS avg_rank_gap, COUNT(*) AS seasons
FROM ranked GROUP BY Team ORDER BY avg_rank_gap DESC LIMIT 10;

-- 5. Do high-power offenses get paid more? Average payroll and wins by ISO quartile
WITH q AS (SELECT *, NTILE(4) OVER (ORDER BY ISO) AS iso_quartile FROM team_season)
SELECT iso_quartile, COUNT(*) AS team_seasons, ROUND(AVG(ISO), 3) AS avg_iso,
       ROUND(AVG(Payroll) / 1e6, 1) AS avg_payroll_m, ROUND(AVG(WinPct), 3) AS avg_win_pct
FROM q GROUP BY iso_quartile ORDER BY iso_quartile;

-- 6. Same cut for xwOBA (overall offensive quality)
WITH q AS (SELECT *, NTILE(4) OVER (ORDER BY xwOBA) AS xwoba_quartile FROM team_season)
SELECT xwoba_quartile, COUNT(*) AS team_seasons, ROUND(AVG(xwOBA), 3) AS avg_xwoba,
       ROUND(AVG(Payroll) / 1e6, 1) AS avg_payroll_m, ROUND(AVG(WinPct), 3) AS avg_win_pct
FROM q GROUP BY xwoba_quartile ORDER BY xwoba_quartile;

-- 7. Biggest year-over-year payroll jumps (LAG)
WITH d AS (
  SELECT Season, Team, Payroll,
         LAG(Payroll) OVER (PARTITION BY Team ORDER BY Season) AS prev_payroll
  FROM team_season)
SELECT Season, Team, ROUND(prev_payroll / 1e6, 1) AS prev_m, ROUND(Payroll / 1e6, 1) AS payroll_m,
       ROUND(100.0 * (Payroll - prev_payroll) / prev_payroll, 1) AS pct_change
FROM d WHERE prev_payroll IS NOT NULL ORDER BY pct_change DESC LIMIT 10;

-- 8. Teams that won 90+ games on a below-median payroll
WITH m AS (SELECT Season, AVG(Payroll) AS season_avg FROM team_season GROUP BY Season)
SELECT t.Season, t.Team, t.Wins, ROUND(t.Payroll / 1e6, 1) AS payroll_m, ROUND(m.season_avg / 1e6, 1) AS league_avg_m
FROM team_season t JOIN m USING (Season)
WHERE t.Wins >= 90 AND t.Payroll < m.season_avg ORDER BY t.Wins DESC;
