# Hockey Analytics Learning Roadmap & Portfolio Site — Design

**Author:** Matthew Brunetti
**Date:** 2026-05-07
**Status:** Approved by user, ready for implementation planning

---

## 1. Vision

Build an integrated 9-12 month program that produces:

1. The skills of a competent hockey analyst (player evaluation, draft modeling, statistical inference, ML for sports, reproducible analysis), and
2. A public-facing portfolio website that demonstrates those skills through completed analyses,

…in service of a **career pivot from business-analytics consulting into a hockey operations analytics role** (NHL/AHL team, or hockey data company).

Each learning milestone produces a website artifact. Skills development and portfolio construction are not separate tracks — they are the same track viewed from two angles.

## 2. User & motivation

- Senior consultant at a business analytics consulting company; 5+ years professional experience.
- Strong/used professionally: SQL, Snowflake, Alteryx, Tableau, QlikSense, PowerBI, Python (pandas), Jupyter, Git/GitHub, viz libraries.
- Gaps: R (we won't use it), web frameworks (we won't need them), statistical methods beyond intro, deployment.
- Hockey background: engaged NHL fan, follows Evolving-Hockey and HockeyViz, gets gist of advanced metrics without owning the math; New Jersey Devils fan.
- Side interest (bonus, not focus): fantasy/betting applications.
- Time commitment: 5-10 hours/week, bursty average; 9-12 month horizon.
- Career rationale: likes current work but wants more passion; for hockey ops the public portfolio *is* the application — most working hockey ops analysts (Tulsky, Charron, Dellow, Mehta) were hired from public-facing work.

## 3. Approach decisions

| Decision | Choice | Reason |
|---|---|---|
| Learning + site relationship | **Integrated** — every milestone produces a site artifact | Forces shipped work; builds skills and portfolio together |
| Tech stack | **Quarto-First Analyst Path** | Low web-side overhead, native to analyst community (HockeyViz, academia), excellent default output |
| Site IA | **Standard Analyst Blog** — Home / Projects / Notes / About | Notes prevents perfectionism trap; Skills page omitted in favor of project-anchored skill display |
| Project page anatomy | **Insight-First** (BLUF) — title → tagline → hero chart → body → collapsible methodology → repo link | Optimizes for skim-readers (hiring managers, ~90 seconds); academic structure underperforms for hiring portfolios |
| Identity | **Real name** | Job-seeker site benefits from named identity over pseudonym |
| Distribution | Quarto-published site **+ Twitter threads per long-form** | Two non-exclusive channels; Twitter is where hockey-ops scouts talent |
| Skills display | **Project-tag aggregation + About-page Tools section** (no static Skills page) | Project-anchored skills display is durable and credible; Skills pages rot |

## 4. Roadmap of milestones

### Phase 0 — Foundation (3-4 weeks)

Build infrastructure once, use it forever.

- Dev environment: Python 3.12 + `uv` + `ruff`.
- Stand up Quarto site, deploy "hello world" to Netlify with continuous deploy from GitHub `main`.
- Build personal hockey data warehouse: DuckDB file populated by `nhl-api-py`/`hockey_scraper`, MoneyPuck CSVs, Natural Stat Trick. Documented schema (`raw_*`, `clean_*`, `mart_*`).
- Read landmark canon: Tulsky's Corsi essays, Andrew Thomas' xG paper, Evolving-Hockey RAPM methodology, HockeyViz documentation.
- **Publication 1 (Note):** *"Building a personal NHL data warehouse — the stack and the gotchas."*

**Exit criteria:** Live site at custom domain, working data pipeline runnable with one command, one published note.

### Phase 1 — Project 1: Devils Injury-Recovery Study (8-10 weeks)

User's motivating question. Hypothesis: Devils' players underperform after returning from mid-season injury more than league-wide baseline.

- **W1-3:** Build injury dataset by triangulating IR transactions (PuckPedia), DailyFaceoff archives, ManGamesLost, beat-reporter game notes. Joined to player-season identity.
- **W4-5:** Define performance (per-60: xGF%, points/60, individual xG/60). Pick matched controls (similar age/position/role/season, no IR stint).
- **W6-7:** Mixed-effects regression `performance ~ games_since_return + controls`, random effect per player. Bootstrapped recovery curves. Devils-vs-league overlay.
- **W8-10:** Visualization, peer review (Hockey Graphs Discord), publish.
- **Publication 2 (Long-form):** Devils piece + Twitter thread + open-source repo.

**Negative-result protocol:** If the Devils do not actually underperform vs. league baseline, *publish anyway* — "I had this fan-hypothesis, here's what the data says" is a credibility-building paper.

**Cap:** Data-gathering phase capped at 4 weeks. If incomplete, scope down to "Devils + 5 comparable teams" and ship.

