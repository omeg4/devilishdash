"""Download and load MoneyPuck per-season shot CSVs into raw.moneypuck_shots."""

from __future__ import annotations

from pathlib import Path

import duckdb
import requests

MONEYPUCK_SHOT_URL = (
    "https://peter-tanner.com/moneypuck/downloads/shots_{season}.zip"
)
# Alternate non-zipped CSV URL (for newer years MoneyPuck has shipped both):
MONEYPUCK_SHOT_CSV_URL = (
    "https://peter-tanner.com/moneypuck/downloads/shots_{season}.csv"
)
TIMEOUT = 60

CREATE_SHOTS_TABLE = """
CREATE TABLE IF NOT EXISTS raw.moneypuck_shots (
    shot_id          BIGINT,
    season           INTEGER,
    game_id          BIGINT,
    team             VARCHAR,
    shooter_id       BIGINT,
    x_cord_adjusted  DOUBLE,
    y_cord_adjusted  DOUBLE,
    shot_type        VARCHAR,
    x_goal           DOUBLE,
    goal             INTEGER,
    fetched_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def download(season: int, cache_dir: Path) -> Path:
    """Download the MoneyPuck shots CSV for ``season`` to ``cache_dir``."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"shots_{season}.csv"

    url = MONEYPUCK_SHOT_CSV_URL.format(season=season)
    resp = requests.get(url, stream=True, timeout=TIMEOUT)
    resp.raise_for_status()
    with out.open("wb") as fh:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                fh.write(chunk)
    return out


def load_shots(
    con: duckdb.DuckDBPyConnection,
    *,
    csv_path: Path,
    season: int,
) -> int:
    """Replace all rows for ``season`` in raw.moneypuck_shots from ``csv_path``.

    DELETE + INSERT run inside a single transaction so a load failure cannot
    leave the warehouse with a hollowed-out season.

    Returns the number of rows present for ``season`` after the load.
    """
    con.execute(CREATE_SHOTS_TABLE)
    con.execute("BEGIN")
    try:
        con.execute("DELETE FROM raw.moneypuck_shots WHERE season = ?", [season])
        con.execute(
            f"""
            INSERT INTO raw.moneypuck_shots
              (shot_id, season, game_id, team, shooter_id,
               x_cord_adjusted, y_cord_adjusted, shot_type, x_goal, goal)
            SELECT
              shotID, season, game_id, team, shooterPlayerId,
              xCordAdjusted, yCordAdjusted, shotType, xGoal, goal
            FROM read_csv('{csv_path.as_posix()}', header=true)
            """
        )
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    return con.execute(
        "SELECT COUNT(*) FROM raw.moneypuck_shots WHERE season = ?", [season]
    ).fetchone()[0]
