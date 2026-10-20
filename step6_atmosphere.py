import itur

lat = 12.9237
lon = 77.4987
frequency = 12.0 * itur.u.GHz
antenna_diameter = 0.5 * itur.u.m
p = 0.1

elevations = [10, 20, 30, 45, 60, 90]

print("Elev    Gas     Cloud   Rain    Scint   Total   (all in dB)")
for el in elevations:
    Ag, Ac, Ar, As, A = itur.atmospheric_attenuation_slant_path(
        lat, lon, frequency, el, p, antenna_diameter,
        return_contributions=True)
    print(f"{el:3d}    {Ag.value:5.2f}   {Ac.value:5.2f}   {Ar.value:5.2f}   "
          f"{As.value:5.2f}   {A.value:5.2f}")