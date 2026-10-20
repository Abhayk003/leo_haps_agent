from skyfield.api import load, wgs84

ts = load.timescale()
satellites = load.tle_file("starlink.tle")

rvce = wgs84.latlon(12.9237, 77.4987, elevation_m=900)

t = ts.now()
print("Time (UTC):", t.utc_strftime())

visible = []
for sat in satellites:
    difference = sat - rvce
    topocentric = difference.at(t)
    alt, az, distance = topocentric.altaz()
    if alt.degrees > 10:
        visible.append((sat.name, alt.degrees, az.degrees, distance.km))

visible.sort(key=lambda row: row[1], reverse=True)

print("Satellites above 10 degrees:", len(visible))
for name, elev, azim, dist in visible[:10]:
    print(f"{name:20s} elevation {elev:5.1f} deg  azimuth {azim:5.1f} deg  distance {dist:7.1f} km")