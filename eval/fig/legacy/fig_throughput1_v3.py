"""GOMR throughput comparison (v3, horizontal): three N panels side by side.
One y-axis label (on the leftmost panel); per-panel y ranges/ticks are not
aligned. Sized for a two-column-spanning figure*.
"""

import figstyle as fs
import matplotlib.pyplot as plt
from pathlib import Path

fs.init(16)
OUT_DIR = Path(__file__).resolve().parent

N_exp = [11, 14, 17]
xs = [2 ** x for x in range(0, 5)]
mhcast_ys = [
    [28.4949, 26.9795, 26.5879, 26.8002, 27.4412],
    [3.77788, 3.79738, 3.75746, 3.76584, 3.75427],
    [0.481027, 0.479917, 0.479928, 0.480021, 0.479739],
]
agomr_ys = [[4.25947, 4.76395, 4.75736, 3.97306, 4.38208]] * 3
fgomr_ys = [[6.48283, 5.601985, 5.63000, 6.39458, 6.21391]] * 3
ymax = [31.0, 7.2, 7.2]

fig, axes = plt.subplots(1, 3, figsize=(11, 3.3))
for i, ax in enumerate(axes):
    ax.set_xscale("log", base=2)
    ax.set_xticks(xs)
    ax.set_xlim(xs[0] / 1.6, xs[-1] * 1.6)
    ax.set_ylim(0, ymax[i])
    ax.locator_params(axis="y", nbins=4)
    ax.set_title(f"$N = 2^{{{N_exp[i]}}}$", fontsize=15)
    fs.plot_line(ax, xs, agomr_ys[i], "AGOMR", label="AGOMR (1 group)")
    fs.plot_line(ax, xs, fgomr_ys[i], "FGOMR", label="FGOMR (1 group)")
    fs.plot_line(ax, xs, mhcast_ys[i], "MHcast")  # hero on top

axes[0].set_ylabel("Throughput (msgs/sec)")
axes[1].set_xlabel("Recipient group size")

plt.tight_layout(rect=(0, 0.07, 1, 1))

order = ["MHcast", "AGOMR (1 group)", "FGOMR (1 group)"]
handles, labels = axes[0].get_legend_handles_labels()
hl = dict(zip(labels, handles))
leg = fig.legend([hl[n] for n in order], order, loc="lower center",
                 bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=14,
                 frameon=True, edgecolor="#cccccc", framealpha=0.92)

out = OUT_DIR / "throughput1.pdf"
fig.savefig(out, bbox_inches="tight", bbox_extra_artists=[leg])
print(f"wrote {out}")
