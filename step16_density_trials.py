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

fractions = [1.0, 0.75, 0.5, 0.35, 0.25, 0.15, 0.10, 0.07, 0.05]
trials = 20

print("Fraction  Sats   No satellite above 10 deg   Best between 10-30 deg")
for fraction in fractions:
    n = int(len(satellites) * fraction)
    no_sat_results = []
    low_results = []
    for trial in range(trials):
        chosen = rng.choice(len(satellites), size=n, replace=False)
        best = elev[chosen].max(axis=0)
        no_sat_results.append(np.mean(best < 10) * 100)
        low_results.append(np.mean((best >= 10) & (best < 30)) * 100)
    print(f"{fraction * 100:5.0f}%   {n:4d}    "
          f"{np.mean(no_sat_results):5.1f} +/- {np.std(no_sat_results):4.1f} %          "
          f"{np.mean(low_results):5.1f} +/- {np.std(low_results):4.1f} %")