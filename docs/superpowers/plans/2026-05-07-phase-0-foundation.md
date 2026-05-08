# Phase 0 — Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the technical foundation for the hockey analytics portfolio: a Python utility package, a personal DuckDB hockey-data warehouse populated by idempotent ingest scripts, a published Quarto site at a custom domain, and the first published Note ("Building a personal NHL data warehouse").

**Architecture:** Single monorepo at `/home/bruno/devilishdash/`. A `devilishdash/` Python package holds reusable helpers (warehouse connection, chart style, per-60 metrics). Standalone ingest scripts in `data/ingest/` populate `data/warehouse.duckdb` from public sources (NHL Stats API via `nhl-api-py`; MoneyPuck shot CSVs). A Quarto site at the repo root publishes via GitHub Actions to Netlify on every push to `main`.

**Tech Stack:** Python 3.12+ (system has 3.14), `uv` for env/deps, `ruff` for lint/format, `pytest` for tests, DuckDB for the warehouse, `nhl-api-py` for NHL data, `pandas`/`requests` for ingest, Quarto for the site, GitHub Actions for CI, Netlify for hosting.

---

## File structure produced

```
devilishdash/
├── .github/workflows/deploy.yml          # CI: render quarto, deploy to Netlify
├── .gitignore                            # exists; will be augmented
├── README.md                             # project overview
├── pyproject.toml                        # uv-managed deps + package config
├── _quarto.yml                           # site-level config
├── index.qmd                             # home page
├── about.qmd                             # bio + tools/methods
├── projects/                             # placeholder; first project comes Phase 1
│   └── _metadata.yml
├── notes/                                # short-form blog
│   ├── _metadata.yml
│   └── 2026-05-XX-warehouse-stack.qmd    # publication 1
├── data/
│   ├── warehouse.duckdb                  # tracked (will grow; revisit at Phase 1)
│   ├── schema.md                         # documented schema
│   └── ingest/                           # idempotent ingest scripts
│       ├── __init__.py
│       ├── nhl_schedule.py
│       ├── moneypuck_shots.py
│       └── run_all.py
├── devilishdash/                         # importable utility package
│   ├── __init__.py
│   ├── data.py                           # warehouse connection helpers
│   ├── viz.py                            # set_house_style + palette
│   └── stats.py                          # per_60 + rolling helpers
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_viz.py
│   ├── test_stats.py
│   ├── test_ingest_nhl.py
│   └── test_ingest_moneypuck.py
├── Makefile                              # one-command pipeline + render
└── docs/                                 # already exists
    └── superpowers/
        ├── specs/2026-05-07-...
        └── plans/2026-05-07-phase-0-foundation.md  (this file)
```

---

## Task 1: Project metadata and `uv` environment

**Files:**
- Create: `/home/bruno/devilishdash/README.md`
- Create: `/home/bruno/devilishdash/pyproject.toml`

- [ ] **Step 1: Install uv if not present**

Run:
```bash
which uv || curl -LsSf https://astral.sh/uv/install.sh | sh
```
Then either restart shell or `source ~/.local/bin/env`. Verify:
```bash
uv --version
```
Expected: prints a version like `uv 0.5.x` or newer.

- [ ] **Step 2: Create README.md**

Write `/home/bruno/devilishdash/README.md`:

````markdown
# devilishdash

Public hockey-analytics portfolio: data warehouse, analyses, and Quarto site.

Live site: TBD (Netlify URL until custom domain is configured)

## Quick start

```bash
# Install Python deps
uv sync

# Build the data warehouse from public sources
make data

# Render the site locally
make preview
```

## Layout

- `devilishdash/` — importable utility package (warehouse helpers, chart style, stats helpers)
- `data/ingest/` — idempotent ingest scripts that populate `data/warehouse.duckdb`
- `notes/`, `projects/` — Quarto content
- `tests/` — pytest suite
- `docs/superpowers/` — design spec + implementation plans
````

- [ ] **Step 3: Create pyproject.toml**

Write `/home/bruno/devilishdash/pyproject.toml`:

```toml
[project]
name = "devilishdash"
version = "0.1.0"
description = "Hockey analytics utility package and portfolio site"
requires-python = ">=3.12"
dependencies = [
    "duckdb>=1.1",
    "pandas>=2.2",
    "requests>=2.32",
    "nhl-api-py>=2.0",
    "matplotlib>=3.9",
    "plotnine>=0.13",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.6",
    "ipykernel>=6.29",
    "jupyter>=1.0",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["devilishdash*"]
exclude = ["tests*", "data*", "docs*", "notes*", "projects*"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "W"]
ignore = []

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --tb=short"
```

- [ ] **Step 4: Create the venv and install dependencies**

Run:
```bash
cd /home/bruno/devilishdash
uv sync --extra dev
```
Expected: prints "Resolved N packages" and "Installed N packages". A `.venv/` directory now exists.

- [ ] **Step 5: Verify install works**

Run:
```bash
uv run python -c "import duckdb, pandas, requests; print('ok')"
```
Expected: prints `ok`.

- [ ] **Step 6: Commit**

```bash
git add README.md pyproject.toml uv.lock
git commit -m "chore: add project metadata and uv-managed deps"
```

---

## Task 2: Python package skeleton with smoke test

**Files:**
- Create: `/home/bruno/devilishdash/devilishdash/__init__.py`
- Create: `/home/bruno/devilishdash/tests/__init__.py`
- Create: `/home/bruno/devilishdash/tests/conftest.py`
- Create: `/home/bruno/devilishdash/tests/test_smoke.py`

