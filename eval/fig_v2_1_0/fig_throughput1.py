from pathlib import Path

import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent

xs = [2**x for x in range(0, 5)]
mhcast_ys = [
    [28.4949, 26.9795, 26.5879, 26.8002, 27.4412],
    [3.77788, 3.79738, 3.75746, 3.76584, 3.75427],
    [0.481027, 0.479917, 0.479928, 0.480021, 0.479739],
]
agomr_ys = [
    [4.25947, 4.76395, 4.75736, 3.97306, 4.38208],
    [4.25947, 4.76395, 4.75736, 3.97306, 4.38208],
    [4.25947, 4.76395, 4.75736, 3.97306, 4.38208],
]
fgomr_ys = [
    [6.48283, 5.601985, 5.63000, 6.39458, 6.21391],
    [6.48283, 5.601985, 5.63000, 6.39458, 6.21391],
    [6.48283, 5.601985, 5.63000, 6.39458, 6.21391],
]

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Times New Roman"
plt.figure(figsize=(4.5, 8))

for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_xscale("log", base=2)
    ax.set_ylabel("Throughput\n(msgs/sec)")
    ax.locator_params(axis="y", nbins=4)
    ax.set_xticks(xs)

    if i < 3:
        ax.set_title(f"\\# of mailboxes: $2^{'{'}{11 + i * 3}{'}'}$")
        ax.plot(xs, mhcast_ys[i], label="MHcast", color="red", marker="x")
        ax.plot(xs, agomr_ys[i], label="AGOMR (1 group)", color="purple", marker="*")
        ax.plot(xs, fgomr_ys[i], label="FGOMR (1 group)", color="orange", marker="D")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -1.5), ncol=1, fontsize=16)
plt.tight_layout(pad=0.1)

fig = plt.gcf()
plt.show()
fig.savefig(OUT_DIR / "throughput1.pdf", bbox_inches="tight")
