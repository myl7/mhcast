import json

import matplotlib.pyplot as plt
import numpy as np

xs = np.array([2**x for x in range(0, 6)])
x_labels = [str(x) for x in xs]
x_pos = np.arange(len(xs))

with open("data/part_time.json", "r") as f:
    data = json.load(f)
    mhcast_rows = np.array(data["mhcast_mac"])
    spectrum_rows = np.array(data["spectrum_audit"])
    express_rows = np.array(data["express_audit"])

plt.figure(figsize=(16, 4))

for i in range(3):
    axes = plt.subplot(1, 3, i + 1)
    axes.set_yscale("log", base=2)
    axes.set_xticks(x_pos, labels=x_labels)
    width = 0.5
    axes.bar(x_pos - width / 2, mhcast_rows[i] / 1000, width / 2, label="MHcast", color="brown")
    axes.bar(x_pos, spectrum_rows[i] / 1000, width / 2, label="Spectrum", color="blue")
    axes.bar(x_pos + width / 2, express_rows[i] / 1000, width / 2, label="Express", color="green")
    axes.legend()
    axes.title.set_text(f"Mailboxes: {2 ** (11 + i * 3)}")
    axes.xaxis.label.set_text("Recipient group size")
    axes.yaxis.label.set_text("Access control / audit time (sec)")

plt.tight_layout()
plt.show()
