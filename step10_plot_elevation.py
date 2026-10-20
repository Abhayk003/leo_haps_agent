import numpy as np
import matplotlib.pyplot as plt
from link_model import leo_link

EARTH_RADIUS_KM = 6371.0
SAT_ALTITUDE_KM = 482.5


def slant_range_km(elev_deg, altitude_km):
    e = np.radians(elev_deg)
    r = EARTH_RADIUS_KM
    return np.sqrt((r + altitude_km) ** 2 - (r * np.cos(e)) ** 2) - r * np.sin(e)


print(f"Check: slant range at 10 deg = {slant_range_km(10, SAT_ALTITUDE_KM):.1f} km")

elevations = np.arange(10, 90, 1)
distances = slant_range_km(elevations, SAT_ALTITUDE_KM)

snr_clear = []
snr_rain = []
cap_clear = []
cap_rain = []
delay = []

for el, d in zip(elevations, distances):
    clear = leo_link(el, d, raining=False)
    rain = leo_link(el, d, raining=True)
    snr_clear.append(clear["snr_db"])
    snr_rain.append(rain["snr_db"])
    cap_clear.append(clear["capacity_mbps"])
    cap_rain.append(rain["capacity_mbps"])
    delay.append(clear["delay_ms"])

fig, axes = plt.subplots(2, 2, figsize=(11, 8))

axes[0, 0].plot(elevations, distances)
axes[0, 0].set_title("Slant range")
axes[0, 0].set_ylabel("Distance (km)")

axes[0, 1].plot(elevations, delay)
axes[0, 1].set_title("One-way propagation delay")
axes[0, 1].set_ylabel("Delay (ms)")

axes[1, 0].plot(elevations, snr_clear, label="Clear sky")
axes[1, 0].plot(elevations, snr_rain, label="Heavy rain (p = 0.1%)")
axes[1, 0].axhline(0, color="grey", linestyle="--")
axes[1, 0].set_title("SNR")
axes[1, 0].set_ylabel("SNR (dB)")
axes[1, 0].legend()

axes[1, 1].plot(elevations, cap_clear, label="Clear sky")
axes[1, 1].plot(elevations, cap_rain, label="Heavy rain (p = 0.1%)")
axes[1, 1].set_title("Shannon capacity")
axes[1, 1].set_ylabel("Capacity (Mbps)")
axes[1, 1].legend()

for ax in axes.flat:
    ax.set_xlabel("Elevation angle (deg)")
    ax.grid(True)

fig.suptitle("LEO downlink performance vs elevation angle (RVCE, 12 GHz, altitude 482.5 km)")
fig.tight_layout()
fig.savefig("elevation_analysis.png", dpi=150)
print("Saved elevation_analysis.png")
plt.show()