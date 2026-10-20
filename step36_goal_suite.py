from agent import run_agent, extract_plan
from agent_tools import evaluate_plan

BUDGET = 15

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


correct = 0
for i, (goal, expected) in enumerate(GOALS, start=1):
    answer, calls = run_agent(goal, BUDGET, verbose=False)

    chosen = None
    for name, args in calls:
        if name == "build_plan":
            try:
                chosen = normalise(args)
            except (KeyError, ValueError):
                chosen = "invalid arguments"

    ok = chosen == expected
    correct += ok

    print(f"Goal {i}: {goal}")
    print(f"  Expected settings: {expected}")
    print(f"  Chosen settings:   {chosen}   {'CORRECT' if ok else 'WRONG'}")

    plan = extract_plan(answer)
    if plan is None:
        print("  Verified result:   invalid answer (no single FINAL PLAN line)")
    else:
        print(f"  Final plan:        {plan}")
        for line in evaluate_plan(plan).splitlines():
            print(f"    {line}")
    print()

print(f"Settings correct for {correct} of {len(GOALS)} goals")