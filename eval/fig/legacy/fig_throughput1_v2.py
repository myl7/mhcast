from pathlib import Path

import figstyle as fs
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent

fs.init(17)

xs = [2**x for x in range(0, 5)]
mhcast_ys = [
    [28.4949, 26.9795, 26.5879, 26.8002, 27.4412],
    [3.77788, 3.79738, 3.75746, 3.76584, 3.75427],
    [0.481027, 0.479917, 0.479928, 0.480021, 0.479739],
]
agomr_ys = [[4.25947, 4.76395, 4.75736, 3.97306, 4.38208]] * 3
fgomr_ys = [[6.48283, 5.601985, 5.63000, 6.39458, 6.21391]] * 3

# Start at 0 and include the MHcast line (previously clipped at the top of the
# first panel) so all three systems are visible on every panel.
ymax = [31.0, 7.2, 7.2]

fig = plt.figure(figsize=(4.5, 7.7))
for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_xscale("log", base=2)
    ax.set_xticks(xs)
    ax.set_ylim(0, ymax[i])
    ax.locator_params(axis="y", nbins=4)
    ax.set_ylabel("Throughput\n(msgs/sec)")
    ax.set_title(f"$N = 2^{{{11 + i * 3}}}$", fontsize=16)
    fs.plot_line(ax, xs, agomr_ys[i], "AGOMR", label="AGOMR (1 group)")
    fs.plot_line(ax, xs, fgomr_ys[i], "FGOMR", label="FGOMR (1 group)")
    fs.plot_line(ax, xs, mhcast_ys[i], "MHcast")  # hero drawn last (on top)

plt.xlabel("Recipient group size")
fs.ordered_legend(
    fig.axes[-1], ["MHcast", "AGOMR (1 group)", "FGOMR (1 group)"],
    loc="lower center", bbox_to_anchor=(0.5, -1.12), ncol=2, fontsize=15,
)
plt.tight_layout(pad=0.2)
plt.gcf().savefig(OUT_DIR / "throughput1.pdf", bbox_inches="tight")
