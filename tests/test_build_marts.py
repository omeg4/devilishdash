from __future__ import annotations

from pathlib import Path

from data.ingest import build_marts
from devilishdash import data


def _seed(con):
    data.ensure_schemas(con)
    con.execute("""
        CREATE TABLE IF NOT EXISTS raw.moneypuck_shots (
            shot_id BIGINT, season INTEGER, game_id BIGINT, team VARCHAR,
            shooter_id BIGINT, x_cord_adjusted DOUBLE, y_cord_adjusted DOUBLE,
            shot_type VARCHAR, x_goal DOUBLE, goal INTEGER,
            fetched_at TIMESTAMP
        )
    """)
    con.execute("""
        INSERT INTO raw.moneypuck_shots VALUES
          (1, 2024, 100, 'NJD', 1, 70.0, 0.0, 'WRIST', 0.05, 0, NULL),
          (2, 2024, 100, 'NJD', 1, 80.0, 0.0, 'SLAP',  0.04, 1, NULL),
          (3, 2024, 100, 'BUF', 2, 60.0, 0.0, 'WRIST', 0.06, 0, NULL),
          (4, 2024, 101, 'NJD', 1, 70.0, 0.0, 'WRIST', 0.07, 0, NULL)
    """)


def test_build_shots_per_game_creates_view(tmp_warehouse: Path):
    con = data.connect(tmp_warehouse)
    try:
        _seed(con)
        build_marts.build_shots_per_game(con)
        rows = con.execute(
            "SELECT season, game_id, team, shots, x_goals, goals "
            "FROM mart.shots_per_game ORDER BY game_id, team"
        ).fetchall()
        assert rows == [
            (2024, 100, "BUF", 1, 0.06, 0),
            (2024, 100, "NJD", 2, 0.09, 1),
            (2024, 101, "NJD", 1, 0.07, 0),
        ]
    finally:
        con.close()


def test_build_shots_per_game_is_idempotent(tmp_warehouse: Path):
    con = data.connect(tmp_warehouse)
    try:
        _seed(con)
        build_marts.build_shots_per_game(con)
        build_marts.build_shots_per_game(con)  # rerun
        n = con.execute("SELECT COUNT(*) FROM mart.shots_per_game").fetchone()[0]
        assert n == 3
    finally:
        con.close()
