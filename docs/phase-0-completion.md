# Phase 0 — Completion Report & Handoff

> **Status as of 2026-05-11:** Phase 0 code is shipped (T1–T14 complete, T15 + T16 awaiting your hands). Local site renders cleanly. All tests pass. Repo not yet pushed to GitHub.

This document captures **everything that was actually built** (which differs in a few places from the plan), the **environment state** on this machine, and the **step-by-step actions you need to take for T15 (Netlify + domain) and T16 (reading list)**.

For the original design intent see `superpowers/specs/2026-05-07-hockey-analytics-portfolio-design.md`. For the per-task plan see `superpowers/plans/2026-05-07-phase-0-foundation.md`. This file is the *what-we-actually-shipped + what-you-do-next* companion.

---

## 1. What's in the repo

```
devilishdash/
├── .github/workflows/deploy.yml      # CI: dormant until Netlify secrets exist
├── .gitignore                        # *.duckdb, data/cache/, __pycache__/, _site/, etc.
├── _quarto.yml                       # Quarto site config (navbar, theme, repo-url)
├── about.qmd                         # Bio + tools/methods
├── custom.scss                       # Empty placeholder (Phase 1: real theming)
├── styles.css                        # Empty placeholder (Phase 1: real theming)
├── data/
│   ├── ingest/                       # Idempotent ingest scripts
│   │   ├── __init__.py
│   │   ├── build_marts.py            # mart.shots_per_game
│   │   ├── moneypuck_shots.py        # download + load_shots (atomic DELETE+INSERT)
│   │   ├── nhl_schedule.py           # fetch_week + load_schedule (upsert)
│   │   └── run_all.py                # Pipeline orchestrator (argparse CLI)
│   └── schema.md                     # Documented warehouse schema
├── devilishdash/                     # Importable Python package
│   ├── __init__.py
│   ├── data.py                       # connect, ensure_schemas, default path
│   ├── stats.py                      # per_60 scalar + DataFrame variants
│   └── viz.py                        # HOUSE_PALETTE + set_house_style
├── docs/
│   ├── phase-0-completion.md         # ← this file
│   └── superpowers/
│       ├── plans/2026-05-07-phase-0-foundation.md
│       └── specs/2026-05-07-hockey-analytics-portfolio-design.md
├── index.qmd                         # Home page
├── Makefile                          # data / preview / render / lint / test / clean
├── notes/
│   ├── _metadata.yml                 # freeze: false, toc: true, code-fold: true
│   ├── 2026-05-09-warehouse-stack.qmd  # Publication 1
│   └── index.qmd                     # Notes listing
├── projects/
│   └── index.qmd                     # Empty listing (Phase 1 fills it)
├── pyproject.toml                    # uv-managed deps, ruff + pytest config
├── README.md
├── tests/                            # 23 tests, all green
│   ├── __init__.py
│   ├── conftest.py                   # tmp_warehouse fixture
│   ├── test_build_marts.py
│   ├── test_data.py
│   ├── test_ingest_moneypuck.py
│   ├── test_ingest_nhl.py
│   ├── test_smoke.py
│   ├── test_stats.py
│   └── test_viz.py
└── uv.lock                           # Pinned dependency graph
```

**Runtime artifacts (gitignored, regenerable):**
- `.venv/` — Python virtual environment created by `uv sync --extra dev`
- `data/warehouse.duckdb` — DuckDB warehouse file (created by `make data`)
- `data/cache/` — MoneyPuck CSV cache (created by ingest)
- `_site/` — Rendered Quarto site (created by `make render`)
- `.quarto/` — Quarto's build cache
- `__pycache__/`, `*.pyc` — Python bytecode

---

## 2. Tech stack as actually installed

| Tool | Version | Path |
|---|---|---|
| Python | 3.14.4 (system) | `/usr/bin/python` |
| Project Python | 3.14.4 (venv) | `.venv/bin/python` |
| `uv` | 0.11.12 | `~/.local/bin/uv` (installed via `astral.sh/uv` script) |
| Quarto | 1.9.37 | `~/.local/share/quarto/bin/quarto` (tarball install, no sudo) |
| DuckDB | resolved via uv.lock | inside `.venv/` |

To re-create the environment on a new machine:

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env

