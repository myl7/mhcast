"""Throughput figure (v3, horizontal): three N groups side by side. Each group
has a broken x-axis: a wide left segment (3/4) with the full system comparison
at small groups, and a narrow right segment (1/4) with MHcast only at large
groups, separated by a wavy break. One y-axis label; per-group y ticks are not
aligned (each group keeps its own range and tick numbers). Sized for a
two-column-spanning figure*.
"""

import numpy as np
import figstyle as fs
import matplotlib.pyplot as plt
from pathlib import Path

fs.init(16)
OUT_DIR = Path(__file__).resolve().parent

N_exp = [11, 14, 17]
xs_small = [2 ** x for x in range(0, 5)]
xs_large = [
    [2 ** x for x in range(7, 12)],
    [2 ** x for x in range(10, 15)],
    [2 ** x for x in range(13, 18)],
]

mhcast_small = [
    [28.4949, 26.9795, 26.5879, 26.8002, 27.4412],
    [3.77788, 3.79738, 3.75746, 3.76584, 3.75427],
    [0.481027, 0.479917, 0.479928, 0.480021, 0.479739],
]
spectrum_small = [
    [32.2969, 16.1484, 8.07422, 4.03711, 2.01856],
    [4.04097, 2.02048, 1.01024, 0.50512, 0.25256],
    [0.503336, 0.251668, 0.125834, 0.0629170, 0.0314585],
]
express_small = [
    [6.14968, 3.07484, 1.53742, 0.76871, 0.384355],
    [5.84967, 2.92484, 1.46242, 0.73121, 0.365604],
    [3.39979, 1.69990, 0.84995, 0.42497, 0.212487],
]
talek_small = [
    [2.39263] * 5,
    [0.0285111] * 5,
    [0.000448418] * 5,
]
mhcast_large = [
    [1000 / v for v in (36.608278, 35.167111, 35.586771, 34.545813, 36.017361)],
    [1000 / v for v in (263.152232, 263.46868, 263.407839, 262.761382, 264.484196)],
    [1 / v for v in (2.082698943, 2.079641115, 2.081890343, 2.07949364, 2.081169384)],
]
ymax = [34.0, 6.4, 3.7]


def wavy(ax, xfrac, n=120, amp=0.04, ext=0.06):
    t = np.linspace(0, 1, n)
    yy = (t * 2 - 1) * ext
    xx = xfrac + amp * np.sin(t * np.pi * 4)
    ax.plot(xx, yy, transform=ax.transAxes, color=fs.FRAME,
            lw=1.1, clip_on=False, zorder=20)


fig = plt.figure(figsize=(12.5, 3.5))

L0, R0 = 0.055, 0.008   # outer margins (auto-cropped by tight bbox anyway)
b = 0.014               # break gap within a group
g = 0.060               # inter-group gap (room for the next group's y numbers)
bottom, top = 0.21, 0.84
H = top - bottom
P = (1 - L0 - R0 - 3 * b - 2 * g) / 3   # one group's plot width (left+right)
WL, WR = 0.75 * P, 0.25 * P

groups = []
for i in range(3):
    x0 = L0 + i * (P + b + g)
    axL = fig.add_axes([x0, bottom, WL, H])
    axR = fig.add_axes([x0 + WL + b, bottom, WR, H], sharey=axL)
    groups.append((axL, axR, x0))

    for ax in (axL, axR):
        ax.set_xscale("log", base=2)
        ax.set_ylim(0, ymax[i])
        ax.locator_params(axis="y", nbins=4)

    axL.set_xticks(xs_small)
    axL.set_xlim(xs_small[0] / 1.6, xs_small[-1] * 1.6)
    fs.plot_line(axL, xs_small, spectrum_small[i], "Spectrum")
    fs.plot_line(axL, xs_small, express_small[i], "Express")
    fs.plot_line(axL, xs_small, talek_small[i], "Talek")
    fs.plot_line(axL, xs_small, mhcast_small[i], "MHcast")

    axR.set_xticks([xs_large[i][0], xs_large[i][-1]])  # endpoints only (narrow segment)
    axR.set_xlim(xs_large[i][0] / 1.7, xs_large[i][-1] * 1.7)
    fs.plot_line(axR, xs_large[i], mhcast_large[i], "MHcast")

    axL.spines["right"].set_visible(False)
    axR.spines["left"].set_visible(False)
    axR.tick_params(left=False, labelleft=False)
    wavy(axL, 1.0)
    wavy(axR, 0.0)

    if i == 0:
        axL.set_ylabel("Throughput (msgs/sec)")
    fig.text(x0 + (WL + b + WR) / 2, top + 0.03, f"$N = 2^{{{N_exp[i]}}}$",
             ha="center", va="bottom", fontsize=15)

fig.text(0.5, 0.03, "Recipient group size", ha="center", va="bottom")

order = ["MHcast", "Spectrum", "Express", "Talek"]
handles, labels = groups[0][0].get_legend_handles_labels()
hl = dict(zip(labels, handles))
leg = fig.legend([hl[n] for n in order], order, loc="lower center",
                 bbox_to_anchor=(0.5, -0.14), ncol=4, fontsize=14,
                 frameon=True, edgecolor="#cccccc", framealpha=0.92)

out = OUT_DIR / "throughput_concat.pdf"
fig.savefig(out, bbox_inches="tight", bbox_extra_artists=[leg])
print(f"wrote {out}")
