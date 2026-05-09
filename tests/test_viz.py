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
    assert plt.rcParams["axes.grid"] is False  # baseline
    viz.set_house_style()
    assert plt.rcParams["axes.grid"] is True
    assert plt.rcParams["axes.spines.top"] is False
    assert plt.rcParams["axes.spines.right"] is False
    assert plt.rcParams["font.size"] == 11


def test_set_house_style_is_idempotent():
    viz.set_house_style()
    viz.set_house_style()  # should not raise
    assert plt.rcParams["axes.spines.top"] is False


def test_set_house_style_sets_prop_cycle_to_palette_colors():
    viz.set_house_style()
    cycle_colors = [d["color"] for d in plt.rcParams["axes.prop_cycle"]]
    assert cycle_colors == [
        viz.HOUSE_PALETTE["accent"],
        viz.HOUSE_PALETTE["muted"],
        viz.HOUSE_PALETTE["good"],
        viz.HOUSE_PALETTE["bad"],
    ]
