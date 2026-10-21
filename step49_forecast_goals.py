from pipeline import run_pipeline

BUDGET = 15
FORECAST_FILE = "scenario_links_forecast.csv"

GOALS = [
    ("Avoid all outages first. Then make the average throughput as high as possible.",
     (15, 0, False, 0)),
    ("Avoid all outages first. Then make the average throughput as high as possible. "
     "The rain forecast may be wrong, so keep some HAPS minutes ready for surprises.",
     (15, 0, False, 3)),
    ("Keep 7 HAPS minutes in reserve for other users. Use the rest to maximise throughput.",
     (8, 0, False, 0)),
    ("Use HAPS as little as possible, but never allow an outage. The weather forecast is unreliable.",
     (15, 0, True, 3)),
    ("Maximise throughput, and hold back 5 HAPS minutes in case the forecast is wrong.",
     (15, 0, False, 5)),
    ("Use at most 10 HAPS minutes, and keep 2 of them ready for unexpected outages.",
     (10, 0, False, 2)),
]


def normalise(args, reserve):
    m = min(int(args["max_haps_minutes"]), BUDGET)
    g = float(args["min_gain_mbps"])
    h = args["minimise_haps_use"]
    if isinstance(h, str):
        h = h.strip().lower() == "true"
    return (m, g, bool(h), reserve)


correct = 0
for i, (goal, expected) in enumerate(GOALS, start=1):
    r = run_pipeline(goal, BUDGET, planning_file=FORECAST_FILE)

    chosen = None
    for name, args in r["calls"]:
        if name == "build_plan":
            try:
                chosen = normalise(args, r["reserve"])
            except (KeyError, ValueError):
                chosen = "invalid arguments"
    ok = chosen == expected
    correct += ok

    print(f"=== Goal {i}: {goal}")
    print(f"  Expected settings: {expected}")
    print(f"  Chosen settings:   {chosen}   {'CORRECT' if ok else 'WRONG'}")
    for lim in r["limitations"] or ["none"]:
        print("  LIMITATION:", lim)
    print("  Final plan:", r["plan"])
    for line in r["verified"].splitlines():
        print("    " + line)
    print()

print(f"Settings correct for {correct} of {len(GOALS)} goals")