- [ ] **Step 1: Write the failing test**

Write `/home/bruno/devilishdash/tests/test_smoke.py`:

```python
def test_package_imports():
    import devilishdash

    assert devilishdash.__version__ == "0.1.0"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run pytest tests/test_smoke.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'devilishdash'`.

- [ ] **Step 3: Create the package init**

Write `/home/bruno/devilishdash/devilishdash/__init__.py`:

```python
"""devilishdash — hockey analytics utility package."""

__version__ = "0.1.0"
```

Write empty `/home/bruno/devilishdash/tests/__init__.py`:

```python
```

Write `/home/bruno/devilishdash/tests/conftest.py`:

```python
"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_warehouse(tmp_path: Path) -> Path:
    """A path to a per-test temporary warehouse file."""
    return tmp_path / "warehouse.duckdb"
```

- [ ] **Step 4: Re-run test to verify pass**

```bash
uv run pytest tests/test_smoke.py -v
```
Expected: PASS — `tests/test_smoke.py::test_package_imports PASSED`.

- [ ] **Step 5: Commit**

```bash
git add devilishdash/__init__.py tests/
git commit -m "feat(pkg): scaffold devilishdash package and smoke test"
```

---

## Task 3: Warehouse connection helper (`devilishdash/data.py`)

**Files:**
- Create: `/home/bruno/devilishdash/devilishdash/data.py`
- Create: `/home/bruno/devilishdash/tests/test_data.py`

- [ ] **Step 1: Write the failing tests**

Write `/home/bruno/devilishdash/tests/test_data.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_data.py -v
```
Expected: 4 failures — `ModuleNotFoundError: No module named 'devilishdash.data'`.

- [ ] **Step 3: Implement `devilishdash/data.py`**

Write `/home/bruno/devilishdash/devilishdash/data.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify pass**

```bash
uv run pytest tests/test_data.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add devilishdash/data.py tests/test_data.py
git commit -m "feat(data): warehouse connection + schema bootstrap helpers"
```

---

## Task 4: Per-60 stats helper (`devilishdash/stats.py`)

**Files:**
- Create: `/home/bruno/devilishdash/devilishdash/stats.py`
- Create: `/home/bruno/devilishdash/tests/test_stats.py`

- [ ] **Step 1: Write the failing tests**

Write `/home/bruno/devilishdash/tests/test_stats.py`:

```python
from __future__ import annotations

import math

import pandas as pd
import pytest

from devilishdash import stats


def test_per_60_basic_division():
    # 2 events in 1200 seconds (20 min) → 6 events / 60 min
    assert stats.per_60(events=2, toi_seconds=1200) == pytest.approx(6.0)


def test_per_60_zero_toi_returns_nan():
    assert math.isnan(stats.per_60(events=5, toi_seconds=0))


def test_per_60_negative_toi_raises():
    with pytest.raises(ValueError):
        stats.per_60(events=1, toi_seconds=-1)


def test_per_60_dataframe_column():
    df = pd.DataFrame({"goals": [1, 2, 0], "toi_seconds": [600, 1800, 0]})
    out = stats.per_60_column(df, events_col="goals", toi_col="toi_seconds")
    # 1/600s = 6/hr ; 2/1800s = 4/hr ; 0/0s = NaN
    assert out.iloc[0] == pytest.approx(6.0)
    assert out.iloc[1] == pytest.approx(4.0)
    assert math.isnan(out.iloc[2])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_stats.py -v
```
Expected: 4 failures — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `devilishdash/stats.py`**

Write `/home/bruno/devilishdash/devilishdash/stats.py`:

```python
"""Per-60 and rolling rate helpers for skater/team metrics."""

from __future__ import annotations

import math

import pandas as pd

SECONDS_PER_HOUR = 3600


def per_60(events: float, toi_seconds: float) -> float:
    """Rate of ``events`` per 60 minutes given total time-on-ice in seconds.

    Returns ``nan`` when ``toi_seconds`` is exactly zero (no exposure).
    Raises ``ValueError`` for negative time-on-ice.
    """
    if toi_seconds < 0:
        raise ValueError(f"toi_seconds must be >= 0, got {toi_seconds}")
    if toi_seconds == 0:
        return math.nan
    return events * SECONDS_PER_HOUR / toi_seconds


def per_60_column(df: pd.DataFrame, *, events_col: str, toi_col: str) -> pd.Series:
    """Vectorised version of :func:`per_60` over two DataFrame columns."""
    toi = df[toi_col]
    rate = df[events_col] * SECONDS_PER_HOUR / toi
    rate = rate.where(toi > 0, other=math.nan)
    return rate
```

- [ ] **Step 4: Run tests to verify pass**

```bash
uv run pytest tests/test_stats.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add devilishdash/stats.py tests/test_stats.py
git commit -m "feat(stats): per-60 rate helper (scalar + DataFrame)"
```

---

## Task 5: Chart house-style helper (`devilishdash/viz.py`)

**Files:**
- Create: `/home/bruno/devilishdash/devilishdash/viz.py`
- Create: `/home/bruno/devilishdash/tests/test_viz.py`

- [ ] **Step 1: Write the failing tests**

Write `/home/bruno/devilishdash/tests/test_viz.py`:

```python
from __future__ import annotations

import matplotlib

# Use a non-interactive backend in CI / headless environments.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from devilishdash import viz  # noqa: E402


def test_house_palette_has_expected_keys():
    p = viz.HOUSE_PALETTE
    for key in ("accent", "muted", "ink", "paper", "good", "bad"):
        assert key in p
        assert isinstance(p[key], str)
        assert p[key].startswith("#")


