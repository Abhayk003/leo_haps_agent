from pipeline import run_pipeline

BUDGET = 15
SIZES = [("25%", "scenario_links_25.csv"), ("10%", "scenario_links_10.csv")]

GOALS = [
    ("Avoid all outages first. Then make the average throughput as high as possible.", (15, 0, False)),
    ("Use HAPS as little as possible, but never allow an outage.", (15, 0, True)),
    ("Keep 7 HAPS minutes in reserve for other users. Use the rest to maximise throughput.", (8, 0, False)),
    ("Only use HAPS when it adds at least 100 Mbps.", (15, 100, False)),
    ("HAPS should be an emergency backup only.", (15, 0, True)),
    ("Get the highest possible average throughput.", (15, 0, False)),
    ("Use at most 10 HAPS minutes, and only where HAPS adds at least 150 Mbps.", (10, 150, False)),
]


def normalise(args):
    m = min(int(args["max_haps_minutes"]), BUDGET)
    g = float(args["min_gain_mbps"])
    h = args["minimise_haps_use"]
    if isinstance(h, str):
        h = h.strip().lower() == "true"
    return (m, g, bool(h))


for size_label, links_file in SIZES:
    print(f"########## Constellation {size_label} ##########")
    correct = 0
    for i, (goal, expected) in enumerate(GOALS, start=1):
        r = run_pipeline(goal, BUDGET, planning_file=links_file, true_file=links_file)
        chosen = None
        for name, args in r["calls"]:
            if name == "build_plan":
                try:
                    chosen = normalise(args)
                except (KeyError, ValueError):
                    chosen = "invalid arguments"
        ok = chosen == expected
        correct += ok

        print(f"Goal {i}: {goal}")
        print(f"  Chosen settings: {chosen}  expected {expected}  {'CORRECT' if ok else 'WRONG'}"
              f"   reserve {r['reserve']}")
        for lim in r["limitations"] or ["none"]:
            print("  LIMITATION:", lim)
        for line in r["verified"].splitlines():
            print("    " + line)
    print(f"Settings correct for {correct} of {len(GOALS)} goals at {size_label}")
    print()