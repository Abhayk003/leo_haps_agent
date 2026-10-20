import numpy as np
from skyfield.api import load, wgs84

ts = load.timescale()
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=tle"
satellites = load.tle_file(url, filename="oneweb.tle")
print("Loaded", len(satellites), "OneWeb satellites")

rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

t0 = ts.now()
minutes = np.arange(0, 61, 2)
times = ts.tt_jd(t0.tt + minutes / 1440)

best_elev = np.full(len(minutes), -90.0)
count_above_10 = np.zeros(len(minutes), dtype=int)
count_above_25 = np.zeros(len(minutes), dtype=int)

for sat in satellites:
    alt, az, dist = (sat - rvce).at(times).altaz()
    elev = alt.degrees
    best_elev = np.maximum(best_elev, elev)
    count_above_10 += (elev > 10)
    count_above_25 += (elev > 25)

print()
for m, e, c10, c25 in zip(minutes, best_elev, count_above_10, count_above_25):
    print(f"t + {m:2d} min   highest {e:5.1f} deg   above 10 deg: {c10:3d}   above 25 deg: {c25:3d}")

print()
print(f"Lowest 'highest elevation': {best_elev.min():.1f} deg")
print(f"Time with best satellite below 30 deg: {np.mean(best_elev < 30) * 100:.0f}%")