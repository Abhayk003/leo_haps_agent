from simulator import MIN_SNR_DB, usable_capacity


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


def make_perfect_planner(options, budget):
    gains = []
    for t, opts in options.items():
        haps = next(o for o in opts if o["option"] == "HAPS")
        leo = best_leo(opts)
        leo_cap = usable_capacity(leo) if leo else 0.0
        gain = usable_capacity(haps) - leo_cap
        if gain > 0:
            gains.append((gain, t))

    gains.sort(reverse=True)
    haps_minutes = {t for gain, t in gains[:budget]}

    def policy(t, opts, current, haps_left):
        if t in haps_minutes:
            return "HAPS"
        leo = best_leo(opts)
        return leo["option"] if leo else None

    return policy