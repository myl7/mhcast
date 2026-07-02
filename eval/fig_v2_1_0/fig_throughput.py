from pathlib import Path

import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Times New Roman"
plt.figure(figsize=(4.5, 7.5))

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
    [2.39263, 2.39263, 2.39263, 2.39263, 2.39263],
    [0.0285111, 0.0285111, 0.0285111, 0.0285111, 0.0285111],
    [0.000448418, 0.000448418, 0.000448418, 0.000448418, 0.000448418],
]

for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_xscale("log", base=2)
    ax.set_ylabel("Throughput\n(msgs/sec)")
    ax.locator_params(axis="y", nbins=4)
    ax.set_xticks(xs)
    ax.set_title(f"\\# of mailboxes: $2^{'{'}{11 + i * 3}{'}'}$")
    ax.plot(xs, mhcast_ys[i], label="MHcast", color="red", marker="x")
    ax.plot(xs, spectrum_ys[i], label="Spectrum", color="blue", marker="o")
    ax.plot(xs, express_ys[i], label="Express", color="green", marker="s")
    ax.plot(xs, talek_ys[i], label="Talek", color="brown", marker="^")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -1.1), ncol=2, fontsize=16)
plt.tight_layout(pad=0.1)

fig = plt.gcf()
plt.show()
fig.savefig(OUT_DIR / "throughput.pdf", bbox_inches="tight")
