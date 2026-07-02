"""Access control time (v3, horizontal): three N panels side by side, grouped
bars (MHcast/Spectrum/Express), log y. One y-axis label on the leftmost panel.
Sized for a two-column-spanning figure*.
"""

import figstyle as fs
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

fs.init(16)
OUT_DIR = Path(__file__).resolve().parent

N_exp = [11, 14, 17]
xs = np.array([2 ** x for x in range(0, 5)])
x_labels = [str(x) for x in xs]
x_pos = np.arange(len(xs))

mhcast_ys = [
    [29.659673, 30.950221, 30.851648, 31.210384, 30.326905],
    [230.31795, 230.194412, 230.862869, 230.944989, 231.485136],
    [1.833815127 * 1000, 1.837374709 * 1000, 1.838322443 * 1000, 1.836929155 * 1000, 1.838118125 * 1000],
]
spectrum_ys = [
    np.array([554.991303, 556.488653 * 2, 555.23022 * 4, 555.514761 * 8, 563.569438 * 16]) / 16,
    np.array([3.681384067 * 1000, 3.666200507 * 1000 * 2, 3.669299073 * 1000 * 4, 3.665820202 * 1000 * 8, 3.668039065 * 1000 * 16]) / 16,
    np.array([28.641998771 * 1000, 28.557677269 * 1000 * 2, 28.650189558 * 1000 * 4, 28.637425566 * 1000 * 8, 28.572164332 * 1000 * 16]) / 16,
]
express_ys = [
    [226.217987 - 108, 223.315432 * 2, 221.775604 * 4, 229.574951 * 8, 228.824117 * 16],
    [(107.895071 + 108), (108.356588 + 108) * 2, (106.856553 + 108) * 4, (109.616877 + 108) * 8, (108.296005 + 108) * 16],
    [(121.377388 + 108), (119.952944 + 108) * 2, (119.277318 + 108) * 4, (118.946191 + 108) * 8, (117.753241 + 108) * 16],
]

mhcast_ys = [np.array(y) / 1000 for y in mhcast_ys]
spectrum_ys = [np.array(y) / 1000 for y in spectrum_ys]
express_ys = [np.array(y) / 1000 for y in express_ys]
bars = [("MHcast", mhcast_ys), ("Spectrum", spectrum_ys), ("Express", express_ys)]

fig, axes = plt.subplots(1, 3, figsize=(11, 3.3))
width = 0.5
for i, ax in enumerate(axes):
    ax.set_yscale("log", base=10)
    ax.set_xticks(x_pos, labels=x_labels)
    ax.grid(True, axis="y", which="major", color=fs.GRID, linewidth=0.6)
    ax.grid(True, axis="y", which="minor", color="#f3f3f3", linewidth=0.4)
    ax.grid(False, axis="x")
    for k, (name, data) in enumerate(bars):
        ax.bar(x_pos + (k - 1) * width / 2, data[i] / 1000, width / 2,
               label=name, color=fs.COLORS[name], edgecolor="white", linewidth=0.4)
    ax.set_title(f"$N = 2^{{{N_exp[i]}}}$", fontsize=15)

axes[0].set_ylabel("Access control time (sec)")
axes[1].set_xlabel("Recipient group size")

plt.tight_layout(rect=(0, 0.07, 1, 1))

order = ["MHcast", "Spectrum", "Express"]
handles, labels = axes[0].get_legend_handles_labels()
hl = dict(zip(labels, handles))
leg = fig.legend([hl[n] for n in order], order, loc="lower center",
                 bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=14,
                 frameon=True, edgecolor="#cccccc", framealpha=0.92)

out = OUT_DIR / "part_access_control.pdf"
fig.savefig(out, bbox_inches="tight", bbox_extra_artists=[leg])
print(f"wrote {out}")
