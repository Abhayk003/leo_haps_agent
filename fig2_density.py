import os
import numpy as np
import matplotlib.pyplot as plt
from skyfield.api import load, wgs84

os.makedirs("figures", exist_ok=True)

ts = load.timescale()
satellites = load.tle_file("oneweb.tle")
rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)
t0 = ts.utc(2026, 10, 20, 8, 55, 10)
minutes = np.arange(0, 181, 2)
times = ts.tt_jd(t0.tt + minutes / 1440)

elev = np.zeros((len(satellites), len(minutes)))
for i, sat in enumerate(satellites):
    alt, az, dist = (sat - rvce).at(times).altaz()
    elev[i] = alt.degrees

rng = np.random.default_rng(seed=42)
fractions = [1.0, 0.75, 0.5, 0.35, 0.25, 0.15, 0.10, 0.07, 0.05]
trials = 20

no_mean, no_std, low_mean, low_std = [], [], [], []
print("Fraction  No satellite (mean +/- std)   Weak 10-30 deg (mean +/- std)")
for fraction in fractions:
    n = int(len(satellites) * fraction)
    no_sat, low = [], []
    for trial in range(trials):
        chosen = rng.choice(len(satellites), size=n, replace=False)
        best = elev[chosen].max(axis=0)
        no_sat.append(np.mean(best < 10) * 100)
        low.append(np.mean((best >= 10) & (best < 30)) * 100)
    no_mean.append(np.mean(no_sat))
    no_std.append(np.std(no_sat))
    low_mean.append(np.mean(low))
    low_std.append(np.std(low))
    print(f"{fraction * 100:6.0f}%    {no_mean[-1]:5.1f} +/- {no_std[-1]:4.1f} %"
          f"              {low_mean[-1]:5.1f} +/- {low_std[-1]:4.1f} %")

percent = [f * 100 for f in fractions]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.errorbar(percent, no_mean, yerr=no_std, marker="o", capsize=4,
            label="No satellite above 10°")
ax.errorbar(percent, low_mean, yerr=low_std, marker="s", linestyle="--", capsize=4,
            label="Best satellite between 10° and 30°")
for p in [25, 15, 10]:
    ax.axvline(p, color="grey", linestyle=":", linewidth=1)
    ax.text(p, ax.get_ylim()[1] * 0.95, f" {p}%", color="grey")

ax.invert_xaxis()
ax.set_xlabel("Operational fraction of the OneWeb constellation (%)")
ax.set_ylabel("Percentage of time (%)")
ax.set_title("LEO coverage over RVCE vs constellation density\n(mean ± std over 20 random subsets, 3 hours)")
ax.grid(True)
ax.legend()
fig.tight_layout()
fig.savefig("figures/fig2_density.png", dpi=150)
print("Saved figures/fig2_density.png")
plt.show()