import numpy as np
from skyfield.api import load, wgs84

ts = load.timescale()
satellites = load.tle_file("oneweb.tle")
rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

t0 = ts.now()
minutes = np.arange(0, 181, 2)
times = ts.tt_jd(t0.tt + minutes / 1440)

elev = np.zeros((len(satellites), len(minutes)))
for i, sat in enumerate(satellites):
    alt, az, dist = (sat - rvce).at(times).altaz()
    elev[i] = alt.degrees

rng = np.random.default_rng(seed=42)

print("Fraction   Satellites   No satellite above 10 deg   Best between 10-30 deg")
for fraction in [1.0, 0.5, 0.25, 0.1, 0.05]:
    n = int(len(satellites) * fraction)
    chosen = rng.choice(len(satellites), size=n, replace=False)
    best = elev[chosen].max(axis=0)
    no_sat = np.mean(best < 10) * 100
    low = np.mean((best >= 10) & (best < 30)) * 100
    print(f"{fraction * 100:6.0f}%    {n:6d}       {no_sat:6.0f}%                     {low:6.0f}%")