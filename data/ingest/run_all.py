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
