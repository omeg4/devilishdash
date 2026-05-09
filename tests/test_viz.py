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
