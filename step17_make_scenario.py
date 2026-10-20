import csv
import numpy as np
from skyfield.api import load, wgs84

FRACTION = 0.15
SEED = 7
DURATION_MIN = 180
STEP_MIN = 1
MIN_ELEV_DEG = 10.0

ts = load.timescale()
satellites = load.tle_file("oneweb.tle")
rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

rng = np.random.default_rng(seed=SEED)
n = int(len(satellites) * FRACTION)
chosen = rng.choice(len(satellites), size=n, replace=False)
subset = [satellites[i] for i in chosen]

t0 = ts.now()
minutes = np.arange(0, DURATION_MIN + 1, STEP_MIN)
times = ts.tt_jd(t0.tt + minutes / 1440)
print("Scenario start (UTC):", t0.utc_strftime())

rows = []
best = np.full(len(minutes), -90.0)
for sat in subset:
    alt, az, dist = (sat - rvce).at(times).altaz()
    elev = alt.degrees
    best = np.maximum(best, elev)
    for k in range(len(minutes)):
        if elev[k] > MIN_ELEV_DEG:
            rows.append([minutes[k], sat.name, round(elev[k], 2), round(dist.km[k], 1)])

rows.sort(key=lambda r: (r[0], -r[2]))

with open("scenario_leo.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time_min", "satellite", "elevation_deg", "distance_km"])
    writer.writerows(rows)

print("Satellites in subset:", n)
print("Rows written:", len(rows))
print(f"No satellite above 10 deg: {np.mean(best < 10) * 100:.1f}%")
print(f"Best between 10-30 deg:    {np.mean((best >= 10) & (best < 30)) * 100:.1f}%")