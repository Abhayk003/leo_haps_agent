import numpy as np
import itur

# Ground station (RVCE)
LAT = 12.9237
LON = 77.4987

# LEO downlink assumptions
FREQUENCY_GHZ = 12.0
EIRP_DBW = 36.0
DISH_DIAMETER_M = 0.5
DISH_EFFICIENCY = 0.6
NOISE_TEMP_K = 150.0
BANDWIDTH_HZ = 250e6
RAIN_P = 0.1

# HAPS downlink assumptions
HAPS_ALTITUDE_KM = 20.0
HAPS_FREQUENCY_GHZ = 2.6
HAPS_EIRP_DBW = 30.0
HAPS_RX_GAIN_DBI = 0.0
HAPS_NOISE_TEMP_K = 500.0
HAPS_BANDWIDTH_HZ = 100e6

# Physical constants
BOLTZMANN_DB = -228.6
SPEED_OF_LIGHT_KM_S = 299792.458


def fspl_db(distance_km, frequency_ghz):
    return 20 * np.log10(distance_km) + 20 * np.log10(frequency_ghz) + 92.45


def antenna_gain_dbi(diameter_m, efficiency, frequency_ghz):
    wavelength_m = 3e8 / (frequency_ghz * 1e9)
    return 10 * np.log10(efficiency * (np.pi * diameter_m / wavelength_m) ** 2)


def noise_power_dbw(noise_temp_k, bandwidth_hz):
    return BOLTZMANN_DB + 10 * np.log10(noise_temp_k) + 10 * np.log10(bandwidth_hz)


def shannon_capacity_mbps(snr_db, bandwidth_hz):
    snr_linear = 10 ** (snr_db / 10)
    return bandwidth_hz * np.log2(1 + snr_linear) / 1e6


def atmospheric_loss_db(elev_deg, frequency_ghz, raining):
    Ag, Ac, Ar, As, A = itur.atmospheric_attenuation_slant_path(
        LAT, LON, frequency_ghz * itur.u.GHz, elev_deg, RAIN_P,
        DISH_DIAMETER_M * itur.u.m, return_contributions=True)
    if raining:
        return A.value
    return Ag.value


def leo_link(elev_deg, distance_km, raining):
    gain = antenna_gain_dbi(DISH_DIAMETER_M, DISH_EFFICIENCY, FREQUENCY_GHZ)
    noise = noise_power_dbw(NOISE_TEMP_K, BANDWIDTH_HZ)
    total_loss = fspl_db(distance_km, FREQUENCY_GHZ) + atmospheric_loss_db(elev_deg, FREQUENCY_GHZ, raining)
    snr = EIRP_DBW + gain - total_loss - noise
    return {
        "snr_db": snr,
        "capacity_mbps": shannon_capacity_mbps(snr, BANDWIDTH_HZ),
        "delay_ms": distance_km / SPEED_OF_LIGHT_KM_S * 1000,
    }


def haps_link(elev_deg, raining):
    distance_km = HAPS_ALTITUDE_KM / np.sin(np.radians(elev_deg))
    noise = noise_power_dbw(HAPS_NOISE_TEMP_K, HAPS_BANDWIDTH_HZ)
    total_loss = fspl_db(distance_km, HAPS_FREQUENCY_GHZ) + atmospheric_loss_db(elev_deg, HAPS_FREQUENCY_GHZ, raining)
    snr = HAPS_EIRP_DBW + HAPS_RX_GAIN_DBI - total_loss - noise
    return {
        "snr_db": snr,
        "capacity_mbps": shannon_capacity_mbps(snr, HAPS_BANDWIDTH_HZ),
        "delay_ms": distance_km / SPEED_OF_LIGHT_KM_S * 1000,
        "distance_km": distance_km,
    }