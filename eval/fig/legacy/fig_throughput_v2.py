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
spectrum_ys = [
    [32.2969, 16.1484, 8.07422, 4.03711, 2.01856],
    [4.04097, 2.02048, 1.01024, 0.50512, 0.25256],
    [0.503336, 0.251668, 0.125834, 0.0629170, 0.0314585],
]
express_ys = [
    [6.14968, 3.07484, 1.53742, 0.76871, 0.384355],
    [5.84967, 2.92484, 1.46242, 0.73121, 0.365604],
    [3.39979, 1.69990, 0.84995, 0.42497, 0.212487],
]
talek_ys = [
    [2.39263] * 5,
    [0.0285111] * 5,
    [0.000448418] * 5,
]

# Start each panel at 0 so the flat MHcast line and the decaying baselines are
# read on a common, honest baseline.
ymax = [34.0, 6.4, 3.7]

fig = plt.figure(figsize=(4.5, 7.7))
for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_xscale("log", base=2)
    ax.set_xticks(xs)
    ax.set_ylim(0, ymax[i])
    ax.locator_params(axis="y", nbins=4)
    ax.set_ylabel("Throughput\n(msgs/sec)")
    ax.set_title(f"$N = 2^{{{11 + i * 3}}}$", fontsize=16)
    fs.plot_line(ax, xs, spectrum_ys[i], "Spectrum")
    fs.plot_line(ax, xs, express_ys[i], "Express")
    fs.plot_line(ax, xs, talek_ys[i], "Talek")
    fs.plot_line(ax, xs, mhcast_ys[i], "MHcast")  # hero drawn last (on top)

plt.xlabel("Recipient group size")
fs.ordered_legend(
    fig.axes[-1], ["MHcast", "Spectrum", "Express", "Talek"],
    loc="lower center", bbox_to_anchor=(0.5, -1.12), ncol=2, fontsize=15,
)
plt.tight_layout(pad=0.2)
plt.gcf().savefig(OUT_DIR / "throughput.pdf", bbox_inches="tight")
