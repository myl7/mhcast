from pathlib import Path

import figstyle as fs
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent

fs.init(17)

xs = [
    [2**x for x in range(7, 12)],
    [2**x for x in range(10, 15)],
    [2**x for x in range(13, 18)],
]
mhcast_ys = [
    [1000 / 36.608278, 1000 / 35.167111, 1000 / 35.586771, 1000 / 34.545813, 1000 / 36.017361],
    [1000 / 263.152232, 1000 / 263.46868, 1000 / 263.407839, 1000 / 262.761382, 1000 / 264.484196],
    [1 / 2.082698943, 1 / 2.079641115, 1 / 2.081890343, 1 / 2.07949364, 1 / 2.081169384],
]

series = [
    ("$N = 2^{11}$", "#F03E3E", "x"),
    ("$N = 2^{14}$", "#1C7ED6", "o"),
    ("$N = 2^{17}$", "#2F9E44", "s"),
]

fig, ax = plt.subplots(figsize=(6, 3.6))
ax.set_xscale("log", base=2)
# Log y-axis: a linear axis squashed the N=2^14 and N=2^17 lines onto zero and
# hid that their throughput is also flat in the group size. Log scale separates
# all three and makes the "throughput stays constant" message visible for each.
ax.set_yscale("log", base=10)
ax.set_xticks([2**x for x in range(7, 18)])
ax.grid(True, which="minor", color="#f0f0f0", linewidth=0.5)

for (label, color, marker), x, y in zip(series, xs, mhcast_ys):
    mec, mew = (color, 1.8) if marker == "x" else ("white", 0.7)
    ax.plot(x, y, label="MHcast (" + label + ")", color=color, marker=marker,
            markersize=6.5, markeredgecolor=mec, markeredgewidth=mew, linewidth=2.0)

# Headroom so the inset legend (placed in the empty upper-right) clears the data.
ax.set_ylim(top=ax.get_ylim()[1] * 3)
ax.set_xlabel("Recipient group size")
ax.set_ylabel("Throughput\n(msgs/sec)")
ax.legend(loc="upper right", ncol=1, fontsize=14)
plt.tight_layout(pad=0.2)
fig.savefig(OUT_DIR / "throughput_large_group.pdf", bbox_inches="tight")