### Phase 1.5 — Stats deepening (2-3 weeks; can overlap with Phase 1 tail)

- Mixed-effects models in `statsmodels`/`pymer4` (used in P1).
- Bootstrapping and uncertainty quantification.
- Regularization (ridge/lasso) — prerequisite for RAPM.
- Conceptual Bayesian — `pymc` enough to read Bayesian results in literature.

Each topic = one 30-min hockey-data exercise; one becomes a Note.

### Phase 2 — Project 2: Build your own xG model (5-7 weeks)

The rite of passage.

- NHL play-by-play; engineer features (location, type, rebound, rush, prior event, score state, strength).
- Compare logistic regression vs. gradient boosting (`xgboost`/`lightgbm`).
- Calibration curves, log-loss, AUC, time-aware CV.
- Compare predictions to MoneyPuck; explain divergences.
- **Publication 3 (Long-form):** model write-up + reusable open-source repo.

**Expected outcome:** Your model will *not* beat MoneyPuck. That's not the point — the write-up is the deliverable.

### Phase 3 — Project 3: Player evaluation deep-dive (8-10 weeks)

Marquee piece. Top-interest area.

- Build regularized adjusted plus-minus (RAPM) using your Phase-2 xG as input.
- Multi-season data, large sparse design matrices, ridge regression.
- Compare your top-10 forwards to Evolving-Hockey's published GAR.
- **Publication 4 (Long-form + interactive):** analysis + embedded Observable JS dashboard for team-level exploration.

### Phase 4 — Project 4: Draft / prospect translation model (6-8 weeks)

Second top-interest area.

- Historical CHL/NCAA/Liiga/SHL data.
- League translations (NHLE, league-quality coefficients).
- Age curves, projection under uncertainty.
- Output tool: "Player X projects as ~0.45 NHL pts/game (±0.12) by age 23."
- **Publication 5 (Long-form):** with interactive prospect comparison.

### Phase 5 — Capstone (8-10 weeks)

Pick at the time, based on what's clicking. Options:

- α: Tracking-data spatial analysis (NHL EDGE).
- β: Goalie deep-dive (high-value niche).
- γ: Devils roster construction critique using all your tools.
- δ: "Which junior leagues are NHL teams under-scouting?" using the Phase-4 model.

### Continuous (throughout)

- 1-2 short Notes per phase.
- Twitter thread for every long-form.
- Quarterly "what I'm working on" Note.
- Read everything Evolving-Hockey, HockeyViz, JFresh, Hockey Graphs publish.

**End-state portfolio:** ≥5 long-form analyses + 1 capstone + 8-12 notes + 2-3 open-source repos.

## 5. Technical foundation

### Repo layout (single monorepo at `/home/bruno/devilishdash/`)

```
devilishdash/
├── _quarto.yml              # site-level config
├── index.qmd                # home
├── about.qmd                # bio + contact + Tools/Methods section
├── projects/                # long-form analyses
│   └── 2026-injury-recovery/
│       ├── index.qmd        # published page
│       ├── analysis.ipynb   # exploratory notebook
│       ├── hypotheses.md    # pre-registered hypotheses
│       └── data/            # cleaned project-specific extracts
├── notes/                   # short-form (Quarto blog format)
├── data/                    # SHARED data layer
│   ├── warehouse.duckdb     # personal warehouse
│   ├── ingest/              # idempotent scrapers
│   └── schema.md            # documented schema
├── devilishdash/            # personal Python utility package
│   ├── data.py              # warehouse helpers
│   ├── viz.py               # set_house_style() + chart palette
│   └── stats.py             # rolling/per60 helpers
├── pyproject.toml
├── README.md
└── .github/workflows/deploy.yml  # render quarto + deploy on push
```

### Tools

| Layer | Tool |
|---|---|
| Python env | uv |
| Lint/format | ruff |
| Data manipulation | pandas (Polars later if comfortable) |
| Warehouse | DuckDB |
| Stats | statsmodels, pymer4 |
| ML | scikit-learn, xgboost |
| Bayesian | pymc (Phase 1.5+) |
| Viz | matplotlib + plotnine + plotly + Observable JS |
| Notebooks | Jupyter (Quarto renders .ipynb natively) |
| Site | Quarto |
| Hosting | Netlify (free tier, auto-deploy) |
| CI | GitHub Actions |

### Data layer principles

- Scrapers are idempotent.
- `raw_*` → `clean_*` → `mart_*` schema progression.
- Warehouse committed if <500MB; git-lfs or rebuild-in-CI beyond.
- One source of truth: every project queries `data/warehouse.duckdb`; no project re-scrapes.

### Visual identity

- Single accent color (avoid Devils red; brand should not be team-locked).
- Two sans fonts (heading + body) + one mono (code).
- Chart palette saved in `devilishdash/viz.py::set_house_style()`; every chart in every project uses it.

