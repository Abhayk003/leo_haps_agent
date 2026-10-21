import os
import matplotlib.pyplot as plt
from simulator import load_options, run
from policies import greedy_with_budget, haps_as_fallback, make_perfect_planner

os.makedirs("figures", exist_ok=True)
options = load_options("scenario_links.csv")
budgets = list(range(0, 37))

results = {"Greedy with budget": [], "HAPS as fallback": [], "Perfect planner": []}
for b in budgets:
    results["Greedy with budget"].append(run(greedy_with_budget, options, budget=b))
    results["HAPS as fallback"].append(run(haps_as_fallback, options, budget=b))
    results["Perfect planner"].append(run(make_perfect_planner(options, b), options, budget=b))

styles = {"Greedy with budget": "-", "HAPS as fallback": "--", "Perfect planner": ":"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
for name, runs in results.items():
    ax1.plot(budgets, [s["avg_throughput_mbps"] for s in runs],
             linestyle=styles[name], marker="o", markersize=3, label=name)
    ax2.plot(budgets, [s["outage_min"] for s in runs],
             linestyle=styles[name], marker="o", markersize=3, label=name)

ax1.set_xlabel("HAPS budget (minutes)")
ax1.set_ylabel("Average throughput (Mbps)")
ax1.set_title("Throughput")
ax2.set_xlabel("HAPS budget (minutes)")
ax2.set_ylabel("Outage minutes")
ax2.set_title("Outages")
for ax in (ax1, ax2):
    ax.grid(True)
    ax.legend()

fig.suptitle("Effect of the HAPS budget (15% OneWeb subset, real weather, 181 minutes)")
fig.tight_layout()
fig.savefig("figures/fig3_budget_sweep.png", dpi=150)
print("Saved figures/fig3_budget_sweep.png")

for b in [6, 15, 22]:
    line = f"Budget {b:2d}:"
    for name, runs in results.items():
        s = runs[b]
        line += f"  {name} {s['avg_throughput_mbps']:.1f} Mbps / {s['outage_min']} outages;"
    print(line)

plt.show()