# Phase 1 — Devils Injury-Recovery Study Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **Read `docs/superpowers/research/2026-05-19-phase-1-injury-data-scouting.md` before starting** — it grounds the methodology pivot this plan operationalizes.

**Goal:** Publish a methodology-rigorous analysis of whether New Jersey Devils skaters underperform after extended absences relative to a league-wide baseline. Output: one long-form Quarto project page at `projects/devils-injury-study/`, a reproducible warehouse pipeline backing it, and a forward-looking HR injury snapshot accumulator that seeds Phase 2+ datasets.

**Methodology pivot (decided 2026-05-19):** No public source preserves resolved historical injuries as a queryable ledger. Phase 1 uses an **extended-absence proxy** derived from NHL API game logs (player on roster, missed ≥N consecutive games while team played) as the historical injury signal, cross-validated against `lwadya/nhl_injuries` season-aggregate TSN labels. In parallel, daily snapshots of Hockey Reference's `/friv/injuries.cgi` build a real forward-looking injury ledger for future seasons. Full rationale: `docs/superpowers/research/2026-05-19-phase-1-injury-data-scouting.md`.

**Architecture:** Build on Phase 0's monorepo. New ingest scripts in `data/ingest/` populate new raw/clean/mart tables in `data/warehouse.duckdb`. New helpers in `devilishdash.stats` cover windowed metrics, matched controls, and bootstrap CIs. A new mixed-effects modeling module `devilishdash/models.py` wraps statsmodels. The publication lives at `projects/devils-injury-study/index.qmd`. Forward-snapshot infrastructure runs as a separate GitHub Actions cron workflow.