# 2. Sync Python env + editable install of devilishdash
cd /path/to/devilishdash
uv sync --extra dev

# 3. Install Quarto (tarball, no sudo)
curl -L -o /tmp/quarto.tgz \
  "https://github.com/quarto-dev/quarto-cli/releases/download/v1.9.37/quarto-1.9.37-linux-amd64.tar.gz"
mkdir -p ~/.local/share/quarto
tar -xzf /tmp/quarto.tgz -C ~/.local/share/quarto --strip-components=1
export PATH="$HOME/.local/share/quarto/bin:$PATH"

# 4. Verify
uv run pytest -q       # → 23 passed
uv run ruff check .    # → All checks passed
make render            # → renders to _site/
```

The Makefile encodes the Quarto path via `QUARTO_BIN := $(HOME)/.local/share/quarto/bin`, so `make` targets work even if the binary isn't on the global `PATH`.

---

## 3. Commit history & what each commit means

22 commits since the plan landed, organized by task. Each `feat(...)` is verbatim spec; each `fix(...)` is a follow-up addressing a real issue surfaced by the two-stage review.

```
09b3300 chore: replace identity placeholders with omeg4 (and add repo-url for code-tools)
bc9840e chore(phase-0): hygiene fixes from final review
b0bf424 ci: render Quarto and deploy to Netlify on push to main          ← T14
e48ee43 fix(site): scope render to project content and use venv python
ef84848 post(notes): publication 1 — building a personal NHL warehouse   ← T13
38490a2 feat(site): notes + projects listing pages                       ← T12
3f2dbfe chore: add Quarto-generated .gitignore entries
35d0387 feat(site): scaffold Quarto site (home + about)                  ← T11
63e1a3d docs(data): document raw + mart schemas                          ← T10
d37f69b chore: remove accidental warehouse.duckdb from tracking, add *.duckdb to .gitignore
3b0820d fix(lint): resolve pre-existing ruff issues (UP035 + I001)
831a439 feat(pipeline): end-to-end warehouse build via make data         ← T9
56dad97 feat(mart): mart.shots_per_game from raw.moneypuck_shots         ← T8
7f50a20 fix(ingest): atomic DELETE+INSERT for moneypuck_shots load
1a96e77 feat(ingest): MoneyPuck shots loader (season-replace semantics)  ← T7
6d27b56 feat(ingest): NHL schedule into raw.schedule (idempotent)        ← T6
b480514 test(viz): assert real rcParam changes and prop_cycle order
f53ce30 feat(viz): house chart style + palette                           ← T5
847a28a fix(stats): per_60_column matches scalar semantics on negative TOI
83fe592 feat(stats): per-60 rate helper (scalar + DataFrame)             ← T4
69b5c3a feat(data): warehouse connection + schema bootstrap helpers      ← T3
783d56b feat(pkg): scaffold devilishdash package and smoke test          ← T2
15304b0 chore: add project metadata and uv-managed deps                  ← T1
```

---

## 4. Adaptations from the plan (and why)

The plan was followed verbatim except for these intentional changes. They're all documented in commit messages too, but worth surfacing in one place:

### Code changes flagged by mid-flight review

| Commit | Module | Why |
|---|---|---|
| `847a28a` | `devilishdash/stats.py` | Scalar `per_60` raises `ValueError` on negative TOI; vectorised `per_60_column` silently returned `NaN`. The docstring claimed vectorised parity. Fixed to match scalar semantics + added test. |
| `b480514` | `tests/test_viz.py` | Original `test_set_house_style_changes_rcParams` always passed via an `or`-fallback — its primary `before != after` assertion was dead code because both branches set `font.family` to the same value. Tightened to assert real changes + added a `prop_cycle` test. |
| `7f50a20` | `data/ingest/moneypuck_shots.py` | `load_shots` ran `DELETE` then `INSERT` in separate auto-committed transactions. If `INSERT` failed (corrupt CSV, schema mismatch), the season's rows were gone with no rollback. Wrapped in explicit `BEGIN`/`COMMIT`/`ROLLBACK` + added cross-season isolation test. |

### Real-world adaptations during ingest

| Module | Change | Why |
|---|---|---|
| `data/ingest/nhl_schedule.py` | `g.get("gameDate", day_date)` fallback | The real NHL API doesn't include `gameDate` on game objects — only on the parent day. The plan's mocked fixture had `gameDate`, but the live API doesn't. Defensive fallback works for both. |
| `data/ingest/nhl_schedule.py` | `ON CONFLICT ... DO UPDATE SET fetched_at = now()` (not `CURRENT_TIMESTAMP`) | DuckDB 1.5.x parses `CURRENT_TIMESTAMP` as an identifier (not a function) in `UPDATE SET` clauses. `now()` works. The DDL's `DEFAULT CURRENT_TIMESTAMP` is unchanged because DDL context doesn't have this quirk. |

### Site / deployment adaptations

| Commit | Change | Why |
|---|---|---|
| `d37f69b` | Added `*.duckdb` and `*.duckdb.wal` to `.gitignore` | The plan said "warehouse tracked", but the file is large, grows with every ingest, and is regenerable via `make data`. Better to keep it out of git. |
| `e48ee43` | `_quarto.yml` `render:` allow-list + Makefile `uv run quarto` | Quarto whole-site render tried to render `docs/superpowers/plans/...md` because it contains `{python}` blocks (real Python snippets in the plan doc, intended as docs). Now Quarto only renders project content. Also: Quarto's Jupyter kernel wasn't using the venv Python, so `import devilishdash` failed. Invoking via `uv run quarto` makes the venv active. |
| `bc9840e` | Created empty `custom.scss` and `styles.css`; removed unused `nhl-api-py` dep; added `data/cache/` to `.gitignore` | Hygiene fixes from the final review. The two CSS files silence Quarto's "theme file not found" warnings; the dep was declared but never imported; the cache dir is regenerable. |
| `09b3300` | Replaced `<your-github-username>` etc. with `omeg4`; added `repo-url` under `website:` | Identity sweep before push. The `repo-url` activates the `code-tools: true` dropdown's "View source" link. No Twitter (per your call). |

### T13 chart fallback (publication 1)

The plan's warehouse-stack note had an embedded Python chart querying `mart.shots_per_game`. That mart only exists if `make data` succeeded — and MoneyPuck's URL currently 404s. The chart was wrapped in `try/except duckdb.CatalogException`:

```python
try:
    df = con.execute("SELECT ... FROM mart.shots_per_game ...").df()
