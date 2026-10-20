from simulator import load_options, run
from policies import greedy_with_budget, haps_as_fallback, make_perfect_planner

options = load_options()
budgets = [0, 2, 4, 6, 8, 10, 12, 15, 18, 22, 36]

print("Budget |  Greedy         |  Fallback       |  Perfect planner")
print("(min)  |  Mbps   Outage  |  Mbps   Outage  |  Mbps   Outage  HAPS used")
for b in budgets:
    g = run(greedy_with_budget, options, budget=b)
    f = run(haps_as_fallback, options, budget=b)
    p = run(make_perfect_planner(options, b), options, budget=b)
    print(f"{b:5d}  | {g['avg_throughput_mbps']:6.1f}  {g['outage_min']:4d}    | "
          f"{f['avg_throughput_mbps']:6.1f}  {f['outage_min']:4d}    | "
          f"{p['avg_throughput_mbps']:6.1f}  {p['outage_min']:4d}    {p['haps_min']:4d}")