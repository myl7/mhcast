"""Part time (v3, horizontal, combined): 2 rows x 3 N columns. Top row =
multicast time, bottom row = access control time. Grouped bars
(MHcast/Spectrum/Express), log y. Per-row y-axis label; shared x-axis label and
a single legend. Sized for a two-column-spanning figure*.
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

# --- Multicast time (us, before scaling) ---
mc_mhcast = [
    [5.145846, 5.864128, 6.509374, 5.821873, 5.858455],
    [34.116021, 32.876273, 34.989534, 34.332863, 34.589337],
    [244.733407, 245.970701, 244.979463, 245.961906, 246.010341],
]
mc_spectrum = [
    np.array([23.527587, 24.157152 * 2, 23.901477 * 4, 23.110163 * 8, 23.902056 * 16]) / 16,
    np.array([208.304942, 208.400053 * 2, 215.018723 * 4, 236.54003 * 8, 212.549999 * 16]) / 16,
    np.array([1.496008509 * 1000, 1.655254209 * 1000 * 2, 1.599455261 * 1000 * 4, 1.488166033 * 1000 * 8, 1.466206667 * 1000 * 16]) / 16,
]
mc_express = [
    [36.253436, 39.34214 * 2, 41.43044 * 4, 36.045401 * 8, 35.520358 * 16],
    [351.153192, 346.862686 * 2, 353.569257 * 4, 354.358528 * 8, 344.530103 * 16],
    [4.313930804 * 1000, 4.490653314 * 1000 * 2, 4.598824788 * 1000 * 4, 4.613637511 * 1000 * 8, 4.840407418 * 1000 * 16],
]

# --- Access control time (us, before scaling) ---
ac_mhcast = [
    [29.659673, 30.950221, 30.851648, 31.210384, 30.326905],
    [230.31795, 230.194412, 230.862869, 230.944989, 231.485136],
    [1.833815127 * 1000, 1.837374709 * 1000, 1.838322443 * 1000, 1.836929155 * 1000, 1.838118125 * 1000],
]
ac_spectrum = [
    np.array([554.991303, 556.488653 * 2, 555.23022 * 4, 555.514761 * 8, 563.569438 * 16]) / 16,
    np.array([3.681384067 * 1000, 3.666200507 * 1000 * 2, 3.669299073 * 1000 * 4, 3.665820202 * 1000 * 8, 3.668039065 * 1000 * 16]) / 16,
    np.array([28.641998771 * 1000, 28.557677269 * 1000 * 2, 28.650189558 * 1000 * 4, 28.637425566 * 1000 * 8, 28.572164332 * 1000 * 16]) / 16,
]
ac_express = [
    [226.217987 - 108, 223.315432 * 2, 221.775604 * 4, 229.574951 * 8, 228.824117 * 16],
    [(107.895071 + 108), (108.356588 + 108) * 2, (106.856553 + 108) * 4, (109.616877 + 108) * 8, (108.296005 + 108) * 16],
    [(121.377388 + 108), (119.952944 + 108) * 2, (119.277318 + 108) * 4, (118.946191 + 108) * 8, (117.753241 + 108) * 16],
]


def scale(rows):
    return [np.array(y) / 1e6 for y in rows]


rows = [
    ("Multicast\ntime (sec)", scale(mc_mhcast), scale(mc_spectrum), scale(mc_express)),
    ("Access control\ntime (sec)", scale(ac_mhcast), scale(ac_spectrum), scale(ac_express)),
]

fig, axes = plt.subplots(2, 3, figsize=(11, 5.4))
width = 0.5
for r, (ylab, mh, sp, ex) in enumerate(rows):
    bars = [("MHcast", mh), ("Spectrum", sp), ("Express", ex)]
    for j in range(3):
        ax = axes[r][j]
        ax.set_yscale("log", base=10)
        ax.set_xticks(x_pos, labels=(x_labels if r == 1 else [""] * len(xs)))
        ax.grid(True, axis="y", which="major", color=fs.GRID, linewidth=0.6)
        ax.grid(True, axis="y", which="minor", color="#f3f3f3", linewidth=0.4)
        ax.grid(False, axis="x")
        for k, (name, data) in enumerate(bars):
            ax.bar(x_pos + (k - 1) * width / 2, data[j], width / 2,
                   label=name, color=fs.COLORS[name], edgecolor="white", linewidth=0.4)
        if r == 0:
            ax.set_title(f"$N = 2^{{{N_exp[j]}}}$", fontsize=15)
    axes[r][0].set_ylabel(ylab)

axes[1][1].set_xlabel("Recipient group size")

plt.tight_layout(rect=(0, 0.06, 1, 1))

order = ["MHcast", "Spectrum", "Express"]
handles, labels = axes[0][0].get_legend_handles_labels()
hl = dict(zip(labels, handles))
leg = fig.legend([hl[n] for n in order], order, loc="lower center",
                 bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=14,
                 frameon=True, edgecolor="#cccccc", framealpha=0.92)

out = OUT_DIR / "part_time.pdf"
fig.savefig(out, bbox_inches="tight", bbox_extra_artists=[leg])
print(f"wrote {out}")
