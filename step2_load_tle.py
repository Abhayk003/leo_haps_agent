from skyfield.api import load

url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
satellites = load.tle_file(url, filename="starlink.tle")

print("Loaded", len(satellites), "satellites")

first = satellites[0]
print("First satellite:", first.name)
print("Orbit data epoch:", first.epoch.utc_strftime())