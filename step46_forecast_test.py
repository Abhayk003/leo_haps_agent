from simulator import load_options, run
from policies import make_perfect_planner, haps_as_fallback, make_hybrid_planner

BUDGET = 15
truth = load_options("scenario_links.csv")
forecast = load_options("scenario_links_forecast.csv")

rows = [
    ("Perfect planner, true weather", make_perfect_planner(truth, BUDGET)),
    ("Planner on forecast", make_perfect_planner(forecast, BUDGET)),
    ("HAPS as fallback (reactive)", haps_as_fallback),
]
for r in [0, 3, 6, 9]:
    rows.append((f"Hybrid, reserve {r}", make_hybrid_planner(forecast, BUDGET, r)))

print("Policy (all scored on real weather)   Mbps    Outage  HAPS used  Handovers")
for name, policy in rows:
    s = run(policy, truth, budget=BUDGET)
    print(f"{name:36s}  {s['avg_throughput_mbps']:6.1f}   {s['outage_min']:4d}    {s['haps_min']:4d}      {s['handovers']:4d}")