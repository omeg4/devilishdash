"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_warehouse(tmp_path: Path) -> Path:
    """A path to a per-test temporary warehouse file."""
    return tmp_path / "warehouse.duckdb"
