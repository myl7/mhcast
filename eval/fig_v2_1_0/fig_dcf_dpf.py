from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(__file__).resolve().parent

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Times New Roman"

xs = np.array([2**x for x in range(11, 18)])
dcf_ys = np.array([12.702942, 25.124477, 47.140151, 93.677549, 187.932052, 371.466433, 754.881201]) / 2
dpf_ys = [53.5, 103.5, 208.5, 412.5, 818.92, 1.7226 * 1000, 3.3234 * 1000]

plt.figure(figsize=(6, 3.5))

plt.yscale("log", base=10)
plt.xscale("log", base=2)
plt.xticks(xs)

plt.plot(xs, dcf_ys, label="DCF of MHcast", color="#FA5252", marker="x")
plt.plot(xs, dpf_ys, label="DPF of Express", color="#4CAF50", marker="s")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.75), ncol=2, fontsize=16)
plt.xlabel("Number of mailboxes")
plt.ylabel("Full domain eval\ntime (sec)")

plt.tight_layout(pad=0.1)

fig = plt.gcf()
plt.show()
fig.savefig(OUT_DIR / "dcf_dpf.pdf", bbox_inches="tight")