except duckdb.CatalogException:
    df = pd.DataFrame(columns=["team", "shots_per_game"])
finally:
    con.close()

if df.empty:
    fig, ax = plt.subplots(figsize=(8, 1.2))
    ax.text(0.5, 0.5,
        "MoneyPuck source unavailable — chart will populate after the next data refresh.",
        ...)
    ax.axis("off")
else:
    # original bar chart
```

When MoneyPuck is back (or you point at a working URL), the chart will auto-populate on the next `make render`.

---

## 5. Known limitations & deferred items

### MoneyPuck URL is 404

The plan's URL `https://peter-tanner.com/moneypuck/downloads/shots_{season}.csv` returns 404 for both 2023 and 2024 seasons as of 2026-05-11. The schedule loader works fine (NHL API is healthy; T9 smoke-test ingested 1404 schedule rows for 2023). Workarounds in place:

1. **CI is gated off** — `.github/workflows/deploy.yml` step "Build the warehouse" has `if: ${{ false }}` so the workflow doesn't fail on the 404. Flip back to enabled when there's a working URL.
2. **The note's chart falls back gracefully** — see T13 fallback above.

**Phase 1 task:** investigate alternative URLs. MoneyPuck's downloads page (https://moneypuck.com/data.htm) probably has the current canonical link. The loader's URL constant `MONEYPUCK_SHOT_CSV_URL` is the one place to update.

### Forward-referenced files that don't exist yet

- `projects/index.qmd` has an empty listing (`contents: "*/index.qmd"` matches nothing) — first project lands in Phase 1.
- `custom.scss` and `styles.css` are empty placeholders — Phase 1 will style the site.

### `clean.*` schema is empty

`data.ensure_schemas` creates `raw`, `clean`, and `mart`. Only `raw.*` and `mart.*` have tables; `clean.*` is reserved for Phase 1 (deduped/joined surfaces).

### What's not tested

- The `run_all.py` orchestrator — by design (thin shell over already-tested helpers).
- The Quarto render itself — the note's fallback path is exercised by an actual render in `make render`, which is the smoke test.
- The end-to-end ingest happy path against live sources — would require network + working MoneyPuck.

