from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from devilishdash import data
from data.ingest import nhl_schedule

SAMPLE_API_RESPONSE = {
    "gameWeek": [
        {
            "date": "2024-10-08",
            "games": [
                {
                    "id": 2024020001,
                    "season": 20242025,
                    "gameType": 2,
                    "gameDate": "2024-10-08",
                    "startTimeUTC": "2024-10-09T00:00:00Z",
                    "homeTeam": {"id": 1, "abbrev": "NJD"},
                    "awayTeam": {"id": 2, "abbrev": "BUF"},
                    "gameState": "OFF",
                }
            ],
        }
    ]
}


def _mock_get(*_args, **_kwargs):
    m = MagicMock()
    m.status_code = 200
    m.json.return_value = SAMPLE_API_RESPONSE
    m.raise_for_status = MagicMock()
    return m


def test_fetch_week_returns_normalised_rows():
    with patch.object(nhl_schedule.requests, "get", side_effect=_mock_get):
        rows = nhl_schedule.fetch_week("2024-10-07")
    assert len(rows) == 1
    r = rows[0]
    assert r["game_id"] == 2024020001
    assert r["season"] == 20242025
    assert r["home_abbrev"] == "NJD"
    assert r["away_abbrev"] == "BUF"


def test_load_schedule_writes_to_raw_schema(tmp_warehouse: Path):
    con = data.connect(tmp_warehouse)
    try:
        data.ensure_schemas(con)
        with patch.object(nhl_schedule.requests, "get", side_effect=_mock_get):
            inserted = nhl_schedule.load_schedule(
                con, week_dates=["2024-10-07"]
            )
        assert inserted == 1
        result = con.execute(
            "SELECT game_id, home_abbrev FROM raw.schedule"
        ).fetchall()
        assert result == [(2024020001, "NJD")]
    finally:
        con.close()


def test_load_schedule_is_idempotent(tmp_warehouse: Path):
    con = data.connect(tmp_warehouse)
    try:
        data.ensure_schemas(con)
        with patch.object(nhl_schedule.requests, "get", side_effect=_mock_get):
            nhl_schedule.load_schedule(con, week_dates=["2024-10-07"])
            nhl_schedule.load_schedule(con, week_dates=["2024-10-07"])
        count = con.execute("SELECT COUNT(*) FROM raw.schedule").fetchone()[0]
        assert count == 1  # not 2 — idempotent on game_id
    finally:
        con.close()
