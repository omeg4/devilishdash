"""House chart style — single source of truth for the site's visual identity."""

from __future__ import annotations

import matplotlib.pyplot as plt

# Deliberately not Devils red — see spec section 9 (brand should not be team-locked).
HOUSE_PALETTE: dict[str, str] = {
    "accent": "#0a6cf5",   # primary accent (blue)
    "muted":  "#9aa5b1",   # secondary lines / annotations
    "ink":    "#0e1014",   # text + axis lines
    "paper":  "#ffffff",   # page background
    "good":   "#1f8a4c",   # positive deltas
    "bad":    "#c0392b",   # negative deltas
}


def set_house_style() -> None:
    """Apply the project's chart style to global matplotlib rcParams."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": HOUSE_PALETTE["ink"],
        "axes.labelcolor": HOUSE_PALETTE["ink"],
        "axes.titlesize": 13,
        "axes.titleweight": "semibold",
        "xtick.color": HOUSE_PALETTE["ink"],
        "ytick.color": HOUSE_PALETTE["ink"],
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "figure.facecolor": HOUSE_PALETTE["paper"],
        "axes.facecolor": HOUSE_PALETTE["paper"],
        "axes.prop_cycle": plt.cycler(
            color=[HOUSE_PALETTE["accent"], HOUSE_PALETTE["muted"],
                   HOUSE_PALETTE["good"], HOUSE_PALETTE["bad"]]
        ),
    })
