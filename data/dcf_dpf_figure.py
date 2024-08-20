import json

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 12
plt.rcParams["font.family"] = "Times Roman"

xs = np.array([2**x for x in range(11, 18)])

with open("data/dcf_dpf.json", "r") as f:
    data = json.load(f)
    dcf_rows = np.array(data["dcf"])
    dpf_rows = np.array(data["dpf"])

plt.figure(figsize=(5, 3.5))

plt.yscale("log", base=10)
plt.xscale("log", base=2)

plt.plot(xs, dcf_rows, label="DCFs of MHcast", color="brown", marker="D")
plt.plot(xs, dpf_rows, label="DPFs of Express", color="green", marker="s")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.75), ncol=2)
plt.xlabel("Number of mailboxes")
plt.ylabel("Full eval\ntime (sec)")

plt.tight_layout()

fig = plt.gcf()
plt.show()
if input("Save plot? (y/N): ") == "y":
    fig.savefig("data/dcf_dpf.pdf", bbox_inches="tight")
