"""Personal DuckDB warehouse helpers."""

from __future__ import annotations

from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WAREHOUSE = REPO_ROOT / "data" / "warehouse.duckdb"
SCHEMAS = ("raw", "clean", "mart")


def default_warehouse_path() -> Path:
    """Return the canonical path to the project's DuckDB file."""
    return DEFAULT_WAREHOUSE


def connect(path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """Open (and create-if-missing) the DuckDB warehouse at ``path``."""
    target = Path(path) if path is not None else DEFAULT_WAREHOUSE
    target.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(target))


def ensure_schemas(con: duckdb.DuckDBPyConnection) -> None:
    """Create the raw / clean / mart schemas if they don't exist."""
    for schema in SCHEMAS:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
