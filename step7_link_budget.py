import numpy as np
import itur
from skyfield.api import load, wgs84

# --- Satellite pass (same as Task 5) ---
ts = load.timescale()
satellites = load.tle_file("starlink.tle")
by_name = {sat.name: sat for sat in satellites}
sat = by_name["STARLINK-31755"]

lat, lon = 12.9237, 77.4987
rvce = wgs84.latlon(lat, lon, elevation_m=900)

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
elev_deg = alt.degrees
distance_km = dist.km

# --- Link budget assumptions ---
frequency_ghz = 12.0
eirp_dbw = 36.0
dish_diameter_m = 0.5
dish_efficiency = 0.6
noise_temp_k = 150.0
bandwidth_hz = 250e6
boltzmann_db = -228.6
p = 0.1

# --- Fixed receiver numbers ---
wavelength_m = 3e8 / (frequency_ghz * 1e9)
rx_gain_dbi = 10 * np.log10(dish_efficiency * (np.pi * dish_diameter_m / wavelength_m) ** 2)
noise_dbw = boltzmann_db + 10 * np.log10(noise_temp_k) + 10 * np.log10(bandwidth_hz)

print(f"Receive antenna gain: {rx_gain_dbi:.1f} dBi")
print(f"Noise power:          {noise_dbw:.1f} dBW")
print()

fspl_db = 20 * np.log10(distance_km) + 20 * np.log10(frequency_ghz) + 92.45

print("Elev     FSPL      SNR clear   SNR heavy rain")
for k in range(20):
    Ag, Ac, Ar, As, A = itur.atmospheric_attenuation_slant_path(
        lat, lon, frequency_ghz * itur.u.GHz, elev_deg[k], p,
        dish_diameter_m * itur.u.m, return_contributions=True)

    pr_clear = eirp_dbw + rx_gain_dbi - fspl_db[k] - Ag.value
    pr_rain = eirp_dbw + rx_gain_dbi - fspl_db[k] - A.value

    snr_clear = pr_clear - noise_dbw
    snr_rain = pr_rain - noise_dbw

    print(f"{elev_deg[k]:5.1f}   {fspl_db[k]:6.1f} dB   {snr_clear:6.1f} dB    {snr_rain:6.1f} dB")