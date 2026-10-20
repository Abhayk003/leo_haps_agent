import numpy as np
from skyfield.api import load, wgs84

ts = load.timescale()
satellites = load.tle_file("starlink.tle")
rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

t0 = ts.now()
minutes = np.arange(0, 31, 1)
times = ts.tt_jd(t0.tt + minutes / 1440)

best_elev = np.full(len(minutes), -90.0)
count_above_25 = np.zeros(len(minutes), dtype=int)

for sat in satellites:
    alt, az, dist = (sat - rvce).at(times).altaz()
    elev = alt.degrees
    best_elev = np.maximum(best_elev, elev)
    count_above_25 += (elev > 25)

for m, e, c in zip(minutes, best_elev, count_above_25):
    print(f"t + {m:2d} min   highest elevation {e:5.1f} deg   satellites above 25 deg: {c}")

print()
print(f"Lowest 'highest elevation' over 30 min: {best_elev.min():.1f} deg")