import os
import numpy as np
import matplotlib.pyplot as plt
from simulator import load_options, run
from policies import (leo_only, greedy_with_budget, haps_as_fallback,
                      make_perfect_planner, make_hybrid_planner)

os.makedirs("figures", exist_ok=True)
BUDGET = 15
SIZES = [
    ("25%", "scenario_links_25.csv", "scenario_links_forecast_25.csv"),
    ("15%", "scenario_links.csv", "scenario_links_forecast.csv"),
    ("10%", "scenario_links_10.csv", "scenario_links_forecast_10.csv"),
]
POLICY_NAMES = ["Greedy with budget", "HAPS as fallback", "Planner on forecast",
                "Hybrid, reserve 3", "Perfect planner"]
COLORS = {"LEO only": "C7", "Greedy with budget": "C0", "HAPS as fallback": "C1",
          "Planner on forecast": "C2", "Hybrid, reserve 3": "C3", "Perfect planner": "C4"}

gain = {name: [] for name in POLICY_NAMES}
outage = {name: [] for name in ["LEO only"] + POLICY_NAMES}

for label, true_file, forecast_file in SIZES:
    truth = load_options(true_file)
    forecast = load_options(forecast_file)
    base = run(leo_only, truth, budget=BUDGET)
    outage["LEO only"].append(base["outage_min"])
    policies = {
        "Greedy with budget": greedy_with_budget,
        "HAPS as fallback": haps_as_fallback,
        "Planner on forecast": make_perfect_planner(forecast, BUDGET),
        "Hybrid, reserve 3": make_hybrid_planner(forecast, BUDGET, 3),
        "Perfect planner": make_perfect_planner(truth, BUDGET),
    }
    print(f"{label}: LEO only {base['avg_throughput_mbps']:.1f} Mbps, {base['outage_min']} outages")
    for name in POLICY_NAMES:
        s = run(policies[name], truth, budget=BUDGET)
        gain[name].append(s["avg_throughput_mbps"] - base["avg_throughput_mbps"])
        outage[name].append(s["outage_min"])
        print(f"   {name:22s} gain {gain[name][-1]:+6.1f} Mbps, {s['outage_min']} outages")

x = np.arange(len(SIZES))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))

width = 0.8 / len(POLICY_NAMES)
for k, name in enumerate(POLICY_NAMES):
    offset = (k - (len(POLICY_NAMES) - 1) / 2) * width
    ax1.bar(x + offset, gain[name], width, color=COLORS[name], label=name)

names2 = ["LEO only"] + POLICY_NAMES
width2 = 0.8 / len(names2)
for k, name in enumerate(names2):
    offset = (k - (len(names2) - 1) / 2) * width2
    ax2.bar(x + offset, outage[name], width2, color=COLORS[name], label=name)

for ax in (ax1, ax2):
    ax.set_xticks(x)
    ax.set_xticklabels([label for label, _, _ in SIZES])
    ax.set_xlabel("Operational fraction of the OneWeb constellation")
    ax.grid(True, axis="y")
ax1.set_ylabel("Throughput gain over LEO only (Mbps)")
ax1.set_title("Throughput gain")
ax2.set_ylabel("Outage minutes (of 181)")
ax2.set_title("Outages")
ax2.legend(fontsize=8)

fig.suptitle(f"HAPS policies across constellation sizes (budget {BUDGET} min, scored on real weather)")
fig.tight_layout()
fig.savefig("figures/fig5_sizes.png", dpi=150)
print("Saved figures/fig5_sizes.png")
plt.show()