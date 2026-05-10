"""Ingest NHL schedule data from the public NHL API into raw.schedule."""

from __future__ import annotations

from collections.abc import Iterable

import duckdb
import requests

NHL_WEEK_URL = "https://api-web.nhle.com/v1/schedule/{date}"
TIMEOUT = 30

CREATE_SCHEDULE_TABLE = """
CREATE TABLE IF NOT EXISTS raw.schedule (
    game_id      BIGINT PRIMARY KEY,
    season       BIGINT,
    game_type    INTEGER,
    game_date    DATE,
    start_utc    TIMESTAMP,
    home_team_id INTEGER,
    home_abbrev  VARCHAR,
    away_team_id INTEGER,
    away_abbrev  VARCHAR,
    game_state   VARCHAR,
    fetched_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def fetch_week(date: str) -> list[dict]:
    """Fetch one week starting at ``date`` (YYYY-MM-DD) and return flat rows."""
    resp = requests.get(NHL_WEEK_URL.format(date=date), timeout=TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    rows: list[dict] = []
    for day in payload.get("gameWeek", []):
        day_date = day.get("date", "")
        for g in day.get("games", []):
            rows.append(
                {
                    "game_id": g["id"],
                    "season": g["season"],
                    "game_type": g["gameType"],
                    # Real API puts the date on the day object, not the game object.
                    # Fall back to the day-level date for compatibility.
                    "game_date": g.get("gameDate", day_date),
                    "start_utc": g["startTimeUTC"],
                    "home_team_id": g["homeTeam"]["id"],
                    "home_abbrev": g["homeTeam"]["abbrev"],
                    "away_team_id": g["awayTeam"]["id"],
                    "away_abbrev": g["awayTeam"]["abbrev"],
                    "game_state": g.get("gameState", ""),
                }
            )
    return rows


def load_schedule(
    con: duckdb.DuckDBPyConnection,
    *,
    week_dates: Iterable[str],
) -> int:
    """Insert (or upsert by game_id) schedule rows for each week start date."""
    con.execute(CREATE_SCHEDULE_TABLE)
    inserted = 0
    for d in week_dates:
        rows = fetch_week(d)
        for r in rows:
            con.execute(
                """
                INSERT INTO raw.schedule
                  (game_id, season, game_type, game_date, start_utc,
                   home_team_id, home_abbrev, away_team_id, away_abbrev,
                   game_state)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (game_id) DO UPDATE SET
                  game_state = excluded.game_state,
                  start_utc  = excluded.start_utc,
                  fetched_at = now()
                """,
                [
                    r["game_id"],
                    r["season"],
                    r["game_type"],
                    r["game_date"],
                    r["start_utc"],
                    r["home_team_id"],
                    r["home_abbrev"],
                    r["away_team_id"],
                    r["away_abbrev"],
                    r["game_state"],
                ],
            )
            inserted += 1
    return inserted


def season_week_dates(season_start_year: int) -> list[str]:
    """Return Mondays from early October through end-of-April for a season."""
    from datetime import date, timedelta

    start = date(season_start_year, 10, 1)
    # Snap to the first Monday on or after Oct 1.
    start += timedelta(days=(7 - start.weekday()) % 7)
    end = date(season_start_year + 1, 4, 30)
    out = []
    cur = start
    while cur <= end:
        out.append(cur.isoformat())
        cur += timedelta(days=7)
    return out
