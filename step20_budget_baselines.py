from simulator import load_options, run, MIN_SNR_DB, HAPS_BUDGET_MIN


def best_leo(opts):
    leo = [o for o in opts if o["option"] != "HAPS"]
    if not leo:
        return None
    return max(leo, key=lambda o: o["capacity_mbps"])


def leo_only(t, opts, current, haps_left):
    leo = [o for o in opts if o["option"] != "HAPS"]
    if not leo:
        return None
    return max(leo, key=lambda o: o["elevation_deg"])["option"]


def always_haps(t, opts, current, haps_left):
    return "HAPS"


def greedy_with_budget(t, opts, current, haps_left):
    best = max(opts, key=lambda o: o["capacity_mbps"])
    if best["option"] == "HAPS" and haps_left <= 0:
        leo = best_leo(opts)
        return leo["option"] if leo else None
    return best["option"]


def haps_as_fallback(t, opts, current, haps_left):
    leo = best_leo(opts)
    if leo is not None and leo["snr_db"] >= MIN_SNR_DB:
        return leo["option"]
    if haps_left > 0:
        return "HAPS"
    return leo["option"] if leo else None


options = load_options()
print(f"HAPS budget: {HAPS_BUDGET_MIN} minutes out of {len(options)}")
print()
print("Policy                   Avg throughput   Handovers   Outage min   HAPS min used")
for name, policy in [("LEO only", leo_only),
                     ("Always HAPS", always_haps),
                     ("Greedy with budget", greedy_with_budget),
                     ("HAPS as fallback", haps_as_fallback)]:
    s = run(policy, options)
    print(f"{name:22s}  {s['avg_throughput_mbps']:8.1f} Mbps   {s['handovers']:6d}      "
          f"{s['outage_min']:6d}         {s['haps_min']:6d}")