# Phase 1 — Injury Data Scouting Spike

**Date:** 2026-05-19
**Author:** Matthew Brunetti (with Claude)
**Context:** Phase 1 of the hockey-analytics portfolio is the Devils Injury-Recovery Study. The spec (`docs/superpowers/specs/2026-05-07-hockey-analytics-portfolio-design.md` §4 Phase 1) names injury-data assembly as the hardest gate. This document captures a focused 1-hour scouting spike conducted before writing the Phase 1 task plan.

**TL;DR:** No public source has a structured archive of *resolved* historical injuries with per-event dates and types. The closest free source — Hockey Reference's `/friv/injuries.cgi` — only shows currently-open injuries. Wayback Machine snapshots are sparse. The recommended path forward is a **methodology pivot**: use NHL API game-log gaps as injury proxies for historical seasons, and start daily HR snapshots now to accumulate a forward-looking dataset.

---

## 1. Sources investigated

### 1.1 NHL official API (`api-web.nhle.com`)

- **Verdict:** Free, no UA needed, but **no IR / injury status field anywhere**.
- **What works:**
  - `/v1/roster/{team}/{season}` returns the active roster as JSON. Fields are identity-only (id, name, position, biometrics, birth). Verified against `NJD/20232024`.
  - `/v1/player/{playerId}/game-log/{season}/{gameType}` (per Zmalski's unofficial reference) returns per-game player participation — usable for "absence detection" (player on roster, didn't play, team played → missed game).
- **What doesn't exist:** `/v1/transactions` returns 404. There is no documented transactions, IR, or injury endpoint in either Zmalski's or dfleis's API references.
- **Inference:** The league deliberately doesn't expose injury data through their API. Any "scrape it" approach is fighting the league's information policy, not just an engineering problem.

### 1.2 Hockey Reference (`hockey-reference.com`)

- **`/friv/injuries.cgi`** — ✅ **The scouting find of the day.**
  - Free, scrapable with a normal browser User-Agent (default Python `requests` UA returns 403; Mozilla UA returns 200).
  - Clean HTML table with columns: Player, Team, Date of Injury, Injury Type (e.g., "Upper-Body", "ACL"), Injury Note (free-text including return-date hints).
  - 2026-05-19 sample row (Devils): `Arseny Gritsyuk | NJD | Mar 24, 2026 | Upper-Body | "...will have surgery...will miss the rest of the season."`
  - **Critical limitation:** Only *currently open* injuries. Once a player returns, the row vanishes. This is a state snapshot, not a ledger.
- **Team page** (e.g., `/teams/NJD/2024.html`) — has "Injuries" in the meta title but no injury table in the page body. Misleading SEO text.
- **Player pages** — pattern `/players/{first-letter}/{slug}.html`. URL slug isn't trivial to guess; would need to query the player index first. Not investigated in depth — deferred until needed.

### 1.3 PuckPedia (`puckpedia.com`)

- **Verdict:** UA-blocked. Default WebFetch returns 403. Likely solvable with a browser-like UA, Playwright, or scraping their internal API if one exists.
- **Known surface area:** `/transactions` and `/injuries` exist; visible in a normal browser; both show current-state, not a historical ledger (consistent with HR).
- **Not investigated:** API endpoints, Playwright access, or whether their data goes deeper than the public UI suggests.

### 1.4 DailyFaceoff (`dailyfaceoff.com`)

- **Verdict:** UA-blocked + URL structure changed. The spec-cited URL pattern (`/teams/new-jersey-devils/injuries`) returns 404. The active injury report appears to be at `/hockey-player-news/injuries/1`.
- **Not investigated:** Whether the archive is paywalled (anecdotally suggested to be).

### 1.5 TSN (`tsn.ca/nhl/injuries`)

- **Verdict:** JavaScript-rendered; requires Playwright/Selenium. Per `lwadya/nhl_injuries` (see §1.7), scrapable but data is "not exhaustive."
- **Not investigated** beyond confirming the URL pattern.

### 1.6 NHL Injury Viz (`nhlinjuryviz.blogspot.com`)

- **Verdict:** A solo blogger ("LW3H") publishing team-level man-games-lost visualizations using PuckPedia + CBS Sports + Evolving-Hockey data.
- **Coverage:** 2024-25 and 2025-26 seasons; current-season focused.
- **Raw data:** Not shared publicly. Visualizations only.
- **Action item:** Worth emailing the author if we end up needing labeled data — collaboration may be possible.

