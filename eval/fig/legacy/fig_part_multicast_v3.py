"""Multicast time (v3, horizontal): three N panels side by side, grouped bars
(MHcast/Spectrum/Express), log y. One y-axis label on the leftmost panel.
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
    [5.145846, 5.864128, 6.509374, 5.821873, 5.858455],
    [34.116021, 32.876273, 34.989534, 34.332863, 34.589337],
    [244.733407, 245.970701, 244.979463, 245.961906, 246.010341],
]
spectrum_ys = [
    np.array([23.527587, 24.157152 * 2, 23.901477 * 4, 23.110163 * 8, 23.902056 * 16]) / 16,
    np.array([208.304942, 208.400053 * 2, 215.018723 * 4, 236.54003 * 8, 212.549999 * 16]) / 16,
    np.array([1.496008509 * 1000, 1.655254209 * 1000 * 2, 1.599455261 * 1000 * 4, 1.488166033 * 1000 * 8, 1.466206667 * 1000 * 16]) / 16,
]
express_ys = [
    [36.253436, 39.34214 * 2, 41.43044 * 4, 36.045401 * 8, 35.520358 * 16],
    [351.153192, 346.862686 * 2, 353.569257 * 4, 354.358528 * 8, 344.530103 * 16],
    [4.313930804 * 1000, 4.490653314 * 1000 * 2, 4.598824788 * 1000 * 4, 4.613637511 * 1000 * 8, 4.840407418 * 1000 * 16],
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

axes[0].set_ylabel("Multicast time (sec)")
axes[1].set_xlabel("Recipient group size")

plt.tight_layout(rect=(0, 0.07, 1, 1))

order = ["MHcast", "Spectrum", "Express"]
handles, labels = axes[0].get_legend_handles_labels()
hl = dict(zip(labels, handles))
leg = fig.legend([hl[n] for n in order], order, loc="lower center",
                 bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=14,
                 frameon=True, edgecolor="#cccccc", framealpha=0.92)

out = OUT_DIR / "part_multicast.pdf"
fig.savefig(out, bbox_inches="tight", bbox_extra_artists=[leg])
print(f"wrote {out}")
