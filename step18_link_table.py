import csv
from link_model import leo_link, haps_link

HAPS_ELEV_DEG = 45.0
RAIN_START_MIN = 60
RAIN_END_MIN = 120
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

with open("scenario_links.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time_min", "raining", "option", "elevation_deg",
                     "snr_db", "capacity_mbps", "delay_ms"])
    writer.writerows(out)

print("Rows written:", len(out))
for check_t in [0, 90]:
    print()
    print(f"Options at minute {check_t} (raining = {is_raining(check_t)}):")
    for r in out:
        if r[0] == check_t:
            print(f"  {r[2]:15s} elev {r[3]:5.1f}  SNR {r[4]:6.1f} dB  "
                  f"capacity {r[5]:7.1f} Mbps  delay {r[6]:.3f} ms")