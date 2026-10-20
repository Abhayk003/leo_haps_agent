from simulator import load_options, usable_capacity, run
from policies import best_leo

OPTIONS = load_options()
BUDGET = 15

def to_ranges(minutes):
    if not minutes:
        return "none"
    minutes = sorted(minutes)
    ranges = []
    start = prev = minutes[0]
    for m in minutes[1:]:
        if m == prev + 1:
            prev = m
            continue
        ranges.append(f"{start}-{prev}" if start != prev else f"{start}")
        start = prev = m
    ranges.append(f"{start}-{prev}" if start != prev else f"{start}")
    return ", ".join(ranges)


def haps_gain(t):
    opts = OPTIONS[t]
    haps = next(o for o in opts if o["option"] == "HAPS")
    leo = best_leo(opts)
    leo_cap = usable_capacity(leo) if leo else 0.0
    return usable_capacity(haps) - leo_cap, leo_cap


def get_scenario_summary() -> str:
    """
    Get a summary of the scenario: its length, the minutes when no LEO satellite link is
    usable, the rain forecast, and the minutes when HAPS is faster than the best LEO link,
    ranked by how much throughput HAPS adds in each.

    Returns:
      A short text summary with minute ranges.
    """
    minutes = sorted(OPTIONS)
    leo_dead = [t for t in minutes if haps_gain(t)[1] == 0.0]
    rain = [t for t in minutes if OPTIONS[t][0]["raining"]]
    haps_better = [t for t in minutes if haps_gain(t)[0] > 0]
    gains = sorted(((haps_gain(t)[0], t) for t in haps_better), reverse=True)
    ranked_text = ", ".join(f"{t} (+{g:.0f} Mbps)" for g, t in gains)
    lines = [
        f"Scenario length: {len(minutes)} minutes (minute {minutes[0]} to {minutes[-1]}).",
        f"Minutes with no usable LEO link (outage unless HAPS is used): "
        f"{len(leo_dead)} minutes -> {to_ranges(leo_dead)}",
        f"Rain forecast: {to_ranges(rain)}",
        f"Minutes where HAPS is faster than the best LEO link: "
        f"{len(haps_better)} minutes -> {to_ranges(haps_better)}",
        f"Those minutes ranked by throughput gain from using HAPS, largest first: {ranked_text}",
    ]
    return "\n".join(lines)


def parse_ranges(text):
    minutes = set()
    text = text.strip()
    if text == "" or text.lower() == "none":
        return minutes
    for part in text.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            minutes.update(range(int(a), int(b) + 1))
        else:
            minutes.add(int(part))
    return minutes


def evaluate_plan(haps_minutes: str) -> str:
    """
    Simulate a HAPS plan and report its results. In every minute not listed, the best
    LEO satellite link is used.

    Args:
      haps_minutes: The minutes when HAPS should be used, written as ranges,
        for example "117-119, 122-124". Use "none" to use no HAPS at all.

    Returns:
      HAPS minutes used, outage minutes, average throughput and number of handovers,
      or a message explaining why the plan was rejected.
    """
    try:
        plan = parse_ranges(haps_minutes)
    except ValueError:
        return 'Could not read the minutes. Use a format like "117-119, 122-124".'

    if len(plan) > BUDGET:
        return f"Plan rejected: it uses {len(plan)} HAPS minutes but the budget is {BUDGET}."

    outside = [t for t in plan if t not in OPTIONS]
    if outside:
        return f"Plan rejected: minutes outside the scenario: {to_ranges(outside)}."

    def policy(t, opts, current, haps_left):
        if t in plan:
            return "HAPS"
        leo = best_leo(opts)
        return leo["option"] if leo else None

    s = run(policy, OPTIONS, budget=BUDGET)
    return (f"HAPS minutes used: {s['haps_min']} of {BUDGET}\n"
            f"Outage minutes: {s['outage_min']}\n"
            f"Average throughput: {s['avg_throughput_mbps']:.1f} Mbps\n"
            f"Handovers: {s['handovers']}")



def build_plan(max_haps_minutes: int, min_gain_mbps: float, minimise_haps_use: bool) -> str:
    """
    Build the best HAPS plan for the given settings. Minutes are chosen in order of how much
    throughput HAPS adds, largest first. Outage minutes always have the largest gain, so they
    are always covered first.

    Args:
      max_haps_minutes: The most HAPS minutes the plan may use. Cannot exceed the budget.
      min_gain_mbps: Only use HAPS in minutes where it adds at least this much throughput,
        in Mbps. Use 0 for no limit.
      minimise_haps_use: If true, use HAPS only in minutes with no usable LEO link, so that
        as little HAPS as possible is used. If false, also use HAPS to raise throughput.

    Returns:
      The plan as minute ranges, ready to pass to evaluate_plan, and the settings used.
    """
    max_haps_minutes = int(max_haps_minutes)
    min_gain_mbps = float(min_gain_mbps)
    if isinstance(minimise_haps_use, str):
        minimise_haps_use = minimise_haps_use.strip().lower() == "true"

    notes = []
    if max_haps_minutes > BUDGET:
        notes.append(f"max_haps_minutes reduced from {max_haps_minutes} to the budget of {BUDGET}.")
        max_haps_minutes = BUDGET

    candidates = []
    for t in OPTIONS:
        gain, leo_cap = haps_gain(t)
        if gain <= 0 or gain < min_gain_mbps:
            continue
        if minimise_haps_use and leo_cap > 0:
            continue
        candidates.append((gain, t))

    candidates.sort(reverse=True)
    chosen = [t for gain, t in candidates[:max(0, max_haps_minutes)]]

    text = (f"Plan: {to_ranges(chosen)} ({len(chosen)} HAPS minutes)\n"
            f"Settings used: max_haps_minutes={max_haps_minutes}, "
            f"min_gain_mbps={min_gain_mbps:g}, minimise_haps_use={minimise_haps_use}")
    if notes:
        text += "\nNote: " + " ".join(notes)
    return text


if __name__ == "__main__":
    tests = [(15, 0, False), (15, 0, True), (8, 0, False), (15, 100, False), (40, 0, False)]
    for max_m, min_g, out_only in tests:
        print(f"Settings: max_haps_minutes={max_m}, min_gain_mbps={min_g}, outages_only={out_only}")
        result = build_plan(max_m, min_g, out_only)
        print(result)
        plan_text = result.splitlines()[0].replace("Plan: ", "").split(" (")[0]
        print(evaluate_plan(plan_text))
        print()