## 6. Workflow & operating practices

- **Git from day one.** `git init` in Phase 0; public GitHub repo. Recruiters read commit history.
- **Branch per project.** `project/injury-recovery` → PR → squash merge to main. Self-review via the diff.
- **Pre-register hypotheses** for inferential pieces — a `hypotheses.md` committed before analysis. Distinctive credibility signal.
- **Peer review before publish.** Post drafts to Hockey Graphs Discord (or similar) before going public.
- **Drafts visible.** A `drafts/` folder with `not-yet-public` Quarto pages is fine; "working in public" is welcomed.
- **Code-fold everything.** Every chart has its source code embedded but collapsed by default (`code-fold: true`).
- **Captions matter.** Every chart caption includes units and source.
- **"Last updated" date.** Auto-rendered on every page for trustworthiness.

## 7. Domain (hockey) knowledge track

- **Always-on:** Read everything Evolving-Hockey, HockeyViz, Hockey Graphs publish. Take notes when you don't understand something — that's a future Note post.
- **Phase 0:** Tulsky's Corsi essays; Andrew Thomas' xG paper; Schuckers's RAPM papers.
- **Phase 2:** Robert Vollman's *Hockey Abstract* series.
- **Phase 3:** 2-3 published hiring-team analyst publications.
- **Continuous:** Watch hockey *analytically*. Pick a Devils game per week; predict line decisions; write a Note when surprised.
- **Optional but high-leverage:** *Hockey Graphs* podcast; *Spittin' Chiclets* for hockey-traditional sensibilities.

## 8. Skills display

Three mechanisms (no static Skills page):

1. **Project-page badges.** Each project lists `Tools used:` tags (Python, DuckDB, mixed-effects, etc.); tags clickable as filtered project lists.
2. **About-page Tools & Methods section.** Short, supplementary, one-screen.
3. **Auto-generated home-page widget.** Aggregates project tags into a "stack" summary that updates automatically as projects ship.

## 9. Brand

- **Domain:** real name. Candidates: `mattbrunetti.com`, `matthewbrunetti.com`, `mbrunetti.com`, `brunetti.dev`. Decision deferred to Phase 0 first week.
- **Site title:** real name. Subtitle: "Hockey analytics & data work" or similar.
- **Twitter handle:** ideally matches domain (`@mattbrunetti` or fallback).
- **Avoid project-name branding** (e.g., not "DevilishDash") for the public site — too fan-blog. Internal codename use is fine.

## 10. Predictable failure modes & adaptations

| Failure mode | When | Adaptation |
|---|---|---|
| Project 1 sprawls past 10 weeks (injury data harder than expected) | Most likely | Cap data-gathering at 4 weeks; scope down to Devils + 5 teams; ship |
| Finding you don't fully trust | Common | Publish framed as "here's what I found, here's why I might be wrong, here's what would change my mind" |
| Twitter feels demoralizing | Common, ~Phase 2 | Optimize for being noticed by 5 specific people (hockey ops directors), not the algorithm |
| Burnout around month 4-5 | Statistically likely | Plan a deliberate 2-week off-period at month 4; phases have built-in slack |
| Decide consulting is fine | Possible | The portfolio still serves general data-credibility; no pressure to pivot if you decide not to |
| Phase 2 xG model fails to beat MoneyPuck | Almost certain | The write-up *is* the deliverable; "what I learned trying to replicate MoneyPuck" is the publication |

## 11. Success metrics (12-month checkpoint)

- [ ] 4-5 long-form analyses published with reproducible code
- [ ] 1+ open-source GitHub repo with non-zero stars from hockey-analytics community
- [ ] Twitter following ~200-500 from hockey-analytics circles (not random hockey fans)
- [ ] Comfortable explaining work in a 30-min coffee chat with a hiring manager
- [ ] At least one DM/reply from someone working in hockey analytics
- [ ] At least one phone screen with a hockey analytics role

Failing to hit most of these isn't failure; it's recalibration data. Many self-taught analysts take 18-24 months to land a first role.

## 12. Out of scope

- R / tidyverse (Python-only by deliberate choice).
- Custom React/Next.js site (Quarto only).
- Paid tooling beyond optional Evolving-Hockey ($30/yr) and domain (~$12/yr) and Netlify Pro if needed.
- Live in-game data (NHL EDGE *historical* downloads only; no streaming).
- Salary cap optimization as a primary track (may surface in Phase 5 capstone if chosen).
- Goaltending as a primary track (may surface in Phase 5 capstone if chosen).
- Tactical / video / scouting work — not in current scope.

## 13. Implementation note

This spec is the *what*. The next document is the implementation plan (the *how* and *in what order*) for **Phase 0 specifically** — produced via the writing-plans skill. Phases 1-5 will get their own implementation plans at the start of each phase, informed by what was learned in prior phases.
