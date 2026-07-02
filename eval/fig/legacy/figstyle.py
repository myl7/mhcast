"""Shared publication-quality style for MHcast evaluation figures.

Goal: a single coherent visual language across every figure (consistent
palette, markers, thin frame, light grid, legend styling) following the
matplotlib `simple_white` aesthetic. Keeps the original LaTeX/usetex setup so
the text matches the rest of the paper.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Unified, print-friendly palette. Each system keeps the SAME color+marker in
# every figure so the reader builds one mental legend. MHcast is the hero line.
COLORS = {
    "MHcast": "#F03E3E",    # red (our system)
    "Spectrum": "#1C7ED6",  # blue
    "Express": "#2F9E44",   # green
    "Talek": "#F59F00",     # amber
    "AGOMR": "#7048E8",     # violet
    "FGOMR": "#E8590C",     # orange
    "DCF": "#F03E3E",       # DCF == MHcast's primitive
    "DPF": "#2F9E44",       # DPF == Express's primitive
}
MARKERS = {
    "MHcast": "x", "Spectrum": "o", "Express": "s",
    "Talek": "^", "AGOMR": "D", "FGOMR": "P",
    "DCF": "x", "DPF": "s",
}

GRID = "#e4e4e4"
FRAME = "#333333"


def init(size=17):
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "Times New Roman",
        "font.size": size,
        "axes.edgecolor": FRAME,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": FRAME,
        "ytick.color": FRAME,
        "xtick.labelcolor": "black",
        "ytick.labelcolor": "black",
        "legend.frameon": True,
        "legend.framealpha": 0.92,
        "legend.edgecolor": "#cccccc",
        "legend.fancybox": False,
        "legend.borderpad": 0.4,
        "legend.handlelength": 1.6,
        "legend.columnspacing": 1.1,
    })


def plot_line(ax, xs, ys, name, label=None, **kw):
    """Plot one series with the unified per-system style."""
    marker = MARKERS[name]
    color = COLORS[name]
    hero = name == "MHcast"
    if marker == "x":
        mec, mew = color, 1.8
    else:
        mec, mew = "white", 0.7
    return ax.plot(
        xs, ys,
        label=name if label is None else label,
        color=color, marker=marker, markersize=6.5,
        markeredgecolor=mec, markeredgewidth=mew,
        linewidth=2.2 if hero else 1.7,
        zorder=6 if hero else 3,
        **kw,
    )


def ordered_legend(ax, order, **kw):
    """Build a legend on `ax` with series forced into `order`."""
    handles, labels = ax.get_legend_handles_labels()
    idx = [labels.index(n) for n in order]
    return ax.legend([handles[i] for i in idx], [labels[i] for i in idx], **kw)