---

## 6. T15 — Netlify + domain (your hands)

These steps require your involvement: external accounts, payment, DNS. Roughly 30–60 minutes of work.

### Step 1: Push to GitHub

The repo is currently local-only. The `gh` CLI is installed but the saved token is invalid. Re-authenticate:

```bash
gh auth login -h github.com
```

Pick:
- Account: GitHub.com
- Protocol: HTTPS (or SSH if you have keys set up)
- Auth method: Login with a web browser (paste the device code into the URL it gives you)

Then create the public repo and push everything:

```bash
cd /home/bruno/devilishdash
gh repo create omeg4/devilishdash --public --source=. --remote=origin --push
```

Verify:
```bash
gh repo view --web    # opens the live GitHub repo in your browser
```

You should see all 23 commits, the README, and the Actions tab. The Actions workflow will trigger automatically on this first push — it will install uv, Python, Quarto, render the site, then **fail at the Netlify deploy step** because the secrets don't exist yet. That's the expected state until Step 4 below.

### Step 2: Netlify signup + connect repo

1. Go to https://app.netlify.com/signup. Use the email `matthew.brunetti28@gmail.com`. Sign in via GitHub for the lowest-friction setup.
2. Once logged in: **Sites** → **Add new site** → **Import an existing project** → **Deploy with GitHub** → pick `omeg4/devilishdash`.
3. **Build settings** (when prompted):
   - **Build command:** leave blank. (GitHub Actions runs the build; Netlify just hosts.)
   - **Publish directory:** `_site`
   - **Branch to deploy:** `main`
4. Click **Deploy site**. Netlify will do a default build to validate the publish dir. Since the build command is blank and `_site/` doesn't exist on a fresh checkout, this first deploy will fail — that's OK; it just registers the site.

### Step 3: Get the auth token + site ID

Two values you need to copy:

**Auth token (personal access token):**
1. Netlify top-right **Avatar** → **User settings** → **Applications** → **Personal access tokens**
2. **New access token** → name it "GitHub Actions deploy"
3. Copy the token immediately — Netlify won't show it again. Treat it like a password.

**Site ID (a.k.a. API ID):**
1. From Netlify dashboard, click the site you just created
2. **Site configuration** → **General** → "Site information"
3. Copy the **API ID** (it looks like a UUID, e.g. `12345678-90ab-cdef-1234-567890abcdef`)

### Step 4: Add the secrets to GitHub

```bash
# Easiest: use the gh CLI
cd /home/bruno/devilishdash
gh secret set NETLIFY_AUTH_TOKEN     # paste the token when prompted
gh secret set NETLIFY_SITE_ID        # paste the API ID when prompted
```

Or via the web UI: `https://github.com/omeg4/devilishdash/settings/secrets/actions` → **New repository secret** for each.

### Step 5: Trigger a deploy and verify

Either push a tiny change, or trigger manually:

```bash
gh workflow run "Deploy site"
gh run watch                          # tails the latest run
```

Watch the steps execute: checkout → install uv → setup Python → uv sync → setup Quarto → render → deploy to Netlify. The deploy step should now succeed and report a Netlify URL like `https://<random-name>.netlify.app`.

Open the URL. Verify:
- Home page loads
- Nav links work (Home / Projects / Notes / About)
- Notes listing shows the warehouse-stack post
- The warehouse-stack page renders with the "MoneyPuck source unavailable" fallback figure

### Step 6: Buy a custom domain

Recommended candidates: `mattbrunetti.com`, `matthewbrunetti.com`, `mbrunetti.dev`, `brunetti.dev`. Roughly $12/year at any registrar.

Suggested registrars (by preference):
- **Cloudflare Registrar** — at-cost pricing, no markup, no upsells. Requires a Cloudflare account.
- **Porkbun** — cheap, good UX.
- **Namecheap** — competitive pricing.

Avoid GoDaddy (overpriced, aggressive upsells) unless you already have an account there.

### Step 7: Configure DNS in Netlify

1. Netlify site → **Domain management** → **Add a domain** → enter your purchased domain
2. Netlify will show you DNS records to add at your registrar. Typically:
   - **Apex (e.g. `mattbrunetti.com`):** A record → Netlify's load-balancer IP (Netlify gives you the exact IP)
   - **www subdomain:** CNAME → `<your-site>.netlify.app`
