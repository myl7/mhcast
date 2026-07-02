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
    mhcast_rows = np.array(data["mhcast_mac"])
    spectrum_rows = np.array(data["spectrum_audit"])
    express_rows = np.array(data["express_audit"])

plt.figure(figsize=(5, 6))

for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_yscale("log", base=2)
    ax.set_xticks(x_pos, labels=x_labels)
    width = 0.5
    ax.bar(x_pos - width / 2, mhcast_rows[i] / 1000, width / 2, label="MHcast", color="brown")
    ax.bar(x_pos, spectrum_rows[i] / 1000, width / 2, label="Spectrum", color="blue")
    ax.bar(x_pos + width / 2, express_rows[i] / 1000, width / 2, label="Express", color="green")
    ax.title.set_text(f"\\# of mailboxes: $2^{'{'}{11 + i * 3}{'}'}$")
    ax.yaxis.label.set_text("Access control\ntime (sec)")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -1), ncol=3)
plt.tight_layout()

fig = plt.gcf()
plt.show()
if input("Save plot? (y/N): ") == "y":
    fig.savefig("data/access_control_time.pdf", bbox_inches="tight")
