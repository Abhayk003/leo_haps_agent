import numpy as np
from skyfield.api import load, wgs84

BLOCKED_ELEV_DEG = 60.0
OPEN_ELEV_DEG = 10.0


def mask_elevation(az_deg):
    north_side = (az_deg >= 315) | (az_deg <= 45)
    south_side = (az_deg >= 135) & (az_deg <= 225)
    blocked = north_side | south_side
    return np.where(blocked, BLOCKED_ELEV_DEG, OPEN_ELEV_DEG)


ts = load.timescale()
satellites = load.tle_file("oneweb.tle")
rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

t0 = ts.now()
minutes = np.arange(0, 61, 2)
times = ts.tt_jd(t0.tt + minutes / 1440)

best_elev = np.full(len(minutes), -90.0)
count_visible = np.zeros(len(minutes), dtype=int)

for sat in satellites:
    alt, az, dist = (sat - rvce).at(times).altaz()
    elev = alt.degrees
    visible = elev > mask_elevation(az.degrees)
    count_visible += visible
    best_elev = np.maximum(best_elev, np.where(visible, elev, -90.0))

print("East-west street canyon, OneWeb")
for m, e, c in zip(minutes, best_elev, count_visible):
    if c == 0:
        print(f"t + {m:2d} min   NO SATELLITE VISIBLE")
    else:
        print(f"t + {m:2d} min   best visible {e:5.1f} deg   visible satellites: {c}")

print()
print(f"Time with no visible satellite:          {np.mean(count_visible == 0) * 100:.0f}%")
print(f"Time with best visible satellite < 30 deg: {np.mean((count_visible > 0) & (best_elev < 30)) * 100:.0f}%")