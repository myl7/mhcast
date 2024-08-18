import json

import matplotlib.pyplot as plt
import numpy as np

xs = np.array([2**x for x in range(11, 18)])

with open("data/dcf_dpf.json", "r") as f:
    data = json.load(f)
    dcf_rows = np.array(data["dcf"])
    dpf_rows = np.array(data["dpf"])

plt.figure(figsize=(6, 4))

plt.yscale("log", base=10)
plt.xscale("log", base=2)

plt.plot(xs, dcf_rows, label="DCFs of MHcast", color="brown", marker="D")
plt.plot(xs, dpf_rows, label="DPFs of Express", color="green", marker="s")
plt.legend()
plt.xlabel("Number of mailboxes")
plt.ylabel("Time (sec)")

plt.tight_layout()
plt.show()
