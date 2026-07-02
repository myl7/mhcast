import sys
import re
import glob
import os
import json


def str_to_time_s(s: str) -> float:
    assert s[-1] == "s"
    if s[-2].isdigit():
        return float(s[:-1])
    elif s[-2] == "m":
        return float(s[:-2]) / 1000
    elif s[-2] == "n":
        return float(s[:-2]) / 1000_000_000
    else:
        raise ValueError("Invalid time format")


def preprocess_mhcast(p: str) -> float:
    with open(p, "r") as f:
        rows = list(f.readlines())
        write_rows = [row for row in rows if re.match(r"^write: ", row)]
        times = [str_to_time_s(row[len("write: ") : -1]) for row in write_rows]
    time = sum(times) / len(times)
    throughput = 1 / time
    return throughput


def preprocess_express(p: str) -> float:
    with open(p, "r") as f:
        trials = f.read().split("\n\n")
        trials = [t for t in trials if len(t.strip()) > 0]
        ma = re.search(r"mb(\d+)", os.path.basename(p))
        assert ma is not None
        mb = int(ma.group(1))
        m = 2**mb
        assert len(trials) == m
    time = 0.0
    for trial in trials:
        rows = trial.split("\n")
        write_rows = [row for row in rows if re.match(r"^write: ", row)]
        times = [str_to_time_s(row[len("write: ") :]) for row in write_rows]
        time += sum(times) / len(times)
    throughput = 1 / time
    return throughput


def preprocess_talek(p: str) -> float:
    with open(p, "r") as f:
        body = f.read()
        time_m = re.search(r"(\d+) ns\/op", body)
        assert time_m is not None
        time_s = time_m.group(1) + "ns"
        time = str_to_time_s(time_s)
    throughput = 1 / time
    return throughput


if __name__ == "__main__":
    if len(sys.argv) < 2:
        data = {}

        fs = glob.glob("logs/mhcast/write-*.log")
        fs.sort()
        ts = [preprocess_mhcast(f) for f in fs]
        tss = [ts[0:6], ts[6:12], ts[12:18]]
        data["mhcast"] = tss

        fs = glob.glob("logs/spectrum/write-*.log")
        fs.sort()
        ts = [preprocess_mhcast(f) * 8 for f in fs]
        tss = [ts[0:6], ts[6:12], ts[12:18]]
        data["spectrum"] = tss

        fs = glob.glob("logs/express/write-*.log")
        fs.sort()
        ts = [preprocess_express(f) for f in fs]
        tss = [ts[0:6], ts[6:12], ts[12:18]]
        data["express"] = tss

        fs = glob.glob("logs/talek/write-*.log")
        fs.sort()
        ts = [preprocess_talek(f) for f in fs]
        tss = [ts[0:6], ts[6:12], [ts[12] for _ in range(6)]]
        data["talek"] = tss

        with open("data/throughput.json", "w") as f:
            json.dump(data, f)
    elif sys.argv[1] == "mhcast":
        fs = glob.glob("logs/mhcast/write-*.log")
        fs.sort()
        ts = [preprocess_mhcast(f) for f in fs]
        print(ts)
    elif sys.argv[1] == "spectrum":
        fs = glob.glob("logs/spectrum/write-*.log")
        fs.sort()
        ts = [preprocess_mhcast(f) * 8 for f in fs]
        print(ts)
    elif sys.argv[1] == "express":
        fs = glob.glob("logs/express/write-*.log")
        fs.sort()
        ts = [preprocess_express(f) for f in fs]
        print(ts)
    elif sys.argv[1] == "talek":
        fs = glob.glob("logs/talek/write-*.log")
        fs.sort()
        ts = [preprocess_talek(f) for f in fs]
        print(ts)
    else:
        print("Invalid argument")
