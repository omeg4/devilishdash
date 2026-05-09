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
