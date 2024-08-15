import csv

import matplotlib.pyplot as plt

with open("logs/mhcast/throughput.csv", "r") as f:
    mhcast_rows = list(csv.reader(f))
with open("logs/spectrum/throughput.csv", "r") as f:
    spectrum_rows = list(csv.reader(f))

xs = [2**x for x in range(0, 6)]
plt.figure(figsize=(16, 4))

for i in range(3):
    axes = plt.subplot(1, 3, i + 1)
    axes.plot(xs, [float(y) for y in mhcast_rows[i]], label="MHcast", color="brown", marker="D")
    axes.plot(xs, [float(y) for y in spectrum_rows[i]], label="Spectrum", color="blue", marker="o")
    axes.legend()
    axes.title.set_text(f"Number of mailboxes: {2 ** (11 + i * 3)}")
    axes.xaxis.label.set_text("Recipient group size")
    axes.yaxis.label.set_text("Throughput (msgs/sec)")

plt.tight_layout()
plt.show()
