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
    [29.659673, 30.950221, 30.851648, 31.210384, 30.326905],
    [230.31795, 230.194412, 230.862869, 230.944989, 231.485136],
    [1.833815127 * 1000, 1.837374709 * 1000, 1.838322443 * 1000, 1.836929155 * 1000, 1.838118125 * 1000],
]
spectrum_ys = [
    np.array([554.991303, 556.488653 * 2, 555.23022 * 4, 555.514761 * 8, 563.569438 * 16]) / 16,
    np.array([3.681384067 * 1000, 3.666200507 * 1000 * 2, 3.669299073 * 1000 * 4, 3.665820202 * 1000 * 8, 3.668039065 * 1000 * 16]) / 16,
    np.array([28.641998771 * 1000, 28.557677269 * 1000 * 2, 28.650189558 * 1000 * 4, 28.637425566 * 1000 * 8, 28.572164332 * 1000 * 16]) / 16,
]
express_ys = [
    [226.217987 - 108, 223.315432 * 2, 221.775604 * 4, 229.574951 * 8, 228.824117 * 16],
    [(107.895071 + 108), (108.356588 + 108) * 2, (106.856553 + 108) * 4, (109.616877 + 108) * 8, (108.296005 + 108) * 16],
    [(121.377388 + 108), (119.952944 + 108) * 2, (119.277318 + 108) * 4, (118.946191 + 108) * 8, (117.753241 + 108) * 16],
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
    ax.set_ylabel("Access control\ntime (sec)")

plt.xlabel("Recipient group size")
plt.legend(loc="lower center", bbox_to_anchor=(0.5, -1.1), ncol=2, fontsize=16)
plt.tight_layout(pad=0.1)

fig = plt.gcf()
plt.show()
fig.savefig(OUT_DIR / "part_access_control.pdf", bbox_inches="tight")
