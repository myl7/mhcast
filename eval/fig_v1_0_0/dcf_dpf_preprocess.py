import sys
import re
import glob
import os
import json


def str_to_time_ms(s: str) -> float:
    assert s[-1] == "s"
    if s[-2].isdigit():
        return float(s[:-1]) * 1000
    elif s[-2] == "m":
        return float(s[:-2])
    else:
        raise ValueError("Invalid time format")


def preprocess(p: str, topic: str) -> float:
    with open(p, "r") as f:
        rows = list(f.readlines())
        write_rows = [row for row in rows if re.match(r"^" + topic, row)]
        times = [str_to_time_ms(row[len(topic) : -1]) for row in write_rows]
    time = sum(times) / len(times)
    return time


if __name__ == "__main__":
    if len(sys.argv) < 2:
        data = {}

        fs = glob.glob("logs/dcf_dpf/dif-*.log")
        fs.sort()
        ts = [preprocess(f, "dif eval: ") / 2 for f in fs]
        data["dcf"] = ts

        fs = glob.glob("logs/dcf_dpf/dpf-*.log")
        fs.sort()
        ts = [preprocess(f, "dpf eval: ") for f in fs]
        data["dpf"] = ts

        with open("data/dcf_dpf.json", "w") as f:
            json.dump(data, f)
    elif sys.argv[1] == "dcf":
        fs = glob.glob("logs/dcf_dpf/dif-*.log")
        fs.sort()
        ts = [preprocess(f, "dif eval: ") / 2 for f in fs]
        print(ts)
    elif sys.argv[1] == "dpf":
        fs = glob.glob("logs/dcf_dpf/dpf-*.log")
        fs.sort()
        ts = [preprocess(f, "dpf eval: ") for f in fs]
        print(ts)
    else:
        print("Invalid argument")