3. Add those records at your registrar's DNS settings page. Propagation usually takes 5–60 minutes.

### Step 8: Enable HTTPS

1. Once Netlify verifies DNS, the **Domain management** page shows **HTTPS** → **Verify DNS configuration**
2. Click **Provision certificate** (uses Let's Encrypt, free, auto-renewing)
3. Wait ~5 minutes for the cert to issue
4. Toggle **Force HTTPS** to on

### Step 9: Verify the live site

Open your custom domain in a browser. Confirm:
- HTTPS lock icon
- Home / Projects / Notes / About all load
- Warehouse-stack note renders
- No 404s on internal links

### Step 10: Update the live URL

Edit two files:

**`README.md`** — replace:
```
Live site: TBD (Netlify URL until custom domain is configured)
```
with:
```
Live site: https://<your-domain>
```

**`about.qmd`** — already has your GitHub link. No other identity changes needed.

Then commit and push:

```bash
git add README.md
git commit -m "docs: set live URL"
git push
```

The site auto-redeploys via GitHub Actions.

---

## 7. T16 — Phase 0 reading list

Non-code. On your own time, before Phase 1 starts. Plan task T16 has the canon — repeated here for convenience:

- [ ] **Tulsky's Corsi era essays** — search "Eric Tulsky Corsi" on Broad Street Hockey or his old blog. Aim for 3 essays. Take notes.
- [ ] **Andrew Thomas's xG paper** — *A New Way to Look at Hockey* / "Inferring Shot Quality". Free PDF online.
- [ ] **Evolving-Hockey RAPM methodology** — full methodology doc on evolving-hockey.com. You won't follow all the math; that's fine.
- [ ] **HockeyViz "About / Methodology" pages** — what Micah publishes about how he builds his charts.
- [ ] **Schuckers's papers on player evaluation** — search "Schuckers TOI60 plus minus" on SSRN or Google Scholar. Read at least one.
- [ ] **Optional follow-up Note** — "Five papers I read this month" if anything sparks something specific. Good for site activity.

---

## 8. What Phase 1 starts on

Once T15 lands the live site at a real URL and you've done a pass through T16's reading, Phase 1 kicks off the Devils injury-recovery study:

- ~8–10 weeks of work
- Lives at `projects/devils-injury-study/index.qmd`
- Depends on triangulating injury data from PuckPedia + DailyFaceoff + beat-reporter notes + ManGamesLost (since the NHL has no public injury API)
- Spec section 4 Phase 1 has the scope

The foundation laid in Phase 0 makes Phase 1 mostly additive: new ingest scripts, new marts in `mart.*`, a new project under `projects/`, more sophisticated helpers in `devilishdash.stats` (rolling means, bootstrapped CIs). No architectural rework needed.

---

## Appendix A: Useful one-liners

```bash
# Run the test suite
make test
# or: uv run pytest -q

# Lint & format
make lint
# or: uv run ruff check . && uv run ruff format --check .

# Rebuild the warehouse (will fail at MoneyPuck step today; that's known)
make data

# Render the site locally
make render
# Open _site/index.html in a browser to preview

# Live-reload preview while editing
make preview

# Clean rebuild artifacts (keeps warehouse.duckdb)
make clean

# Verify the venv has devilishdash editable-installed
uv run python -c "import devilishdash; print(devilishdash.__file__)"
# Should print: .../devilishdash/devilishdash/__init__.py
```

## Appendix B: If `make render` fails on a fresh machine

The most likely culprits:
1. **Quarto not on PATH** — verify with `which quarto`. The Makefile prepends `$HOME/.local/share/quarto/bin` automatically, but if you put Quarto somewhere else, edit `QUARTO_BIN` in the Makefile.
2. **`import devilishdash` fails inside Quarto's Python kernel** — re-run `uv sync --extra dev` from the repo root. This rewrites the editable-install `.pth` file with absolute paths.
3. **`docs/` files leak into the render** — verify `_quarto.yml`'s `render:` block has only `*.qmd`, `notes/**/*.qmd`, `projects/**/*.qmd`. If something else got added there by accident, `docs/` content will start rendering as part of the site.
