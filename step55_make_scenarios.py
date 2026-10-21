import csv
import numpy as np
from skyfield.api import load, wgs84
from link_model import leo_link, haps_link

SEED = 7
DURATION_MIN = 180
MIN_ELEV_DEG = 10.0
HAPS_ELEV_DEG = 45.0
FRACTIONS = [0.25, 0.10]
REAL_RAIN = (60, 120)
FORECAST_RAIN = (50, 110)
HEADER = ["time_min", "raining", "option", "elevation_deg", "snr_db", "capacity_mbps", "delay_ms"]

ts = load.timescale()
satellites = load.tle_file("oneweb.tle")
rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)
t0 = ts.utc(2026, 10, 20, 8, 55, 10)
minutes = np.arange(0, DURATION_MIN + 1)
times = ts.tt_jd(t0.tt + minutes / 1440)


def make_leo_rows(fraction):
    rng = np.random.default_rng(seed=SEED)
    n = int(len(satellites) * fraction)
    chosen = rng.choice(len(satellites), size=n, replace=False)
    rows = []
    best = np.full(len(minutes), -90.0)
    for i in chosen:
        sat = satellites[i]
        alt, az, dist = (sat - rvce).at(times).altaz()
        elev = alt.degrees
        best = np.maximum(best, elev)
        for k in range(len(minutes)):
            if elev[k] > MIN_ELEV_DEG:
                rows.append([int(minutes[k]), sat.name, round(elev[k], 2), round(dist.km[k], 1)])
    rows.sort(key=lambda r: (r[0], -r[2]))
    return n, rows, best


def print_stats(label, n, rows, best):
    print(f"{label}: {n} satellites, {len(rows)} rows, "
          f"no satellite above 10 deg {np.mean(best < 10) * 100:.1f}%, "
          f"best between 10-30 deg {np.mean((best >= 10) & (best < 30)) * 100:.1f}%")


def link_row(t, name, elev, r, raining):
    return [t, int(raining), name, elev,
            round(r["snr_db"], 2), round(r["capacity_mbps"], 1), round(r["delay_ms"], 3)]


def write_links(path, leo_rows, both, haps_both, rain):
    start, end = rain
    out = []
    for (t, name, elev, dist), (clear, wet) in zip(leo_rows, both):
        raining = start <= t < end
        out.append(link_row(t, name, elev, wet if raining else clear, raining))
    for t in range(DURATION_MIN + 1):
        raining = start <= t < end
        out.append(link_row(t, "HAPS", HAPS_ELEV_DEG, haps_both[1] if raining else haps_both[0], raining))
    out.sort(key=lambda r: (r[0], -r[5]))
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(out)
    return len(out)


n, rows, best = make_leo_rows(0.15)
print_stats("Check, 15% (should be close to 498 rows, 1.7%, 38.1%)", n, rows, best)
print()

haps_both = (haps_link(HAPS_ELEV_DEG, raining=False), haps_link(HAPS_ELEV_DEG, raining=True))

for fraction in FRACTIONS:
    tag = str(round(fraction * 100))
    n, rows, best = make_leo_rows(fraction)
    print_stats(f"{tag}%", n, rows, best)

    with open(f"scenario_leo_{tag}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_min", "satellite", "elevation_deg", "distance_km"])
        writer.writerows(rows)

    print("  Computing clear and rain link values...")
    both = [(leo_link(elev, dist, raining=False), leo_link(elev, dist, raining=True))
            for t, name, elev, dist in rows]

    count = write_links(f"scenario_links_{tag}.csv", rows, both, haps_both, REAL_RAIN)
    write_links(f"scenario_links_forecast_{tag}.csv", rows, both, haps_both, FORECAST_RAIN)
    print(f"  Wrote scenario_leo_{tag}.csv, scenario_links_{tag}.csv ({count} rows), "
          f"scenario_links_forecast_{tag}.csv")
    print()