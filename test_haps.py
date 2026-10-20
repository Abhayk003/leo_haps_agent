from link_model import haps_link

print("HAPS elev   Distance   SNR clear  Cap clear    SNR rain   Cap rain    Delay")
for el in [30, 45, 60, 89]:
    clear = haps_link(el, raining=False)
    rain = haps_link(el, raining=True)
    print(f"{el:5d} deg   {clear['distance_km']:5.1f} km   "
          f"{clear['snr_db']:5.1f} dB  {clear['capacity_mbps']:5.0f} Mbps   "
          f"{rain['snr_db']:5.1f} dB  {rain['capacity_mbps']:5.0f} Mbps   "
          f"{clear['delay_ms']:.3f} ms")