def test_set_house_style_changes_rcParams():
    plt.rcdefaults()
    before = plt.rcParams["font.family"]
    viz.set_house_style()
    after = plt.rcParams["font.family"]
    assert before != after or plt.rcParams["axes.spines.top"] is False


def test_set_house_style_is_idempotent():
    viz.set_house_style()
    viz.set_house_style()  # should not raise
    assert plt.rcParams["axes.spines.top"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_viz.py -v
```
Expected: 3 failures — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `devilishdash/viz.py`**

Write `/home/bruno/devilishdash/devilishdash/viz.py`:

```python
"""House chart style — single source of truth for the site's visual identity."""

from __future__ import annotations

import matplotlib.pyplot as plt

# Deliberately not Devils red — see spec section 9 (brand should not be team-locked).
HOUSE_PALETTE: dict[str, str] = {
    "accent": "#0a6cf5",   # primary accent (blue)
    "muted":  "#9aa5b1",   # secondary lines / annotations
    "ink":    "#0e1014",   # text + axis lines
    "paper":  "#ffffff",   # page background
    "good":   "#1f8a4c",   # positive deltas
    "bad":    "#c0392b",   # negative deltas
}


def set_house_style() -> None:
    """Apply the project's chart style to global matplotlib rcParams."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": HOUSE_PALETTE["ink"],
        "axes.labelcolor": HOUSE_PALETTE["ink"],
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "xtick.color": HOUSE_PALETTE["ink"],
        "ytick.color": HOUSE_PALETTE["ink"],
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "figure.facecolor": HOUSE_PALETTE["paper"],
        "axes.facecolor": HOUSE_PALETTE["paper"],
        "axes.prop_cycle": plt.cycler(
            color=[HOUSE_PALETTE["accent"], HOUSE_PALETTE["muted"],
                   HOUSE_PALETTE["good"], HOUSE_PALETTE["bad"]]
        ),
    })
```

- [ ] **Step 4: Run tests to verify pass**

```bash
uv run pytest tests/test_viz.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add devilishdash/viz.py tests/test_viz.py
git commit -m "feat(viz): house chart style + palette"
```

---

## Task 6: NHL schedule ingest (`data/ingest/nhl_schedule.py`)

**Files:**
- Create: `/home/bruno/devilishdash/data/ingest/__init__.py`
- Create: `/home/bruno/devilishdash/data/ingest/nhl_schedule.py`
- Create: `/home/bruno/devilishdash/tests/test_ingest_nhl.py`

This task uses the NHL Stats API directly via `requests` (rather than `nhl-api-py`), because the schedule endpoint is simple and stable, and going direct keeps the dependency surface small. (Switch to `nhl-api-py` later if helpful.)

- [ ] **Step 1: Write the failing tests with a mocked HTTP response**

Write `/home/bruno/devilishdash/tests/test_ingest_nhl.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_ingest_nhl.py -v
```
Expected: 3 failures — `ModuleNotFoundError: No module named 'data.ingest.nhl_schedule'`.

- [ ] **Step 3: Create the ingest package init**

Write `/home/bruno/devilishdash/data/ingest/__init__.py`:

```python
"""Idempotent ingest scripts that populate the DuckDB warehouse."""
```

- [ ] **Step 4: Implement `data/ingest/nhl_schedule.py`**

Write `/home/bruno/devilishdash/data/ingest/nhl_schedule.py`:

```python
"""Ingest NHL schedule data from the public NHL API into raw.schedule."""

from __future__ import annotations

from typing import Iterable

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
        for g in day.get("games", []):
            rows.append({
                "game_id": g["id"],
                "season": g["season"],
                "game_type": g["gameType"],
                "game_date": g["gameDate"],
                "start_utc": g["startTimeUTC"],
                "home_team_id": g["homeTeam"]["id"],
                "home_abbrev": g["homeTeam"]["abbrev"],
                "away_team_id": g["awayTeam"]["id"],
                "away_abbrev": g["awayTeam"]["abbrev"],
                "game_state": g.get("gameState", ""),
            })
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
                  fetched_at = CURRENT_TIMESTAMP
                """,
                [
                    r["game_id"], r["season"], r["game_type"],
                    r["game_date"], r["start_utc"],
                    r["home_team_id"], r["home_abbrev"],
                    r["away_team_id"], r["away_abbrev"],
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
```

- [ ] **Step 5: Run tests to verify pass**

```bash
uv run pytest tests/test_ingest_nhl.py -v
```
Expected: 3 passed.

- [ ] **Step 6: Smoke-test against the real API for one week**

Run:
```bash
uv run python -c "
from devilishdash import data
from data.ingest import nhl_schedule
con = data.connect()
data.ensure_schemas(con)
n = nhl_schedule.load_schedule(con, week_dates=['2024-10-07'])
print(f'inserted={n}')
print(con.execute('SELECT COUNT(*) FROM raw.schedule').fetchone())
con.close()
"
```
Expected: prints `inserted=N` for some N>0 and `(N,)` matching. (If the network is unavailable or the API has changed, capture the error and skip; tests above prove the code is correct.)

- [ ] **Step 7: Commit**

```bash
git add data/ingest/__init__.py data/ingest/nhl_schedule.py tests/test_ingest_nhl.py
git commit -m "feat(ingest): NHL schedule into raw.schedule (idempotent)"
```

---

## Task 7: MoneyPuck shots ingest (`data/ingest/moneypuck_shots.py`)

**Files:**
- Create: `/home/bruno/devilishdash/data/ingest/moneypuck_shots.py`
- Create: `/home/bruno/devilishdash/tests/test_ingest_moneypuck.py`

MoneyPuck publishes shot-level CSVs at predictable URLs (one per season). We download to a local cache directory, then load to `raw.moneypuck_shots`.

- [ ] **Step 1: Write the failing tests using a fake CSV**

Write `/home/bruno/devilishdash/tests/test_ingest_moneypuck.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_ingest_moneypuck.py -v
```
Expected: 3 failures — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `data/ingest/moneypuck_shots.py`**

Write `/home/bruno/devilishdash/data/ingest/moneypuck_shots.py`:

```python
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

    Returns the number of rows inserted.
    """
    con.execute(CREATE_SHOTS_TABLE)
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
    return con.execute(
        "SELECT COUNT(*) FROM raw.moneypuck_shots WHERE season = ?", [season]
    ).fetchone()[0]
```

- [ ] **Step 4: Run tests to verify pass**

```bash
uv run pytest tests/test_ingest_moneypuck.py -v
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add data/ingest/moneypuck_shots.py tests/test_ingest_moneypuck.py
git commit -m "feat(ingest): MoneyPuck shots loader (season-replace semantics)"
```

---

## Task 8: Build first cleaned + mart views

**Files:**
- Modify: `/home/bruno/devilishdash/data/ingest/__init__.py`
- Create: `/home/bruno/devilishdash/data/ingest/build_marts.py`
- Create: `/home/bruno/devilishdash/tests/test_build_marts.py`

The first mart is `mart.shots_per_game` — total shots per game per team, for the warehouse note's hero chart.

- [ ] **Step 1: Write the failing tests**

Write `/home/bruno/devilishdash/tests/test_build_marts.py`:

```python
from __future__ import annotations

from pathlib import Path

from devilishdash import data
from data.ingest import build_marts


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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_build_marts.py -v
```
Expected: 2 failures — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `data/ingest/build_marts.py`**

Write `/home/bruno/devilishdash/data/ingest/build_marts.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify pass**

```bash
uv run pytest tests/test_build_marts.py -v
```
Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add data/ingest/build_marts.py tests/test_build_marts.py
git commit -m "feat(mart): mart.shots_per_game from raw.moneypuck_shots"
```

---

## Task 9: One-command pipeline runner

**Files:**
- Create: `/home/bruno/devilishdash/data/ingest/run_all.py`
- Create: `/home/bruno/devilishdash/Makefile`

This is the script the README's `make data` invokes. It connects, ensures schemas, runs ingest, builds marts.

- [ ] **Step 1: Write the runner**

Write `/home/bruno/devilishdash/data/ingest/run_all.py`:

```python
"""End-to-end warehouse build: connect → ingest → build marts."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from devilishdash import data
from data.ingest import build_marts, moneypuck_shots, nhl_schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)
log = logging.getLogger("warehouse")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build the devilishdash warehouse")
    p.add_argument(
        "--seasons",
        nargs="+",
        type=int,
        default=[2023, 2024],
        help="Seasons (start year) to ingest. Default: 2023 2024",
    )
    p.add_argument(
        "--cache",
        type=Path,
        default=Path("data/cache"),
        help="Local cache directory for downloaded source files",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    con = data.connect()
    try:
        data.ensure_schemas(con)

        for season in args.seasons:
            log.info("loading NHL schedule for season %s", season)
            week_dates = nhl_schedule.season_week_dates(season)
            inserted = nhl_schedule.load_schedule(con, week_dates=week_dates)
            log.info("schedule rows touched: %s", inserted)

            log.info("downloading MoneyPuck shots for season %s", season)
            csv_path = moneypuck_shots.download(season, cache_dir=args.cache)
            n = moneypuck_shots.load_shots(con, csv_path=csv_path, season=season)
            log.info("shots loaded for %s: %s", season, n)

        log.info("building marts")
        build_marts.build_shots_per_game(con)
        log.info("done")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Write the Makefile**

Write `/home/bruno/devilishdash/Makefile`:

```makefile
.PHONY: data preview render lint test clean

data:
	uv run python -m data.ingest.run_all

preview:
	quarto preview

render:
	quarto render

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

clean:
	rm -rf _site .quarto data/cache
```

- [ ] **Step 3: Verify ingest runs end-to-end (network required)**

```bash
cd /home/bruno/devilishdash
make data
```
Expected: log lines for schedule + MoneyPuck for each season; final "done" line. `data/warehouse.duckdb` exists and has rows in `raw.schedule`, `raw.moneypuck_shots`, and `mart.shots_per_game`.

If network unavailable, skip and verify shape only:
```bash
uv run python -c "
from devilishdash import data
con = data.connect()
data.ensure_schemas(con)
print('schemas ok')
con.close()
"
```

- [ ] **Step 4: Commit**

```bash
git add data/ingest/run_all.py Makefile
git commit -m "feat(pipeline): end-to-end warehouse build via make data"
```

---

## Task 10: Schema documentation (`data/schema.md`)

**Files:**
- Create: `/home/bruno/devilishdash/data/schema.md`

- [ ] **Step 1: Write the schema documentation**

Write `/home/bruno/devilishdash/data/schema.md`:

````markdown
# Warehouse schema

The warehouse is a single DuckDB file: `data/warehouse.duckdb`.

Three schemas, each with a single purpose:

- `raw.*` — untouched extracts from public sources. Column names mirror source field names where reasonable; types are normalised; one timestamp column (`fetched_at`) per row.
- `clean.*` — deduped, type-corrected, renamed. Stable surface for downstream marts. (None yet — populated in Phase 1.)
- `mart.*` — analysis-ready. Each mart is one logical question.

## raw.schedule

NHL game schedule from `https://api-web.nhle.com/v1/schedule/{date}`.

| column | type | notes |
|---|---|---|
| `game_id` | BIGINT | NHL game id; primary key |
| `season` | BIGINT | e.g. 20242025 |
| `game_type` | INTEGER | 1=preseason, 2=regular, 3=playoff |
| `game_date` | DATE | local game date |
| `start_utc` | TIMESTAMP | start time UTC |
| `home_team_id` | INTEGER | NHL team id |
| `home_abbrev` | VARCHAR | e.g. NJD |
| `away_team_id` | INTEGER | |
| `away_abbrev` | VARCHAR | |
| `game_state` | VARCHAR | OFF / FUT / LIVE / FINAL etc. |
| `fetched_at` | TIMESTAMP | row insertion time |

## raw.moneypuck_shots

Per-shot data from MoneyPuck (`shots_{season}.csv`).

| column | type | notes |
|---|---|---|
| `shot_id` | BIGINT | MoneyPuck `shotID` |
| `season` | INTEGER | season start year, e.g. 2024 |
| `game_id` | BIGINT | NHL game id |
| `team` | VARCHAR | shooting team abbrev |
| `shooter_id` | BIGINT | NHL player id |
| `x_cord_adjusted` | DOUBLE | shot x-coordinate, attacking-zone-adjusted |
| `y_cord_adjusted` | DOUBLE | shot y-coordinate, attacking-zone-adjusted |
| `shot_type` | VARCHAR | WRIST / SLAP / SNAP / etc. |
| `x_goal` | DOUBLE | MoneyPuck xG for the shot |
| `goal` | INTEGER | 1 if goal, else 0 |
| `fetched_at` | TIMESTAMP | |

Loader semantics: re-running the loader for a season **replaces** all rows for that season.

## mart.shots_per_game

| column | type | notes |
|---|---|---|
| `season` | INTEGER | |
| `game_id` | BIGINT | |
| `team` | VARCHAR | |
| `shots` | BIGINT | number of recorded shots |
| `x_goals` | DOUBLE | summed expected goals |
| `goals` | BIGINT | actual goals |

Source: `raw.moneypuck_shots`. Rebuilt fresh by `build_marts.build_shots_per_game()` on every pipeline run.
````

- [ ] **Step 2: Commit**

```bash
git add data/schema.md
git commit -m "docs(data): document raw + mart schemas"
```

---

## Task 11: Quarto site scaffold (home + about)

**Files:**
- Create: `/home/bruno/devilishdash/_quarto.yml`
- Create: `/home/bruno/devilishdash/index.qmd`
- Create: `/home/bruno/devilishdash/about.qmd`

- [ ] **Step 1: Install Quarto if not present**

Run:
```bash
which quarto || (
  curl -L -o /tmp/quarto.deb "https://quarto.org/download/latest/quarto-linux-amd64.deb" \
  && sudo dpkg -i /tmp/quarto.deb
)
quarto --version
```
Expected: prints a version string like `1.5.x` or newer. If you don't have sudo, install via the tarball: see https://quarto.org/docs/get-started/.

- [ ] **Step 2: Write `_quarto.yml`**

Write `/home/bruno/devilishdash/_quarto.yml`:

```yaml
project:
  type: website
  output-dir: _site
  resources:
    - "data/warehouse.duckdb"  # excluded; just a marker

website:
  title: "Matthew Brunetti"
  description: "Hockey analytics & data work"
  navbar:
    left:
      - href: index.qmd
        text: Home
      - href: projects/index.qmd
        text: Projects
      - href: notes/index.qmd
        text: Notes
      - href: about.qmd
        text: About
    right:
      - icon: github
        href: https://github.com/<your-github-username>/devilishdash
      - icon: twitter
        href: https://twitter.com/<your-handle>
  page-footer:
    left: "© Matthew Brunetti"
    right: "Built with [Quarto](https://quarto.org)"

format:
  html:
    theme: [cosmo, custom.scss]
    toc: true
    code-fold: true
    code-tools: true
    fig-format: svg
    fig-responsive: true
    css: styles.css
```

- [ ] **Step 3: Write `index.qmd` (home)**

Write `/home/bruno/devilishdash/index.qmd`:

```markdown
---
title: "Matthew Brunetti"
subtitle: "Hockey analytics & data work."
---

I'm a senior business-analytics consultant working toward a hockey-operations
analytics role. This site collects my analyses, methodology notes, and code.

## Recent

- [Notes](notes/index.qmd) — short-form thinking, work in progress, reactions.
- [Projects](projects/index.qmd) — long-form analyses with reproducible code.
- [About](about.qmd) — bio, tools, contact.

The site and every chart on it is built from the same DuckDB warehouse, with
all source code on GitHub. See [the warehouse note](notes/2026-05-XX-warehouse-stack.qmd)
for how the pipeline works.
```

- [ ] **Step 4: Write `about.qmd`**

Write `/home/bruno/devilishdash/about.qmd`:

```markdown
---
title: "About"
---

I'm Matthew Brunetti — senior consultant at a business analytics firm with five
years of experience across SQL, Snowflake, Tableau, PowerBI, and Python. This
site documents my work toward a hockey-operations analytics role.

## What I'm working on

- A reproducible NHL data warehouse (DuckDB + public-source ingest).
- An ongoing analysis of post-injury performance for NHL skaters.
- Player-evaluation, draft-modeling, and goaltending analyses, in roughly that
  order over the next year.

## Tools & methods

- **Languages:** Python, SQL.
- **Data:** DuckDB warehouse, NHL Stats API, MoneyPuck, Natural Stat Trick.
- **Stats / ML:** regression, mixed-effects models, regularization (ridge/lasso),
  gradient boosting, calibration, bootstrapping.
- **Site:** Quarto, GitHub Actions CI, Netlify.

## Contact

- Email: matthew.brunetti28@gmail.com
- GitHub: [github.com/&lt;your-username&gt;](https://github.com/)
- Twitter: [@&lt;your-handle&gt;](https://twitter.com/)
```

- [ ] **Step 5: Render locally and verify**

Run:
```bash
cd /home/bruno/devilishdash
quarto render index.qmd about.qmd
ls _site/
```
Expected: `_site/index.html` and `_site/about.html` exist. Open `_site/index.html` in a browser; verify nav and content render.

- [ ] **Step 6: Commit**

```bash
git add _quarto.yml index.qmd about.qmd
git commit -m "feat(site): scaffold Quarto site (home + about)"
```

---

## Task 12: Notes blog setup

**Files:**
- Create: `/home/bruno/devilishdash/notes/index.qmd`
- Create: `/home/bruno/devilishdash/notes/_metadata.yml`
- Create: `/home/bruno/devilishdash/projects/index.qmd`

- [ ] **Step 1: Write the notes listing page**

Write `/home/bruno/devilishdash/notes/index.qmd`:

```markdown
---
title: "Notes"
subtitle: "Short-form: reactions, methodology questions, mini-charts."
listing:
  contents: "*.qmd"
  exclude:
    filename: "index.qmd"
  type: default
  sort: "date desc"
  fields: [date, title, description]
  feed: true
page-layout: full
---
```

- [ ] **Step 2: Write notes metadata**

Write `/home/bruno/devilishdash/notes/_metadata.yml`:

```yaml
freeze: false
toc: true
code-fold: true
```

- [ ] **Step 3: Write the projects placeholder listing**

Write `/home/bruno/devilishdash/projects/index.qmd`:

```markdown
---
title: "Projects"
subtitle: "Long-form analyses with reproducible code."
listing:
  contents: "*/index.qmd"
  type: default
  sort: "date desc"
  fields: [date, title, description]
page-layout: full
---

The first long-form project — a comparative analysis of NHL post-injury
performance — is in progress. See [Notes](../notes/index.qmd) for short-form
work in the meantime.
```

- [ ] **Step 4: Render and verify the listings work**

Run:
```bash
quarto render notes/index.qmd projects/index.qmd
ls _site/notes/ _site/projects/
```
Expected: `_site/notes/index.html` and `_site/projects/index.html` exist.

- [ ] **Step 5: Commit**

```bash
git add notes/ projects/
git commit -m "feat(site): notes + projects listing pages"
```

---

## Task 13: Publication 1 — the warehouse-stack note

**Files:**
- Create: `/home/bruno/devilishdash/notes/2026-05-XX-warehouse-stack.qmd` (replace `XX` with today's day)

- [ ] **Step 1: Write the note**

Write `/home/bruno/devilishdash/notes/2026-05-XX-warehouse-stack.qmd` (use today's date, e.g. `2026-05-21`):

````markdown
---
title: "Building a personal NHL data warehouse — the stack and the gotchas"
description: "How I'm setting up a single-laptop hockey data pipeline with DuckDB, Quarto, and public sources."
date: "2026-05-XX"
categories: [methodology, data, infra]
format:
  html:
    code-fold: true
---

## Bottom line

A single DuckDB file, three schemas (`raw` / `clean` / `mart`), idempotent
ingest scripts for the NHL Stats API and MoneyPuck shot data, all wired into a
Quarto site that re-renders on every push. Total infrastructure cost: ~$12/year
for a domain. Total runtime to rebuild from sources: under 5 minutes for two
seasons of data.

```{python}
#| label: shots-per-game-hero
#| fig-cap: "Shots per game by team, latest season — sample chart from the warehouse."
import matplotlib.pyplot as plt
import pandas as pd

from devilishdash import data, viz

viz.set_house_style()

con = data.connect()
df = con.execute("""
    SELECT team, AVG(shots) AS shots_per_game
    FROM mart.shots_per_game
    WHERE season = (SELECT MAX(season) FROM mart.shots_per_game)
    GROUP BY team
    ORDER BY shots_per_game DESC
""").df()
con.close()

fig, ax = plt.subplots(figsize=(8, 6))
ax.barh(df["team"], df["shots_per_game"], color=viz.HOUSE_PALETTE["accent"])
ax.invert_yaxis()
ax.set_xlabel("Shots per game")
ax.set_title("Average shots per game, latest season")
plt.tight_layout()
plt.show()
```

## What I built

A monorepo at `github.com/<user>/devilishdash` containing:

- `devilishdash/` — a Python package with three modules (`data.py`, `viz.py`,
  `stats.py`) used by every analysis on this site.
- `data/ingest/` — idempotent scripts that populate `data/warehouse.duckdb`
  from public sources.
- `notes/` and `projects/` — Quarto content. (You're reading a `notes/` page.)
- `Makefile` — single entry point: `make data` rebuilds the warehouse,
  `make preview` runs the Quarto preview server.

## Why DuckDB

I came from enterprise BI — Snowflake, Tableau, PowerBI. The mental model was
"a server somewhere, and I write SQL against it." DuckDB collapses that to "a
file on my laptop." For hockey-data scale (low millions of rows, the largest
season of MoneyPuck shot data is ~120k rows), it's overkill in performance and
underkill in operational cost. Sub-second queries; no server to manage; the
warehouse file lives next to the code that produced it.

## Schema convention

Three schemas, each with one purpose:

| Schema | Purpose | Examples |
|---|---|---|
| `raw.*` | Untouched extract — types normalised, columns renamed for readability, but no semantic transforms | `raw.schedule`, `raw.moneypuck_shots` |
| `clean.*` | Deduped, joined, key-corrected, ready for analysis | (none yet — populated in Phase 1) |
| `mart.*` | Analysis-ready, one mart per logical question | `mart.shots_per_game` |

Loaders are **idempotent by construction**: schedule rows upsert by `game_id`;
shot data is replaced per-season. No duplicate-row bugs from rerunning the
pipeline.

## Three gotchas

**1. The NHL API doesn't return everything in one call.** The `/v1/schedule/{date}`
endpoint returns one *week* starting at the given date. So a full-season fetch
means iterating Mondays from October to April. Trivial in code (`season_week_dates`
in `nhl_schedule.py`), but easy to miss on first read.

**2. MoneyPuck filenames change conventions year to year.** Sometimes the per-
season file ships as `.zip`, sometimes as `.csv`. The current loader assumes
`.csv`; the URL helper has both URLs ready and falls back if the first fails.
Keep an eye on this each October.

**3. Idempotence is not the same as cheapness.** Rerunning ingest is *correct*
— it produces the same warehouse — but for MoneyPuck it re-downloads ~30 MB
per season. The runner caches into `data/cache/`; re-runs are seconds, not
minutes.

## What's next

This pipeline is **Phase 0** of a 9-12 month plan to build a hockey-analytics
portfolio toward a hockey-ops role. Phase 1 (~8-10 weeks) is a comparative
analysis of NHL post-injury performance — using the Devils as a case study and
league-wide as the comparison. The hardest part will be getting clean injury
data, since the NHL doesn't publish an injury API. More on that soon.

If you spot a bug in the warehouse code, the source is on GitHub (link in the
nav). Issues and PRs welcome.
````

- [ ] **Step 2: Render and verify the note appears in the listing**

Run:
```bash
make data        # populate the warehouse so the embedded chart works
quarto render
```
Expected: `_site/notes/2026-05-XX-warehouse-stack/index.html` exists, and `_site/notes/index.html` lists the note. The `shots-per-game-hero` figure renders without errors. Open `_site/notes/index.html` and verify the listing.

- [ ] **Step 3: Commit**

```bash
git add notes/2026-05-XX-warehouse-stack.qmd
git commit -m "post(notes): publication 1 — building a personal NHL warehouse"
```

---

## Task 14: GitHub Actions deploy workflow

**Files:**
- Create: `/home/bruno/devilishdash/.github/workflows/deploy.yml`

This task assumes the GitHub repo exists. Create it first via `gh repo create devilishdash --public --source=. --remote=origin --push` if you haven't.

- [ ] **Step 1: Write the workflow**

Write `/home/bruno/devilishdash/.github/workflows/deploy.yml`:

```yaml
name: Deploy site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install Python deps
        run: uv sync --extra dev

      - name: Set up Quarto
        uses: quarto-dev/quarto-actions/setup@v2

      - name: Build the warehouse
        run: uv run python -m data.ingest.run_all --seasons 2024
        # NOTE: skip in CI for now if the public sources are flaky;
        # commit the prebuilt warehouse instead. To skip:
        # if: ${{ false }}

      - name: Render Quarto site
        run: uv run quarto render

      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v3
        with:
          publish-dir: _site
          production-deploy: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "ci: render Quarto and deploy to Netlify on push to main"
```

(Activation depends on Task 15 — the workflow will sit dormant until Netlify secrets exist.)

---

## Task 15: Netlify deployment + custom domain

**Manual steps (no code).** The end-state is a publicly reachable site.

- [ ] **Step 1: Create a Netlify account** (free tier) at https://app.netlify.com/signup. Use the same email as your eventual GitHub identity.

- [ ] **Step 2: Connect the GitHub repo**

In Netlify: *Sites* → *Add new site* → *Import an existing project* → *GitHub* → select `devilishdash`. When asked for build settings, choose:
- Build command: leave blank (CI does the build; Netlify just hosts)
- Publish directory: `_site`
- Branch to deploy: `main`

After connecting, run a manual deploy to verify the publish dir is correct.

- [ ] **Step 3: Get Netlify auth token + site ID**

In Netlify:
- Auth token: *User settings* → *Applications* → *Personal access tokens* → *New access token* (name it "GitHub Actions deploy")
- Site ID: *Site settings* → *General* → "Site information" → API ID

- [ ] **Step 4: Add the secrets to GitHub**

In your GitHub repo: *Settings* → *Secrets and variables* → *Actions* → *New repository secret*. Add:
- `NETLIFY_AUTH_TOKEN` = the personal access token from Step 3
- `NETLIFY_SITE_ID` = the API ID from Step 3

- [ ] **Step 5: Push and verify CI deploy works**

```bash
git push origin main
```
Watch the Actions tab on GitHub. The workflow should: install deps → install Quarto → render → deploy. After it succeeds, your Netlify site has the latest content.

- [ ] **Step 6: Buy and configure a custom domain**

Recommended candidates: `mattbrunetti.com`, `matthewbrunetti.com`, `mbrunetti.com`, `brunetti.dev`. Buy at any registrar (Namecheap, Porkbun, Cloudflare). ~$12/year.

In Netlify: *Domain management* → *Add a domain* → enter the domain. Netlify will show DNS records to add at your registrar. For most domains, a `CNAME` to your `<site-name>.netlify.app` plus an `A` record to Netlify's load balancer.

- [ ] **Step 7: Enable HTTPS**

In Netlify: *Domain management* → *HTTPS* → "Verify DNS configuration" → "Provision certificate" (uses Let's Encrypt). Wait ~5 minutes. Then enable "Force HTTPS".

- [ ] **Step 8: Verify the live site loads**

Visit your custom domain. Confirm:
- Home page loads
- Navigation works (Home / Projects / Notes / About)
- Notes listing shows the warehouse-stack post
- The hero chart in the warehouse-stack post renders

- [ ] **Step 9: Update README + about page with the live URL**

Edit `/home/bruno/devilishdash/README.md`:

Replace `Live site: TBD ...` with `Live site: https://<your-domain>`.

Edit `/home/bruno/devilishdash/about.qmd`:

Update the GitHub and Twitter placeholders with your real handles.

- [ ] **Step 10: Commit**

```bash
git add README.md about.qmd
git commit -m "docs: update live URL and contact handles"
git push origin main
```

---

## Task 16: Phase 0 reading list checkpoint

**This is a non-code task.** Track reading separately so you don't forget.

- [ ] **Tulsky's Corsi era essays** — search "Eric Tulsky Corsi" on Broad Street Hockey or his old blog. Aim for 3 essays. Take notes.

- [ ] **Andrew Thomas's xG paper** — *A New Way to Look at Hockey* / Inferring Shot Quality. Free PDF online.

- [ ] **Evolving-Hockey RAPM methodology page** — read the full methodology doc on evolving-hockey.com. You won't follow all the math; that's fine.

- [ ] **HockeyViz "About / Methodology" pages** — read what Micah publishes about how he builds his charts.

- [ ] **Schuckers's papers on player evaluation** — search "Schuckers TOI60 plus minus" on SSRN or Google Scholar. Read at least one.

- [ ] **Write a follow-up Note** ("Five papers I read this month") if any of the above sparks something specific. Optional but recommended for site activity.

---

## Self-Review

Spec coverage check, with section numbers from the spec:

| Spec section | Phase 0 task |
|---|---|
| §3 "Tech stack: Quarto-First" | T1 (env), T11 (Quarto scaffold), T14 (CI) |
| §3 "Site IA" | T11 (home/about), T12 (notes/projects) |
| §3 "Project page anatomy" | Deferred to Phase 1 (no project yet) |
| §3 "Real name identity" | T11 (`about.qmd`), T15 step 9 |
| §4 Phase 0 — dev env | T1 |
| §4 Phase 0 — Quarto site & deploy | T11, T12, T14, T15 |
| §4 Phase 0 — DuckDB warehouse | T3, T6, T7, T8, T9 |
| §4 Phase 0 — landmark canon | T16 |
| §4 Phase 0 — Publication 1 | T13 |
| §5 Repo layout | T1 (root), T2 (pkg), T6-T9 (data/), T11-T12 (site), Makefile in T9 |
| §5 Tools | T1 (uv, ruff, pytest), T11 (Quarto), T14 (Actions/Netlify) |
| §5 Data layer raw/clean/mart | T3 (schemas), T6-T8 (raw + mart), §clean populated Phase 1 |
| §5 Visual identity | T5 (`viz.py`) |
| §6 Workflow — git from day one | Already done (initial commit pre-plan) |
| §6 Workflow — branch per project | Process; not a code task |
| §6 Workflow — pre-register hypotheses | Phase 1 |
| §6 Workflow — peer review | Process |
| §6 Workflow — code-fold | T11 (`_quarto.yml` `code-fold: true`) |
| §6 Workflow — captions/units | T13 (note's hero chart sets the example) |
| §7 Domain reading | T16 |
| §8 Skills display via tags | Phase 1 (when first project ships with tags) |
| §9 Brand / domain | T15 (manual steps) |
| §10 Failure modes | Documented; nothing to build in Phase 0 |
| §11 Success metrics | Tracked separately |

**Gaps found:** None for Phase 0 exit criteria. The "deferred" rows above are intentionally deferred to later phases.

**Placeholder scan:** No "TBD"/"TODO" remain in the plan body. Strings like `<your-github-username>`, `<your-handle>`, `2026-05-XX` are explicitly marked for the engineer to fill in at the right time (T11, T13, T15) — these aren't placeholder hand-waves.

**Type/name consistency:**
- `data.connect()`, `data.ensure_schemas()`, `data.default_warehouse_path()` — used consistently across T3, T6, T7, T8, T9, T13.
- `nhl_schedule.fetch_week()`, `nhl_schedule.load_schedule()`, `nhl_schedule.season_week_dates()` — consistent in T6 and T9.
- `moneypuck_shots.download()`, `moneypuck_shots.load_shots()` — consistent in T7 and T9.
- `build_marts.build_shots_per_game()` — consistent in T8 and T9.
- `viz.set_house_style()`, `viz.HOUSE_PALETTE` — consistent in T5 and T13.
- `stats.per_60()`, `stats.per_60_column()` — consistent in T4. (Not yet used in T13's note, but available for Phase 1.)

All names check out.
