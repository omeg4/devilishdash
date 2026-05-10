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
    df = pd.DataFrame({"goals": [1, 2, 0, 5], "toi_seconds": [600, 1800, 0, 0]})
    out = stats.per_60_column(df, events_col="goals", toi_col="toi_seconds")
    # 1/600s = 6/hr ; 2/1800s = 4/hr ; 0/0s and 5/0s = NaN (mask must fire)
    assert out.iloc[0] == pytest.approx(6.0)
    assert out.iloc[1] == pytest.approx(4.0)
    assert math.isnan(out.iloc[2])
    assert math.isnan(out.iloc[3])


def test_per_60_column_negative_toi_raises():
    df = pd.DataFrame({"goals": [1, 2], "toi_seconds": [600, -1]})
    with pytest.raises(ValueError):
        stats.per_60_column(df, events_col="goals", toi_col="toi_seconds")
