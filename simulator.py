import csv
from collections import defaultdict

STEP_S = 60.0
HANDOVER_INTERRUPTION_S = 2.0
MIN_SNR_DB = 0.0
HAPS_BUDGET_MIN = 36


def load_options(path="scenario_links.csv"):
    options = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            t = int(row["time_min"])
            options[t].append({
                "option": row["option"],
                "raining": row["raining"] == "1",
                "elevation_deg": float(row["elevation_deg"]),
                "snr_db": float(row["snr_db"]),
                "capacity_mbps": float(row["capacity_mbps"]),
                "delay_ms": float(row["delay_ms"]),
            })
    return dict(options)


def usable_capacity(opt):
    if opt["snr_db"] < MIN_SNR_DB:
        return 0.0
    return opt["capacity_mbps"]


def run(policy, options, budget=HAPS_BUDGET_MIN):
    current = None
    handovers = 0
    outage_min = 0
    haps_used = 0
    total_mbit = 0.0

    for t in sorted(options):
        haps_left = budget - haps_used
        choice_name = policy(t, options[t], current, haps_left)

        if choice_name == "HAPS" and haps_left <= 0:
            choice_name = None

        if choice_name is None:
            outage_min += 1
            current = None
            continue

        choice = next(o for o in options[t] if o["option"] == choice_name)

        if choice_name == "HAPS":
            haps_used += 1

        seconds = STEP_S
        if current is not None and choice_name != current:
            handovers += 1
            seconds -= HANDOVER_INTERRUPTION_S

        cap = usable_capacity(choice)
        if cap == 0.0:
            outage_min += 1
        total_mbit += cap * seconds
        current = choice_name

    return {
        "avg_throughput_mbps": total_mbit / (len(options) * STEP_S),
        "handovers": handovers,
        "outage_min": outage_min,
        "haps_min": haps_used,
    }