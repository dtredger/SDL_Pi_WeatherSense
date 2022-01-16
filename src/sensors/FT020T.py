# FT020T Sensor (outdoor anemometer sensor)
#
# Sends data as device_id 12

import json

import config
from src.helpers import *
from src import influxdb_client as influx_cli

# Sample json parsed from sLine:
# {
#   "time": "2021-06-07 23:32:11",
#   "model": "SwitchDoc Labs FT020T AIO",
#   "device": 12,
#   "id": 0,
#   "batterylow": 0,
#   "avewindspeed": 0,
#   "gustwindspeed": 0,
#   "winddirection": 9,
#   "cumulativerain": 255,
#   "temperature": 1177,
#   "humidity": 66,
#   "light": 0,
#   "uv": 0,
#   "mic": "CRC"
# }
# Note that time appears to be set to the timezone of the receiving computer (ie Raspberry pi system time) before arriving here -- possibly by rtl_433


# RH cannot be above 100, so throw out those cases
def parse_humidity(raw_humidity):
    if (raw_humidity > 100.0):
        if (config.SWDEBUG):
            print("error--->>> Humidity reading from FT020T")
            print('This is the raw humidity: ' + str(raw_humidity))
        return False
    else:
        return raw_humidity

# The data comes from the FT020T as an a raw_temp that is neither
# celcius nor fahrenheit
def parse_temperature(raw_temp):
    temp_f = (raw_temp - 400) / 10.0
    temp_celcius = fahrenheit_to_celsius(temp_f)
    if (temp_celcius > 60):
        if (config.SWDEBUG):
            print("error--->>> Temperature reading from FT020T")
            print('This is the raw temperature: ' + str(raw_temp))
        return False
    else:
        return temp_celcius

# windspeed sent 10 higher than real value
def parse_wind_data(speed, gust, direction):
    speed = round(speed / 10.0, 1)
    gust = round(gust / 10.0, 1)
    return speed, gust, direction

# Transformations in this method are not documented
def parse_light(light, uv):
    if (light >= 0x1fffa): # 0x1fffa == 131066
        light = light | 0x7fff0000 # 0x7fff0000 == 2147418112

    if (uv >= 0xfa):
        uv = uv | 0x7f00

    uv_index = round(uv / 10.0, 1)
    return light, uv_index

# put data into influxdb json format if a value is given
def format_record(name, value, timestamp, device_id):
    return influx_cli.format_point(measurement=name,
                                   timestamp=timestamp,
                                   device_id=device_id,
                                   field_val=value)


def process_FT020T(json_data):
    if (config.SWDEBUG):
        print("processing raw FT020T Data:")
        print(json.dumps(json_data))

    utc_time = convert_iso_timezone(json_data["time"])

    temp_celcius = parse_temperature(json_data["temperature"])
    humidity = parse_humidity(json_data["humidity"])
    windspeed_kmh, windgust_kmh, wind_direction = parse_wind_data(
        json_data["avewindspeed"], json_data["gustwindspeed"],json_data["winddirection"]
    )
    cumulative_rain = round(json_data["cumulativerain"] / 10.0, 1)
    light_visible, uv_index = parse_light(json_data["light"], json_data["uv"])

    # batterylow: 0 means battery is OK
    if (json_data['batterylow'] == 0):
        battery = False
    else:
        battery = "LOW"

    if config.ENABLE_INFLUXDB == True:
        records = []

        if temp_celcius:
            pt = format_record("temperature", temp_celcius, utc_time, json_data["device"])
            records.append(pt)
        if humidity:
            pt = format_record("humidity", humidity, utc_time, json_data["device"])
            records.append(pt)
        if windspeed_kmh:
            pt = format_record("windspeed_kmh", windspeed_kmh, utc_time, json_data["device"])
            records.append(pt)
        if windgust_kmh:
            pt = format_record("windgust_kmh", windgust_kmh, utc_time, json_data["device"])
            records.append(pt)
        if wind_direction:
            pt = format_record("wind_direction", wind_direction, utc_time, json_data["device"])
            records.append(pt)
        if cumulative_rain:
            pt = format_record("cumulative_rain", cumulative_rain, utc_time, json_data["device"])
            records.append(pt)
        if light_visible:
            pt = format_record("light_visible", light_visible, utc_time, json_data["device"])
            records.append(pt)
        if uv_index:
            pt = format_record("uv_index", uv_index, utc_time, json_data["device"])
            records.append(pt)
        if battery:
            pt = format_record("battery", battery, utc_time, json_data["device"])
            records.append(pt)

        if config.LOG_ABSOLUTE_HUMIDITY == True and temp_celcius and humidity
            hum_absolute = absolute_humidity(temp_celcius, humidity)
            pt = format_record("hum_absolute", hum_absolute, utc_time, json_data["device"])
            records.append(pt)

        insert = influx_cli.insert_records(config.INFLUX_DATABASE, records)

        if (config.SWDEBUG):
            if insert == True:
                print(f"Saved Points to #{config.INFLUX_DATABASE}:")
                print(str(records))
            else:
                print("Points not saved:")
                print(str(records))

        return insert
