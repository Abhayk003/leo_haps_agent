import numpy as np
from skyfield.api import load, wgs84

ts = load.timescale()
satellites = load.tle_file("starlink.tle")
by_name = {sat.name: sat for sat in satellites}
sat = by_name["STARLINK-31755"]

rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

t0 = ts.now()
t1 = ts.tt_jd(t0.tt + 1.0)
times, events = sat.find_events(rvce, t0, t1, altitude_degrees=10)

for i in range(len(events)):
    if events[i] == 0:
        t_rise = times[i]
        break
for j in range(i, len(events)):
    if events[j] == 2:
        t_set = times[j]
        break

sample_times = ts.linspace(t_rise, t_set, 20)
alt, az, dist = (sat - rvce).at(sample_times).altaz()

# --- New part: path loss and delay ---
frequency_ghz = 12.0
speed_of_light_km_s = 299792.458

distance_km = dist.km
fspl_db = 20 * np.log10(distance_km) + 20 * np.log10(frequency_ghz) + 92.45
delay_ms = distance_km / speed_of_light_km_s * 1000

print("Elevation   Distance    FSPL       Delay")
for k in range(20):
    print(f"{alt.degrees[k]:5.1f} deg  {distance_km[k]:7.1f} km  "
          f"{fspl_db[k]:6.1f} dB  {delay_ms[k]:5.2f} ms")