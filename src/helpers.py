import random
import datetime
import pytz

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
