from simulator import load_options, run


def leo_highest_elevation(t, opts, current):
    leo = [o for o in opts if o["option"] != "HAPS"]
    if not leo:
        return None
    return max(leo, key=lambda o: o["elevation_deg"])["option"]


def always_haps(t, opts, current):
    return "HAPS"


def greedy_max_capacity(t, opts, current):
    return max(opts, key=lambda o: o["capacity_mbps"])["option"]


options = load_options()
print("Minutes in scenario:", len(options))
print()
print("Policy                     Avg throughput   Handovers   Outage minutes")
for name, policy in [("LEO only, highest elev", leo_highest_elevation),
                     ("Always HAPS", always_haps),
                     ("Greedy max capacity", greedy_max_capacity)]:
    s = run(policy, options)
    print(f"{name:25s}  {s['avg_throughput_mbps']:8.1f} Mbps   {s['handovers']:6d}      {s['outage_min']:6d}")