### 1.7 `lwadya/nhl_injuries` (GitHub, MIT-licensed)

- **Verdict:** Closest prior art to our task. A 10-season dataset combining Natural Stat Trick player stats with TSN-scraped injury counts.
- **Granularity:** Season-aggregate ("player X missed N games this season"), not per-injury-event.
- **Author's caveat:** "Not exhaustive" — TSN scrape misses injuries.
- **Author's model performance:** Lasso R² = 0.075, Random Forest R² = 0.107. Author concludes "NHL injuries are largely random events that are difficult to neatly capture in a model."
- **Usable as:** A coarse ground-truth label for cross-checking an absence-proxy approach.

### 1.8 Wayback Machine reconstruction

- **Verdict:** Effectively unviable for HR's injury page.
- **Evidence:** `https://web.archive.org/wayback/available?url=hockey-reference.com/friv/injuries.cgi&timestamp=20240115` returns 404 — Wayback has no snapshot near that date. CDX API was 503 on the day of investigation; could retry, but the `available` 404 already signals sparse coverage.
- **Implication:** Cannot diff snapshots to reconstruct injury episodes for the 2023-24 season post-hoc.

---

## 2. The shape of the gap

Every accessible public source is a **current-state snapshot**, not a historical ledger. When a player returns from injury, their row is removed from these pages. No free source preserves:

- Date the player was placed on IR / disappeared from the active roster
- Date the player returned
- Injury type
- Player ID / canonical identifier

…with multi-season historical coverage in a queryable form.

This is consistent with the broader market reality: **clean injury data is a moat in pro hockey ops.** Teams have proprietary medical and IR logs. Public analysts (Tulsky, HockeyViz, the lwadya project) all reconstruct from scattered news mentions and accept lossy coverage. We can't out-engineer that constraint on a one-laptop project.

---

## 3. Methodology pivot

The spec's hypothesis stays the same: **"Do the Devils underperform after returning from mid-season injury, relative to the league baseline?"**

The *operationalization* changes:

### Original spec plan (now known infeasible)

> W1-3: Build injury dataset by triangulating IR transactions (PuckPedia), DailyFaceoff archives, ManGamesLost, beat-reporter game notes. Joined to player-season identity.

This presumed that triangulation across those sources would produce a clean multi-season injury ledger. Scouting shows the underlying data isn't there.

### Revised plan (this document)

1. **Absence-proxy approach for historical seasons (2022-23, 2023-24, 2024-25, 2025-26):**
   - Use NHL API player game logs + team schedule.
   - Define "extended absence" = player listed on a season roster, did not play in N consecutive team games (N likely ≥ 3, tunable).
   - This captures injuries, healthy scratches, suspensions, and minor-league assignments — i.e., it's a *missed-game proxy*, not a pure injury signal.
   - Acceptable because: the analysis question is about *post-absence performance*, and most extended skater absences during a season are in fact injuries (healthy scratches are usually 1-2 games; suspensions are publicly known; minor-league assignments are identifiable from roster moves).

2. **Cross-validation against labeled data:**
   - Use `lwadya/nhl_injuries` season-aggregate injury counts as a ground-truth check: does our proxy's per-player season total roughly match TSN-labeled total? If yes, the proxy is reasonable. If not, we need to filter.

3. **Forward snapshot to build a real injury ledger:**
   - Start scraping HR's `/friv/injuries.cgi` daily into the warehouse from now on.
   - Snapshots over time = a real injury ledger for the 2026-27 season and beyond.
   - Not used in the Phase 1 analysis itself (insufficient accumulation), but cited as future work and the start of an ongoing dataset.

4. **Reframe the publication slightly:**
   - Title direction: "Do the Devils underperform after extended absences? A proxy-based analysis of player return performance."
   - Methodology section is *more interesting* than the original would have been — it includes the constraint, the proxy design, the validation against labeled data, and the limitations. That's the kind of methodology rigor that signals strong analyst judgment.
   - Negative-result protocol still applies.

### What this pivot costs

- **Cannot distinguish injury cause** (upper-body vs. ACL etc.). The original plan never really delivered this either — TSN labels were "not exhaustive."
- **Cannot distinguish injury from healthy scratch / minor-league assignment in edge cases.** Mitigation: cross-validate with lwadya data, threshold consecutive-games filter, and flag uncertain cases.
- **Cannot study return-from-specific-injury-type effects.** This was never going to be tractable from any public source.

