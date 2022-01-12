import random
import datetime


def nowStr():
    return (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def randomadd(value, spread):
    return round(value + random.uniform(-spread, spread), 2)


def enqueue_output(src, out, queue):
    for line in iter(out.readline, b''):
        queue.put((src, line))
    out.close()

def fahrenheit_to_celsius(value):
    celcius = (value - 32.0) / (9.0 / 5.0)
    return round(celcius, 2)

import pytz
import datetime
def isoformat_to_utc(iso_str, zone_str='EST'):
    datetime_obj = datetime.datetime.fromisoformat(iso_str)
    zone = pytz.timezone(zone_str)
    zone.localize(dt).astimezone(pytz.utc)
