import csv
from link_model import leo_link, haps_link
from simulator import load_options, run
from policies import haps_as_fallback, make_hybrid_planner, make_perfect_planner

HAPS_ELEV_DEG = 45.0
DURATION_MIN = 180
BUDGET = 15
RESERVES = [0, 3, 6, 9]

FORECASTS = [
    ("10 min early", 50, 110),
    ("10 min late", 70, 130),
    ("Too short", 65, 115),
    ("Too long", 50, 130),
    ("Rain missed", None, None),
]


def to_option(name, elev, r):
    return {"option": name, "raining": False, "elevation_deg": elev,
            "snr_db": round(r["snr_db"], 2),
            "capacity_mbps": round(r["capacity_mbps"], 1),
            "delay_ms": round(r["delay_ms"], 3)}


print("Computing clear and rain values for every row (one time only)...")
rows = []
with open("scenario_leo.csv", newline="") as f:
    for row in csv.DictReader(f):
        t = int(row["time_min"])
        elev = float(row["elevation_deg"])
        dist = float(row["distance_km"])
        clear = to_option(row["satellite"], elev, leo_link(elev, dist, raining=False))
        rain = to_option(row["satellite"], elev, leo_link(elev, dist, raining=True))
        rows.append((t, clear, rain))

haps_clear = to_option("HAPS", HAPS_ELEV_DEG, haps_link(HAPS_ELEV_DEG, raining=False))
haps_rain = to_option("HAPS", HAPS_ELEV_DEG, haps_link(HAPS_ELEV_DEG, raining=True))


def build_options(rain_start, rain_end):
    def raining(t):
        return rain_start is not None and rain_start <= t < rain_end

    options = {}
    for t, clear, rain in rows:
        options.setdefault(t, []).append(rain if raining(t) else clear)
    for t in range(DURATION_MIN + 1):
        options.setdefault(t, []).append(haps_rain if raining(t) else haps_clear)
    return options


truth = load_options("scenario_links.csv")

s = run(make_perfect_planner(truth, BUDGET), truth, budget=BUDGET)
print(f"Perfect planner, true weather: {s['avg_throughput_mbps']:.1f} Mbps / {s['outage_min']} outages")
s = run(haps_as_fallback, truth, budget=BUDGET)
print(f"HAPS as fallback (reactive):   {s['avg_throughput_mbps']:.1f} Mbps / {s['outage_min']} outages")
print()
print("Results shown as Mbps / outage minutes, all scored on real weather")
print("Forecast        Plan only       " + "".join(f"Reserve {r:<8d}" for r in RESERVES))

for label, start, end in FORECASTS:
    forecast = build_options(start, end)
    line = f"{label:14s}"
    s = run(make_perfect_planner(forecast, BUDGET), truth, budget=BUDGET)
    line += f"  {s['avg_throughput_mbps']:6.1f} / {s['outage_min']:<3d}   "
    for r in RESERVES:
        s = run(make_hybrid_planner(forecast, BUDGET, r), truth, budget=BUDGET)
        line += f"{s['avg_throughput_mbps']:6.1f} / {s['outage_min']:<3d}   "
    print(line)