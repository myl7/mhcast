import json

import matplotlib.pyplot as plt

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 12
plt.rcParams["font.family"] = "Times Roman"

xs = [2**x for x in range(0, 6)]

with open("data/throughput.json", "r") as f:
    data = json.load(f)
    mhcast_rows = data["mhcast"]
    spectrum_rows = data["spectrum"]
    express_rows = data["express"]

plt.figure(figsize=(5, 6.5))

for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.plot(xs, mhcast_rows[i], label="MHcast", color="brown", marker="D")
    ax.plot(xs, spectrum_rows[i], label="Spectrum", color="blue", marker="o")
    ax.plot(xs, express_rows[i], label="Express", color="green", marker="s")
    ax.title.set_text(f"\\# of mailboxes: $2^{'{'}{11 + i * 3}{'}'}$")
    ax.yaxis.label.set_text("Throughput\n(msgs/sec)")
    ax.locator_params(axis="y", nbins=4)

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.75), ncol=3)
plt.tight_layout()

fig = plt.gcf()
plt.show()
if input("Save plot? (y/N): ") == "y":
    fig.savefig("data/throughput.pdf", bbox_inches="tight")
