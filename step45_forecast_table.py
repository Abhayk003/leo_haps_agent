import csv
from link_model import leo_link, haps_link
from simulator import load_options, usable_capacity
from policies import best_leo
from agent_tools import to_ranges

HAPS_ELEV_DEG = 45.0
RAIN_START_MIN = 50
RAIN_END_MIN = 110
DURATION_MIN = 180


def is_raining(t):
    return RAIN_START_MIN <= t < RAIN_END_MIN


leo_rows = []
with open("scenario_leo.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        leo_rows.append(row)

out = []
for row in leo_rows:
    t = int(row["time_min"])
    elev = float(row["elevation_deg"])
    dist = float(row["distance_km"])
    rain = is_raining(t)
    r = leo_link(elev, dist, raining=rain)
    out.append([t, int(rain), row["satellite"], elev,
                round(r["snr_db"], 2), round(r["capacity_mbps"], 1), round(r["delay_ms"], 3)])

for t in range(DURATION_MIN + 1):
    rain = is_raining(t)
    r = haps_link(HAPS_ELEV_DEG, raining=rain)
    out.append([t, int(rain), "HAPS", HAPS_ELEV_DEG,
                round(r["snr_db"], 2), round(r["capacity_mbps"], 1), round(r["delay_ms"], 3)])

out.sort(key=lambda r: (r[0], -r[5]))

with open("scenario_links_forecast.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time_min", "raining", "option", "elevation_deg",
                     "snr_db", "capacity_mbps", "delay_ms"])
    writer.writerows(out)

print("Rows written:", len(out))

def dead_minutes(options):
    dead = []
    for t, opts in options.items():
        leo = best_leo(opts)
        if leo is None or usable_capacity(leo) == 0.0:
            dead.append(t)
    return dead


truth = load_options("scenario_links.csv")
forecast = load_options("scenario_links_forecast.csv")
print("No usable LEO, real weather:     ", to_ranges(dead_minutes(truth)))
print("No usable LEO, forecast weather: ", to_ranges(dead_minutes(forecast)))