### What this pivot preserves

- The core hypothesis (Devils vs. league baseline) is still testable.
- The 8-10 week timeline is preserved.
- The publication still has methodology bones worth showing.
- The dataset is reproducible from the NHL API — no scraping moats.

---

## 4. Implications for the Phase 1 task plan

The plan (to be written next) should structure around:

1. **Data ingest:**
   - Extend `data/ingest/` with a player-game-log loader (NHL API per-player game log endpoint).
   - Joined to existing `raw.schedule` for team-played-game context.
   - Net output: `clean.player_game_appearances` (one row per player-game with `played: bool`).

2. **Absence-episode derivation:**
   - SQL view / mart for absence episodes: contiguous runs of `played=false` while team played, ≥ N games long.
   - Output: `mart.absence_episodes (player_id, start_game, end_game, n_games_missed, season)`.

3. **Performance windowing:**
   - Define pre-absence and post-absence windows (e.g., 10 games before, 10 games after).
   - Compute per-60 metrics in each window using existing `devilishdash/stats.py` helpers.

4. **Statistical model:**
   - Mixed-effects regression `performance ~ games_since_return + age + position + season + (1|player)`.
   - Bootstrap CIs.
   - Devils-vs-league overlay.

5. **Cross-validation against labeled data:**
   - Pull `lwadya/nhl_injuries` season aggregates.
   - Validate absence-proxy season totals against TSN-labeled totals per player.

6. **Forward-scraper for HR injury page (kicks off the next dataset):**
   - Daily cron / GitHub Actions snapshot to `data/snapshots/hr_injuries/YYYY-MM-DD.html`.
   - Parser into `raw.hr_injury_snapshots` (one row per player-day still on the injury list).
   - Episode derivation: player appears day X = open, disappears day Y = closed → injury episode (start X, end Y).
   - Not used in Phase 1 analysis; sets up Phase 1.5 or Phase 2 enrichment.

7. **Quarto write-up (Publication 2):**
   - Methodology section discusses the data constraint and proxy design candidly.
   - Results section uses Devils-vs-league overlay charts.
   - Limitations section discusses proxy edge cases.
   - Open-source repo link.

---

## 5. Decisions captured

- ✅ **Methodology: pivot to absence-proxy** (decided 2026-05-19 with the user).
- ✅ **Documentation: scouting report committed to repo before the plan is written** (this file).
- ⏳ **Scope: league-wide vs. Devils-and-comparables** — defer until first cut of the absence-episode mart shows row counts and data shape.
- ⏳ **Snapshot infrastructure: start now or wait until Phase 1 ships** — defer; not blocking Phase 1 analysis.

---

## 6. Sources

Scouting was conducted on 2026-05-19. Key URLs probed:

- [NHL API roster — Devils 2023-24](https://api-web.nhle.com/v1/roster/NJD/20232024)
- [Hockey Reference — current injuries](https://www.hockey-reference.com/friv/injuries.cgi)
- [Zmalski NHL API reference](https://github.com/Zmalski/NHL-API-Reference)
- [lwadya/nhl_injuries](https://github.com/lwadya/nhl_injuries) (MIT license)
- [NHL Injury Viz](https://nhlinjuryviz.blogspot.com/)
- [PuckPedia transactions](https://puckpedia.com/transactions) (UA-blocked)
- [DailyFaceoff injury report](https://www.dailyfaceoff.com/hockey-player-news/injuries/1) (UA-blocked)
- [TSN injuries](https://www.tsn.ca/nhl/injuries/) (JS-rendered)

---

## 7. Open questions for follow-up sessions

- Is HR's `/friv/injuries.cgi` rate-limited? Need to test before scheduling daily snapshots.
- What's the actual NHL game-log endpoint shape — does it cleanly distinguish "did not dress" from "did not play" (e.g., backup goalie)?
- How does the NHL API surface mid-season trades? A traded player has a roster move that looks like a roster disappearance — need to filter those out before counting absences.
- Does lwadya's CSV survive a `git clone` and parse cleanly, or has the schema changed?
- What's the right minimum-absence threshold N? Try N=3, N=5, N=10 and see which produces cleanest cross-validation against lwadya.
