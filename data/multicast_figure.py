import json

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 12
plt.rcParams["font.family"] = "Times Roman"

xs = np.array([2**x for x in range(0, 6)])
x_labels = [str(x) for x in xs]
x_pos = np.arange(len(xs))

with open("data/part_time.json", "r") as f:
    data = json.load(f)
    mhcast_rows = np.array(data["mhcast_dif"])
    spectrum_rows = np.array(data["spectrum_dpf"])
    express_rows = np.array(data["express_dpf"])

plt.figure(figsize=(5, 6.25))

for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_yscale("log", base=2)
    ax.set_xticks(x_pos, labels=x_labels)
    width = 0.5
    ax.bar(x_pos - width / 2, mhcast_rows[i] / 1000, width / 2, label="MHcast", color="brown")
    ax.bar(x_pos, spectrum_rows[i] / 1000, width / 2, label="Spectrum", color="blue")
    ax.bar(x_pos + width / 2, express_rows[i] / 1000, width / 2, label="Express", color="green")
    ax.title.set_text(f"\\# of mailboxes: $2^{'{'}{11 + i * 3}{'}'}$")
    ax.yaxis.label.set_text("Multicast\ntime (sec)")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.8), ncol=3)
plt.tight_layout()

fig = plt.gcf()
plt.show()
if input("Save plot? (y/N): ") == "y":
    fig.savefig("data/multicast_time.pdf", bbox_inches="tight")
