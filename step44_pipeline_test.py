from pipeline import run_pipeline

BUDGET = 15

GOALS = [
    "Avoid all outages first. Then make the average throughput as high as possible.",
    "Use HAPS as little as possible, but never allow an outage.",
    "Keep 7 HAPS minutes in reserve for other users. Use the rest to maximise throughput.",
    "Only use HAPS when it adds at least 100 Mbps.",
    "HAPS should be an emergency backup only.",
    "Get the highest possible average throughput.",
    "Use at most 10 HAPS minutes, and only where HAPS adds at least 150 Mbps.",
    "Keep the number of handovers below 30.",
    "Always choose the link with the lowest delay.",
    "Use HAPS only between minute 100 and minute 130.",
    "Make sure there are no outages and use exactly 20 HAPS minutes.",
]

for i, goal in enumerate(GOALS, start=1):
    r = run_pipeline(goal, BUDGET)
    print(f"=== Goal {i}: {goal}")
    print("  Tools called:", ", ".join(name for name, args in r["calls"]))
    if r["limitations"]:
        for lim in r["limitations"]:
            print("  LIMITATION:", lim)
    else:
        print("  LIMITATION: none")
    print("  Final plan:", r["plan"])
    for line in r["verified"].splitlines():
        print("    " + line)
    print()