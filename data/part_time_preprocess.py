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


def preprocess_mhcast(p: str, topic: str) -> float:
    with open(p, "r") as f:
        rows = list(f.readlines())
        write_rows = [row for row in rows if re.match(r"^" + topic, row)]
        times = [str_to_time_ms(row[len(topic) : -1]) for row in write_rows]
    time = sum(times) / len(times)
    return time


def preprocess_express(p: str, topic: str) -> float:
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
        write_rows = [row for row in rows if re.match(r"^" + topic, row)]
        times = [str_to_time_ms(row[len(topic) :]) for row in write_rows]
        time += sum(times) / len(times)
    return time


if __name__ == "__main__":
    if len(sys.argv) < 2:
        data = {}

        fs = glob.glob("logs/mhcast/write-*.log")
        fs.sort()
        dif_ts = [preprocess_mhcast(f, "dif eval: ") for f in fs]
        dif_tss = [dif_ts[0:6], dif_ts[6:12], dif_ts[12:18]]
        mac_ts = [preprocess_mhcast(f, "mac: ") for f in fs]
        mac_tss = [mac_ts[0:6], mac_ts[6:12], mac_ts[12:18]]
        data["mhcast_dif"] = dif_tss
        data["mhcast_mac"] = mac_tss

        fs = glob.glob("logs/spectrum/write-*.log")
        fs.sort()
        dpf_ts = [preprocess_mhcast(f, "dpf eval: ") / 8 for f in fs]
        dpf_tss = [dpf_ts[0:6], dpf_ts[6:12], dpf_ts[12:18]]
        audit_ts = [preprocess_mhcast(f, "audit: ") / 8 for f in fs]
        audit_tss = [audit_ts[0:6], audit_ts[6:12], audit_ts[12:18]]
        data["spectrum_dpf"] = dpf_tss
        data["spectrum_audit"] = audit_tss

        fs = glob.glob("logs/express/write-*.log")
        fs.sort()
        dpf_ts = [preprocess_express(f, "dpf eval: ") for f in fs]
        dpf_tss = [dpf_ts[0:6], dpf_ts[6:12], dpf_ts[12:18]]
        audit_ts = [preprocess_express(f, "audit: ") for f in fs]
        audit_tss = [audit_ts[0:6], audit_ts[6:12], audit_ts[12:18]]
        data["express_dpf"] = dpf_tss
        data["express_audit"] = audit_tss

        with open("data/part_time.json", "w") as f:
            json.dump(data, f)
    elif sys.argv[1] == "mhcast":
        fs = glob.glob("logs/mhcast/write-*.log")
        fs.sort()
        dif_ts = [preprocess_mhcast(f, "dif eval: ") for f in fs]
        mac_ts = [preprocess_mhcast(f, "mac: ") for f in fs]
        print("dif eval:", dif_ts)
        print("mac:", mac_ts)
    elif sys.argv[1] == "spectrum":
        fs = glob.glob("logs/spectrum/write-*.log")
        fs.sort()
        dpf_ts = [preprocess_mhcast(f, "dpf eval: ") / 8 for f in fs]
        audit_ts = [preprocess_mhcast(f, "audit: ") / 8 for f in fs]
        print("dpf eval:", dpf_ts)
        print("audit:", audit_ts)
    elif sys.argv[1] == "express":
        fs = glob.glob("logs/express/write-*.log")
        fs.sort()
        dpf_ts = [preprocess_express(f, "dpf eval: ") for f in fs]
        audit_ts = [preprocess_express(f, "audit: ") for f in fs]
        print("dpf eval:", dpf_ts)
        print("audit:", audit_ts)
    else:
        print("Invalid argument")
