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

print("Pass starts (UTC):", t_rise.utc_strftime())
print("Pass ends   (UTC):", t_set.utc_strftime())

sample_times = ts.linspace(t_rise, t_set, 20)
alt, az, dist = (sat - rvce).at(sample_times).altaz()
height = wgs84.height_of(sat.at(sample_times)).km

print()
print("Time (UTC)   Elevation   Distance   Satellite altitude")
for k in range(20):
    print(f"{sample_times[k].utc_strftime('%H:%M:%S')}    "
          f"{alt.degrees[k]:5.1f} deg  {dist.km[k]:7.1f} km   {height[k]:6.1f} km")