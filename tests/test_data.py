from __future__ import annotations

from pathlib import Path

import duckdb

from devilishdash import data


def test_default_warehouse_path_is_repo_data_dir():
    p = data.default_warehouse_path()
    assert p.name == "warehouse.duckdb"
    assert p.parent.name == "data"


def test_connect_creates_file_when_missing(tmp_warehouse: Path):
    assert not tmp_warehouse.exists()
    con = data.connect(tmp_warehouse)
    try:
        assert tmp_warehouse.exists()
        assert isinstance(con, duckdb.DuckDBPyConnection)
    finally:
        con.close()


def test_ensure_schemas_creates_three_schemas(tmp_warehouse: Path):
    con = data.connect(tmp_warehouse)
    try:
        data.ensure_schemas(con)
        rows = con.execute(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name IN ('raw', 'clean', 'mart') ORDER BY schema_name"
        ).fetchall()
        assert [r[0] for r in rows] == ["clean", "mart", "raw"]
    finally:
        con.close()


def test_ensure_schemas_is_idempotent(tmp_warehouse: Path):
    con = data.connect(tmp_warehouse)
    try:
        data.ensure_schemas(con)
        data.ensure_schemas(con)  # should not raise
        rows = con.execute(
            "SELECT COUNT(*) FROM information_schema.schemata "
            "WHERE schema_name IN ('raw', 'clean', 'mart')"
        ).fetchone()
        assert rows[0] == 3
    finally:
        con.close()
