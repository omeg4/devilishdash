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
