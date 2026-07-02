from pathlib import Path

import figstyle as fs
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(__file__).resolve().parent

fs.init(17)

xs = np.array([2**x for x in range(11, 18)])
dcf_ys = np.array([12.702942, 25.124477, 47.140151, 93.677549, 187.932052, 371.466433, 754.881201]) / 2
dpf_ys = [53.5, 103.5, 208.5, 412.5, 818.92, 1.7226 * 1000, 3.3234 * 1000]

fig, ax = plt.subplots(figsize=(6, 3.7))
ax.set_yscale("log", base=10)
ax.set_xscale("log", base=2)
ax.set_xticks(xs)
ax.grid(True, which="minor", color="#f0f0f0", linewidth=0.5)

fs.plot_line(ax, xs, dpf_ys, "DPF", label="DPF of Express")
fs.plot_line(ax, xs, dcf_ys, "DCF", label="DCF of MHcast")

ax.set_xlabel("Number of mailboxes")
ax.set_ylabel("Full domain eval\ntime (sec)")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.78), ncol=2, fontsize=15)
plt.tight_layout(pad=0.2)
fig.savefig(OUT_DIR / "dcf_dpf.pdf", bbox_inches="tight")
