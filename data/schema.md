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
