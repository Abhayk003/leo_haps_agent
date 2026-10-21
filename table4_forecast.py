import csv
import os
from link_model import leo_link, haps_link
from simulator import load_options, run
from policies import haps_as_fallback, make_hybrid_planner, make_perfect_planner

os.makedirs("figures", exist_ok=True)
HAPS_ELEV_DEG = 45.0
DURATION_MIN = 180
BUDGET = 15
RESERVES = [0, 3, 6, 9]
FORECASTS = [
    ("10 min early (50-110)", 50, 110),
    ("10 min late (70-130)", 70, 130),
    ("Too short (65-115)", 65, 115),
    ("Too long (50-130)", 50, 130),
    ("Rain missed", None, None),
]


def to_option(name, elev, r):
    return {"option": name, "raining": False, "elevation_deg": elev,
            "snr_db": round(r["snr_db"], 2),
            "capacity_mbps": round(r["capacity_mbps"], 1),
            "delay_ms": round(r["delay_ms"], 3)}


print("Computing clear and rain values for every row (one time only)...")
rows = []
with open("scenario_leo.csv", newline="") as f:
    for row in csv.DictReader(f):
        t = int(row["time_min"])
        elev = float(row["elevation_deg"])
        dist = float(row["distance_km"])
        clear = to_option(row["satellite"], elev, leo_link(elev, dist, raining=False))
        rain = to_option(row["satellite"], elev, leo_link(elev, dist, raining=True))
        rows.append((t, clear, rain))

haps_clear = to_option("HAPS", HAPS_ELEV_DEG, haps_link(HAPS_ELEV_DEG, raining=False))
haps_rain = to_option("HAPS", HAPS_ELEV_DEG, haps_link(HAPS_ELEV_DEG, raining=True))


def build_options(rain_start, rain_end):
    def raining(t):
        return rain_start is not None and rain_start <= t < rain_end

    options = {}
    for t, clear, rain in rows:
        options.setdefault(t, []).append(rain if raining(t) else clear)
    for t in range(DURATION_MIN + 1):
        options.setdefault(t, []).append(haps_rain if raining(t) else haps_clear)
    return options


truth = load_options("scenario_links.csv")
columns = ["Plan only"] + [f"Reserve {r}" for r in RESERVES]
results = {c: [] for c in columns}

table = [["Forecast (real rain 60-120)"] + columns]
for label, start, end in FORECASTS:
    forecast = build_options(start, end)
    policies = [make_perfect_planner(forecast, BUDGET)]
    policies += [make_hybrid_planner(forecast, BUDGET, r) for r in RESERVES]
    line = [label]
    for column, policy in zip(columns, policies):
        s = run(policy, truth, budget=BUDGET)
        results[column].append(s)
        line.append(f"{s['avg_throughput_mbps']:.1f} / {s['outage_min']}")
    table.append(line)

table.append(["Worst outages"] + [str(max(s["outage_min"] for s in results[c])) for c in columns])
table.append(["Worst Mbps"] + [f"{min(s['avg_throughput_mbps'] for s in results[c]):.1f}" for c in columns])
table.append(["Average Mbps"] + [f"{sum(s['avg_throughput_mbps'] for s in results[c]) / len(results[c]):.1f}"
                                 for c in columns])

with open("figures/table4_forecast.csv", "w", newline="") as f:
    csv.writer(f).writerows(table)

for line in table:
    print(" | ".join(f"{cell:>22s}" if i == 0 else f"{cell:>13s}" for i, cell in enumerate(line)))

perfect = run(make_perfect_planner(truth, BUDGET), truth, budget=BUDGET)
fallback = run(haps_as_fallback, truth, budget=BUDGET)
print()
print(f"For reference: perfect planner {perfect['avg_throughput_mbps']:.1f} / {perfect['outage_min']}, "
      f"HAPS as fallback {fallback['avg_throughput_mbps']:.1f} / {fallback['outage_min']}")
print("Saved figures/table4_forecast.csv  (cells are Mbps / outage minutes)")