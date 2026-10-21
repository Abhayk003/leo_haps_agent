from simulator import load_options, run, usable_capacity
from policies import (best_leo, leo_only, greedy_with_budget, haps_as_fallback,
                      make_perfect_planner, make_hybrid_planner)

BUDGET = 15
SIZES = [
    ("25%", "scenario_links_25.csv", "scenario_links_forecast_25.csv"),
    ("15%", "scenario_links.csv", "scenario_links_forecast.csv"),
    ("10%", "scenario_links_10.csv", "scenario_links_forecast_10.csv"),
]


def dead_count(options):
    count = 0
    for opts in options.values():
        leo = best_leo(opts)
        if leo is None or usable_capacity(leo) == 0.0:
            count += 1
    return count


for label, true_file, forecast_file in SIZES:
    truth = load_options(true_file)
    forecast = load_options(forecast_file)

    print(f"===== Constellation {label} =====")
    print(f"Minutes with no usable LEO: real weather {dead_count(truth)}, forecast {dead_count(forecast)}")
    print(f"HAPS budget: {BUDGET} minutes")

    policies = [
        ("LEO only", leo_only),
        ("Greedy with budget", greedy_with_budget),
        ("HAPS as fallback", haps_as_fallback),
        ("Perfect planner (true weather)", make_perfect_planner(truth, BUDGET)),
        ("Planner on forecast", make_perfect_planner(forecast, BUDGET)),
        ("Hybrid, reserve 3", make_hybrid_planner(forecast, BUDGET, 3)),
        ("Hybrid, reserve 6", make_hybrid_planner(forecast, BUDGET, 6)),
    ]

    print("Policy                            Mbps    Outage  HAPS used")
    for name, policy in policies:
        s = run(policy, truth, budget=BUDGET)
        print(f"{name:32s}  {s['avg_throughput_mbps']:6.1f}   {s['outage_min']:4d}    {s['haps_min']:4d}")
    print()