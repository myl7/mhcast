from pathlib import Path

import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Times New Roman"
plt.figure(figsize=(6, 6.8))

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

plt.xscale("log", base=2)
# plt.set_xscale("log", base=2)
plt.locator_params(axis="y", nbins=4)
# plt.set_ylabel("Throughput\n(msgs/sec)")
plt.ylabel("Throughput\n(msgs/sec)")
# plt.set_xticks([2**x for x in range(7, 18)])
plt.xticks([2**x for x in range(7, 18)])
plt.plot(xs[0], mhcast_ys[0], label="MHcast ($N = 2^{11}$)", color="#FA5252", marker="x")
plt.plot(xs[1], mhcast_ys[1], label="MHcast ($N = 2^{14}$)", color="#339AF0", marker="o")
plt.plot(xs[2], mhcast_ys[2], label="MHcast ($N = 2^{17}$)", color="#4CAF50", marker="s")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -1), ncol=2, fontsize=16)
plt.tight_layout(pad=0.1)

fig = plt.gcf()
plt.show()
fig.savefig(OUT_DIR / "throughput_large_group.pdf", bbox_inches="tight")
