from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(__file__).resolve().parent

plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 18
plt.rcParams["font.family"] = "Times New Roman"

xs = np.array([2**x for x in range(0, 5)])
x_labels = [str(x) for x in xs]
x_pos = np.arange(len(xs))

mhcast_ys = [
    [5.145846, 5.864128, 6.509374, 5.821873, 5.858455],
    [34.116021, 32.876273, 34.989534, 34.332863, 34.589337],
    [244.733407, 245.970701, 244.979463, 245.961906, 246.010341]
]
spectrum_ys = [
    np.array([23.527587, 24.157152 * 2, 23.901477 * 4, 23.110163 * 8, 23.902056 * 16]) / 16,
    np.array([208.304942, 208.400053 * 2, 215.018723 * 4, 236.54003 * 8, 212.549999 * 16]) / 16,
    np.array([1.496008509 * 1000, 1.655254209 * 1000 * 2, 1.599455261 * 1000 * 4, 1.488166033 * 1000 * 8, 1.466206667 * 1000 * 16]) / 16,
]
express_ys = [
    [36.253436, 39.34214 * 2, 41.43044 * 4, 36.045401 * 8, 35.520358 * 16],
    [351.153192, 346.862686 * 2, 353.569257 * 4, 354.358528 * 8, 344.530103 * 16],
    [4.313930804 * 1000, 4.490653314 * 1000 * 2, 4.598824788 * 1000 * 4, 4.613637511 * 1000 * 8, 4.840407418 * 1000 * 16]
]

mhcast_ys = [np.array(y) / 1000 for y in mhcast_ys]
spectrum_ys = [np.array(y) / 1000 for y in spectrum_ys]
express_ys = [np.array(y) / 1000 for y in express_ys]

plt.figure(figsize=(4.7, 7.5))
for i in range(3):
    ax = plt.subplot(3, 1, i + 1)
    ax.set_yscale("log", base=10)
    ax.set_xticks(x_pos, labels=x_labels)
    width = 0.5
    ax.bar(x_pos - width / 2, mhcast_ys[i] / 1000, width / 2, label="MHcast", color="#FA5252")
    ax.bar(x_pos, spectrum_ys[i] / 1000, width / 2, label="Spectrum", color="#339AF0")
    ax.bar(x_pos + width / 2, express_ys[i] / 1000, width / 2, label="Express", color="#4CAF50")
    ax.set_title(f"\\# of mailboxes: $2^{'{'}{11 + i * 3}{'}'}$")
    ax.set_ylabel("Multicast\ntime (sec)")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -1.1), ncol=2, fontsize=16)
plt.tight_layout(pad=0.1)

fig = plt.gcf()
plt.show()
fig.savefig(OUT_DIR / "part_multicast.pdf", bbox_inches="tight")
