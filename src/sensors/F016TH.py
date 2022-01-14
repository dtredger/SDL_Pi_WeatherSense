# F016TH Sensor (small white indoor sensor)
#
# Sends data as device_id 19

import json

import config
from src.helpers import *
from src import influxdb_client as influx_cli

# Sample json parsed from sLine:
# {
#   "time": "2021-06-07 23:32:43",
#   "model": "SwitchDoc Labs F016TH Thermo-Hygrometer",
#   "device": 187,
#   "modelnumber": 5,
#   "channel": 1,
#   "battery": "OK",
#   "temperature_F": 77.200,
#   "humidity": 67,
#   "mic": "CRC"
# }
#
# * Interval between readings appears to be ~53s
#
# * Time appears to be set to the timezone of the receiving computer (ie Raspberry pi system time) before arriving here -- possibly by rtl_433


def process_F016TH(json_data):
    if (config.SWDEBUG):
        print('Processing F016TH data')
        print(json.dumps(json_data))

    utc_time = convert_iso_timezone(json_data["time"])
    temp_celcius = fahrenheit_to_celsius(json_data["temperature_F"])

    if (config.ENABLE_INFLUXDB == True):
        temp_record = influx_cli.format_point(measurement='temperature',
                                              timestamp=utc_time,
                                              device_id=json_data["device"],
                                              field_val=temp_celcius)
        humid_record = influx_cli.format_point(measurement='humidity',
                                               timestamp=utc_time,
                                               device_id=json_data["device"],
                                               field_val=json_data["humidity"])

        records = [temp_record, humid_record]

        if json_data["battery"] != 'OK':
            battery = influx_cli.format_point(measurement='battery',
                                              timestamp=utc_time,
                                              device_id=json_data["device"],
                                              field_val=json_data["battery"])
            records.append(battery)

        insert = influx_cli.insert_records(config.INFLUX_DATABASE, records)

        if (config.SWDEBUG):
            if insert == True:
                print(f"Saved Points to #{config.INFLUX_DATABASE}:")
                print(str(records))
            else:
                print("Points not saved")
                print(str(records))

        return insert
