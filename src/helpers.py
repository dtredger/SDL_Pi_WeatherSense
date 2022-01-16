import random
import datetime
import pytz
import math

# def nowStr():
#     return (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def randomadd(value, spread):
    return round(value + random.uniform(-spread, spread), 2)

def fahrenheit_to_celsius(value):
    celcius = (value - 32.0) / (9.0 / 5.0)
    return round(celcius, 2)

# returns the timestamp with 13-digit precision (ms)
def convert_iso_timezone(iso_str, zone_str='EST'):
    dt_obj = datetime.datetime.fromisoformat(iso_str)
    zone = pytz.timezone(zone_str)
    return zone.localize(dt_obj).astimezone(pytz.utc).isoformat()


# https://www.engineeringtoolbox.com/specific-relative-humidity-air-d_688.html
# specific humidity can be expressed as:
#
#   x = 0.622 φ ρws / (ρ - ρ_ws) 100%
#
# --- where ---
#   x = specific humidity (humidity ratio) of air vapor mixture (kgh2o/kgdry_air)
#   φ = relative humidity (%)
#   ρ_ws = density of water vapor (kg/m3)
#   ρ = density of the moist or humid air (kg/m3)
#
# For humans relative humidity below 25% feels uncomfortable dry. Relative humidity above 60% feels uncomfortable wet. Human comfort requires the relative humidity to be in the range 25 - 60% RH.
#
# returns g/m^3
def absolute_humidity(temp, rel_hum):
    return (6.112 * math.e**((17.67 * temp)/(temp + 243.5)) * rel_hum * 2.1674) / (273.15 + temp)
