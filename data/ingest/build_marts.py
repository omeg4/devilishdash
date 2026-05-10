"""Materialise mart.* tables from raw.* tables."""

from __future__ import annotations

import duckdb

SHOTS_PER_GAME_SQL = """
CREATE OR REPLACE TABLE mart.shots_per_game AS
SELECT
    season,
    game_id,
    team,
    COUNT(*)               AS shots,
    ROUND(SUM(x_goal), 4)  AS x_goals,
    SUM(goal)              AS goals
FROM raw.moneypuck_shots
GROUP BY season, game_id, team
ORDER BY season, game_id, team
"""


def build_shots_per_game(con: duckdb.DuckDBPyConnection) -> None:
    """Build / rebuild the shots-per-game mart."""
    con.execute(SHOTS_PER_GAME_SQL)