**Tech additions on top of Phase 0:**
- `statsmodels>=0.14` (mixed-effects regression)
- `scipy>=1.13` (bootstrap, statistical utilities)
- Possibly `pymer4` (only if statsmodels' MixedLM proves limiting — defer the decision)

**Timeline target:** 8-10 weeks total. Stage A (data) capped at 3 weeks per the spec's data-gathering cap. Methodology-pivot reduces that cap risk substantially vs. the original triangulation plan.

---

## File structure produced (additions to existing repo)

```
devilishdash/
├── data/
│   ├── ingest/
│   │   ├── nhl_player_game_log.py       # T2: per-player game log loader
│   │   ├── lwadya_injuries.py           # T5: GitHub CSV ingest for cross-validation
│   │   └── hr_injury_snapshot.py        # T14: daily HR injury page snapshot+parse
│   ├── snapshots/
│   │   └── hr_injuries/                 # T14: raw daily HTML, gitignored
│   └── schema.md                        # T4: extend with new tables
├── devilishdash/
│   ├── stats.py                         # T6: extend with window_metrics, bootstrap_ci
│   ├── models.py                        # T8: new — mixed-effects wrapper
│   └── absence.py                       # T3, T4: new — absence-episode derivation logic
├── tests/
│   ├── test_ingest_player_game_log.py   # T2
│   ├── test_absence.py                  # T3, T4
│   ├── test_ingest_lwadya.py            # T5
│   ├── test_stats_window.py             # T6 (extend existing test_stats.py)
│   ├── test_models.py                   # T8
│   └── test_ingest_hr_snapshot.py       # T14
├── projects/
│   └── devils-injury-study/
│       ├── _metadata.yml                # T10
│       ├── index.qmd                    # T10–T13: methodology, results, viz, limitations
│       └── figures/                     # T12: generated plots, gitignored if produced at render time
├── .github/workflows/
│   └── hr-injury-snapshot.yml           # T14: daily cron action
└── docs/superpowers/
    └── plans/2026-05-19-phase-1-injury-recovery.md   # (this file)
```

---

## Stage A — Data layer (W1-3, 3-week cap)

Goal: a queryable mart of absence episodes for all NHL skaters across 4 seasons (2022-23, 2023-24, 2024-25, 2025-26), cross-validated against TSN-labeled injury counts.

### Task 1: NHL player game-log endpoint spike

**Type:** Investigation. No production code yet — just confirm the endpoint shape.

- [ ] **Step 1: Pick a Devils skater + season as the probe target**

Jack Hughes 2023-24 (`playerId=8481559`) — he had a season-ending injury in March 2024, so the data should show clear absence patterns.

- [ ] **Step 2: Hit the endpoint, capture sample JSON**

```bash
curl -s -H "User-Agent: Mozilla/5.0" \
  "https://api-web.nhle.com/v1/player/8481559/game-log/20232024/2" \
  | python3 -m json.tool | head -80
```

Game type `2` is regular season. Expected: list of games with date, opponent, goals/assists/TOI/shots, etc.

- [ ] **Step 3: Document the shape**

Write a spike note (not a publication) at `docs/superpowers/research/2026-05-19-nhl-game-log-shape.md` capturing:
- Available fields per game
- Whether the response includes "DNP" rows or only games-played rows (critical distinction — see open question in scouting report)
- Whether there's a way to detect "scratched" vs "did not dress" vs "minor-league assignment"
- The endpoint's behavior for traded players mid-season (does it return both teams' games or only the queried team's?)

- [ ] **Step 4: Acceptance criteria**

A spike-note doc that answers all four questions above. If the endpoint only returns played-games (no DNP rows), the absence-episode logic in T3 has to derive absences from the team schedule, not from the game log directly.

**Anti-goal:** Don't write production loader code yet. Move on once shape is documented.

---

### Task 2: Player game-log ingest (`raw.player_game_log`)

**Files:**
- Create: `data/ingest/nhl_player_game_log.py`
- Create: `tests/test_ingest_player_game_log.py`
- Modify: `data/ingest/run_all.py` (add player-game-log step)

- [ ] **Step 1: Write the failing test first**

`tests/test_ingest_player_game_log.py`:
- Fixture: a small fake roster (one team, three players, one season) and a stub HTTP response per player.
- Assert: after `ingest(con, players, season)` runs, `raw.player_game_log` has expected row count, expected columns (`player_id`, `season`, `game_id`, `game_date`, `team_id`, `opponent_id`, `goals`, `assists`, `shots`, `toi_seconds`, `fetched_at`), no duplicates on `(player_id, game_id)`.
- Reuse `tmp_warehouse` fixture from `tests/conftest.py`.

- [ ] **Step 2: Implement the loader**

`data/ingest/nhl_player_game_log.py`:
- Signature: `def ingest(con, player_ids: list[int], season: int, *, cache: Path | None = None) -> int`
- Per Phase 0's idempotence convention: wrap delete-by-`(player_id, season)` + insert in `BEGIN`/`COMMIT`/`ROLLBACK` (mirror `moneypuck_shots.py` pattern from `7f50a20`).
- Cache responses to `cache / "player_game_log" / f"{player_id}_{season}.json"` to avoid re-hitting the API.
- Returns total rows inserted.

- [ ] **Step 3: Driver function — fetch the league**

`def ingest_league_season(con, season: int, cache: Path | None = None)`:
- Pull each team's roster via existing NHL API helper (or add to `data.py`): `/v1/roster/{team}/{season}`.
- For each player on each roster, call `ingest(con, [player_id], season, cache=cache)`.
- Skip goalies for Phase 1 (different stats schema; out of scope).
- Polite rate limit: `time.sleep(0.1)` between requests. ~700 players × 0.1s = ~70s per season; 4 seasons = ~5 min total.

- [ ] **Step 4: Wire into `run_all.py`**

Extend the argparse to accept a flag `--player-game-logs` that triggers the league-season ingest. Default `False` (it's slow). Document in the README.

- [ ] **Step 5: Acceptance**

- `make data --player-game-logs` populates `raw.player_game_log` with ~50k+ rows for one season.
- Rerunning is idempotent (row count stable; `fetched_at` updates).
- Tests pass.
- Manual sanity check: `SELECT COUNT(DISTINCT player_id) FROM raw.player_game_log WHERE season = 2023` returns ~700-800.

---

### Task 3: Absence-episode derivation (`devilishdash/absence.py` + `clean.player_game_appearances`)

**Files:**
- Create: `devilishdash/absence.py`
- Create: `tests/test_absence.py`
- Create or extend: `data/ingest/build_marts.py` (already exists from Phase 0; add `build_player_game_appearances`)

The key trick: **the NHL game-log endpoint likely returns only played games.** So we derive "did not play" by joining each player-season-team to that team's full schedule.

- [ ] **Step 1: Define the data product**

`clean.player_game_appearances` schema:
```
player_id  INTEGER
season     INTEGER
team_id    INTEGER         # the team the player was on at this game (handles trades)
game_id    INTEGER
game_date  DATE
played     BOOLEAN
goals      INTEGER         # NULL if not played
assists    INTEGER         # NULL if not played
shots      INTEGER         # NULL if not played
toi_seconds INTEGER        # NULL if not played
```

One row per (player_id, season, team_id, game_id). Built by left-joining `raw.player_game_log` onto `raw.schedule` with the player's roster set.

- [ ] **Step 2: Write the failing tests**

`tests/test_absence.py`:
- `test_appearances_includes_dnp_rows`: insert a player game log of 70 games but a team schedule of 82; assert appearance rows = 82 with 12 having `played=False`.
- `test_consecutive_absences`: given a player with `played` values `[T, T, F, F, F, T, T]`, assert `episodes(appearances, min_length=3)` yields one episode of length 3.
- `test_min_length_filter`: same data with `min_length=4` returns no episodes.
- `test_traded_player_split`: a player with 41 games on Team A and 41 on Team B should produce zero absences (handled by joining per team_id).

- [ ] **Step 3: Implement `devilishdash/absence.py`**

```python
def derive_appearances(con) -> None:
    """Build clean.player_game_appearances from raw.player_game_log + raw.schedule."""

def derive_episodes(con, *, min_length: int = 3) -> None:
    """Build mart.absence_episodes from clean.player_game_appearances."""
```

For the SQL: use DuckDB window functions (`LAG`, `LEAD`, gap-and-island pattern) to identify contiguous F-runs per (player_id, season, team_id).

- [ ] **Step 4: Build mart**

`mart.absence_episodes` schema:
```
episode_id          INTEGER PRIMARY KEY    # rowid OK
player_id           INTEGER
season              INTEGER
team_id             INTEGER
first_missed_game_id INTEGER
last_missed_game_id  INTEGER
first_missed_date    DATE
last_missed_date     DATE
n_games_missed       INTEGER
return_game_id       INTEGER                 # NULL if season ended in absence
return_game_date     DATE                    # NULL if season ended in absence
```

- [ ] **Step 5: Acceptance**

- Tests pass.
- `SELECT COUNT(*) FROM mart.absence_episodes WHERE season = 2023 AND n_games_missed >= 5` returns a plausible number (probably 300-500 league-wide).
- Spot-check: known season-ending injuries (e.g., Jack Hughes 2024 — find a real example) appear as expected episodes.

---

### Task 4: Schema documentation update

**Files:**
- Modify: `data/schema.md`

- [ ] Add `raw.player_game_log`, `clean.player_game_appearances`, `mart.absence_episodes`, `raw.lwadya_injuries` (preview for T5) with column-level docs.
- [ ] Update the schema diagram at the top of the file.
- [ ] Acceptance: `data/schema.md` documents every new table; doc-linter (if added) passes.

---

### Task 5: lwadya/nhl_injuries cross-validation ingest

**Files:**
- Create: `data/ingest/lwadya_injuries.py`
- Create: `tests/test_ingest_lwadya.py`

- [ ] **Step 1: Find the CSV in the lwadya repo**

`git clone https://github.com/lwadya/nhl_injuries /tmp/lwadya_injuries` and `ls /tmp/lwadya_injuries/data/`. Identify the per-player-season injury CSV (likely something like `nhl_injuries.csv` or `data/injuries.csv`).

- [ ] **Step 2: Ingest as-is into `raw.lwadya_injuries`**

Don't pretty up the schema — preserve the CSV columns verbatim with snake_case renaming. This is reference data; let the cross-validation step handle the join.

- [ ] **Step 3: Create the cross-validation view**

`mart.absence_vs_lwadya` joining per-player-season:
- `derived_total_missed_games` = sum from `mart.absence_episodes`
- `lwadya_total_missed_games` = from `raw.lwadya_injuries`
- `delta` = derived − lwadya

- [ ] **Step 4: Sanity-check the proxy quality**

Write a one-off Quarto note (or just a notebook cell) showing the correlation between derived and labeled values. **Target:** Pearson ρ ≥ 0.7 between derived and labeled per-player-season totals. If ρ < 0.5, the proxy is too noisy and we need to tune `min_length` or filter on roster moves more carefully.

- [ ] **Step 5: Acceptance**

- Lwadya data ingested into `raw.lwadya_injuries`.
- Cross-validation view exists in `mart.absence_vs_lwadya`.
- A short methodology note `notes/2026-XX-XX-absence-proxy-validation.qmd` published with the correlation figure (could be Publication 2 itself, or a precursor note).

---

## Stage B — Statistical analysis (W4-7)

Goal: estimate "performance ~ games-since-return + controls" with random effect per player, separately for Devils and league baseline.

**Note:** Stage B should be re-detailed at task-level *after* Stage A ships. The exact metric definitions and matched-controls strategy depend on the absence-episode mart's row counts and shape. The outline below is the placeholder.

### Task 6: Performance windowing helpers (`devilishdash/stats.py` extension)

- [ ] Add `window_metrics(appearances_df, *, window: int) -> DataFrame` that computes per-60 metrics over a rolling N-game window.
- [ ] Add `pre_post_episode_metrics(episodes_df, appearances_df, *, pre_window: int, post_window: int)` that joins each absence episode to its before/after performance windows.
- [ ] TDD-style tests against fixture data.

### Task 7: Matched-controls definition

- [ ] Define a "comparable control" for each absence episode: same season, same position, similar age (±2 years), similar TOI/game pre-episode (±1 minute), no absence within ±N games.
- [ ] Implement as a SQL view `mart.episode_controls`.
- [ ] Validate: each absence episode has ≥1 control match on average. If sparse, loosen the criteria.

### Task 8: Mixed-effects model (`devilishdash/models.py`)

- [ ] Wrap `statsmodels.regression.mixed_linear_model.MixedLM` in a thin function: `fit_recovery_model(df, *, formula, group_col) -> ModelResult`.
- [ ] Devils-only fit, league-only fit, combined-with-interaction fit.
- [ ] Bootstrap CIs (1000 resamples; reuse Phase 0 conventions).
- [ ] Decide here whether `pymer4` is needed (only if convergence is bad — defer until evidence).

### Task 9: Recovery-curve figures

- [ ] For each fit, produce a "performance vs. games-since-return" curve with bootstrap band.
- [ ] Overlay Devils on league.
- [ ] Use `devilishdash.viz.HOUSE_PALETTE`; reuse Phase 0 style.

---

## Stage C — Publication (W8-10)

Goal: a long-form Quarto project page presenting the methodology, results, and limitations. The most-important readable artifact.

**Note:** detailed tasks added after Stage B confirms what the results actually say. Publication shape depends on whether the result is positive, negative, or null — and the spec's negative-result protocol means we publish either way.

### Task 10: Project page scaffold

- [ ] Create `projects/devils-injury-study/index.qmd` with title, abstract placeholder, and a "Methodology" section that imports from `devilishdash.absence` and renders sample tables.
- [ ] Add to `projects/index.qmd` listing.
- [ ] Verify it renders via `make preview`.

### Task 11: Methodology section

- [ ] Write the methodology section honestly: the absence-proxy rationale, the cross-validation against lwadya, the limitations.
- [ ] This is the section that signals analyst judgment — invest in it.

### Task 12: Results section + figures

- [ ] Embed the recovery-curve figures from Stage B.
- [ ] Tables of effect sizes with CIs.
- [ ] Devils-specific call-out box.

### Task 13: Limitations + future work

- [ ] Document the absence-proxy edge cases.
- [ ] Cite the forward-snapshot dataset (T14) as the path to a cleaner Phase 2 study.

---

## Stage D — Forward snapshot dataset (parallel; non-blocking)

Goal: start accumulating a real injury ledger from today onward. Not used in Phase 1 analysis; seeds future-phase enrichment.

### Task 14: Daily HR injury snapshot

**Files:**
- Create: `data/ingest/hr_injury_snapshot.py`
- Create: `tests/test_ingest_hr_snapshot.py`
- Create: `.github/workflows/hr-injury-snapshot.yml`

- [ ] **Step 1: Pre-flight test against the live page**

`curl -H "User-Agent: Mozilla/5.0" https://www.hockey-reference.com/friv/injuries.cgi` — confirm we still get the same table structure as documented in the scouting report. (Test now, and test again in two weeks before scheduling daily.)

- [ ] **Step 2: Write the failing test**

Capture the current HR injury HTML once into `tests/fixtures/hr_injuries_sample.html`. Test that the parser extracts a known row correctly.

- [ ] **Step 3: Implement the snapshot+parse**

`data/ingest/hr_injury_snapshot.py`:
- `def snapshot(out_dir: Path) -> Path`: download HTML, save to `out_dir / f"{today}.html"`, return path.
- `def parse(path: Path) -> DataFrame`: parse HTML into a DataFrame matching `raw.hr_injury_snapshots` schema.
- `def ingest(con, snapshot_path: Path)`: upsert into `raw.hr_injury_snapshots` keyed by `(snapshot_date, player_id_csk)`.

`raw.hr_injury_snapshots` schema:
```
snapshot_date    DATE
player_csk       TEXT          # HR's player slug, e.g., "gritsar01"
player_name      TEXT
team_id          TEXT          # 3-letter HR team code
date_of_injury   DATE
injury_type      TEXT
injury_note      TEXT
```

- [ ] **Step 4: GitHub Actions cron**

`.github/workflows/hr-injury-snapshot.yml`:
- Runs daily at 12:00 UTC.
- Checks out `main`, runs snapshot+ingest, commits the warehouse change if any.
- **Don't commit raw HTML** — `data/snapshots/` is gitignored to keep the repo lean. The warehouse delta is the durable record.

- [ ] **Step 5: Episode-derivation logic (read-only mart)**

After ~14 days of accumulated snapshots, add `mart.hr_injury_episodes` deriving open/close dates from snapshot diffs. Don't build this in T14 — write it in a follow-up task once data exists.

- [ ] **Step 6: Acceptance**

- Manual run succeeds: `uv run python -m data.ingest.hr_injury_snapshot --once`.
- Workflow runs daily and the warehouse accumulates one row per current-injury-per-day.
- Tests pass.
- After 30 days: spot-check a known mid-season injury that opened and closed appears as a clean episode.

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| NHL game-log endpoint returns only played games (no DNP rows) | High (assumed) | T3 derives absences via schedule-join; designed for this case from the start. |
| Absence proxy correlates poorly with lwadya labels (ρ < 0.5) | Medium | T5 cross-validates explicitly; if proxy is bad, tune `min_length` or add roster-move filter; worst case, scope to single season where we can manually validate. |
| Mixed-effects model fails to converge in statsmodels | Medium | T8 has a `pymer4` fallback noted; can also simplify to OLS with cluster-robust SEs as a degraded mode. |
| HR injury page structure changes mid-season, breaking snapshot parser | Medium | T14 Step 1 pre-flight; parser logs structural mismatches; cron alerts on parse failure. |
| Phase 1 data-gathering exceeds 3-week cap | Low (methodology pivot reduces this) | Spec's scope-down protocol: ship with single-season analysis (2023-24 only) if multi-season data is too thin. |
| Devils sample size too small for statistical significance | Medium (Devils-only n is small by construction) | Frame the analysis as estimation, not hypothesis test. Devils-vs-league overlay with explicit CIs is the story; "p < 0.05" is not the story. |
| Forward-snapshot data isn't ready in time for publication | Certain | T14 is explicitly non-blocking. Phase 1 ships without it; T14 starts the dataset for Phase 2+. |

---

## Definition of done for Phase 1

- All Stage A tasks shipped; absence-episode mart populated for 4 seasons; cross-validation note published.
- All Stage B tasks shipped; recovery curves generated for Devils-vs-league.
- Stage C: project page live at `https://mbrunetti.netlify.app/projects/devils-injury-study/`, linked from `projects/index.qmd`.
- Stage D: T14 deployed; daily cron running; warehouse accumulating ≥14 days of snapshots before Phase 1 ships.
- README updated with a "Featured project" link to the Devils study.
- An update to `docs/superpowers/research/2026-05-19-phase-1-injury-data-scouting.md`'s "Open questions" section, marking each as answered or escalated.

---

## Out of scope for Phase 1

- Goaltender analysis (different stats schema; revisit Phase 3).
- Injury-type-specific subanalyses (data doesn't exist).
- Causal inference beyond the matched-control comparison (no IV, no DiD; the data won't support it).
- Public-API hosting of the warehouse (Phase 5 capstone consideration).
