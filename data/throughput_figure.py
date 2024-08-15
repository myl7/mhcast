import json

import matplotlib.pyplot as plt

xs = [2**x for x in range(0, 6)]

with open("data/throughput.json", "r") as f:
    data = json.load(f)
    mhcast_rows = data["mhcast"]
    spectrum_rows = data["spectrum"]
    express_rows = data["express"]

plt.figure(figsize=(16, 4))

for i in range(3):
    axes = plt.subplot(1, 3, i + 1)
    axes.plot(xs, mhcast_rows[i], label="MHcast", color="brown", marker="D")
    axes.plot(xs, spectrum_rows[i], label="Spectrum", color="blue", marker="o")
    axes.plot(xs, express_rows[i], label="Express", color="green", marker="s")
    axes.legend()
    axes.title.set_text(f"Mailboxes: {2 ** (11 + i * 3)}")
    axes.xaxis.label.set_text("Recipient group size")
    axes.yaxis.label.set_text("Throughput (msgs/sec)")

plt.tight_layout()
plt.show()
