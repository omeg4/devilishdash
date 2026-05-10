from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from devilishdash import data
from data.ingest import moneypuck_shots

SAMPLE_CSV = (
    "shotID,season,game_id,team,shooterPlayerId,xCordAdjusted,yCordAdjusted,"
    "shotType,xGoal,goal\n"
    "1001,2024,2024020001,NJD,8480002,75.0,4.0,WRIST,0.082,0\n"
    "1002,2024,2024020001,NJD,8480002,80.0,-2.0,SLAP,0.041,1\n"
)


def _mock_get(*_args, **_kwargs):
    m = MagicMock()
    m.status_code = 200
    m.iter_content = lambda chunk_size=8192: iter([SAMPLE_CSV.encode()])
    m.raise_for_status = MagicMock()
    return m


def test_download_writes_csv_to_cache(tmp_path: Path):
    cache = tmp_path / "cache"
    with patch.object(moneypuck_shots.requests, "get", side_effect=_mock_get):
        out = moneypuck_shots.download(season=2024, cache_dir=cache)
    assert out.exists()
    assert out.read_text().startswith("shotID,season,game_id")


def test_load_shots_inserts_rows(tmp_warehouse: Path, tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    csv_path = cache / "shots_2024.csv"
    csv_path.write_text(SAMPLE_CSV)

    con = data.connect(tmp_warehouse)
    try:
        data.ensure_schemas(con)
        n = moneypuck_shots.load_shots(con, csv_path=csv_path, season=2024)
        assert n == 2
        rows = con.execute(
            "SELECT shot_id, season, x_goal, goal "
            "FROM raw.moneypuck_shots ORDER BY shot_id"
        ).fetchall()
        assert rows == [(1001, 2024, 0.082, 0), (1002, 2024, 0.041, 1)]
    finally:
        con.close()


def test_load_shots_replaces_existing_season(tmp_warehouse: Path, tmp_path: Path):
    cache = tmp_path / "cache"
    cache.mkdir()
    csv_path = cache / "shots_2024.csv"
    csv_path.write_text(SAMPLE_CSV)

    con = data.connect(tmp_warehouse)
    try:
        data.ensure_schemas(con)
        moneypuck_shots.load_shots(con, csv_path=csv_path, season=2024)
        moneypuck_shots.load_shots(con, csv_path=csv_path, season=2024)
        n = con.execute(
            "SELECT COUNT(*) FROM raw.moneypuck_shots WHERE season = 2024"
        ).fetchone()[0]
        assert n == 2  # season-replace semantics, not append
    finally:
        con.close()
