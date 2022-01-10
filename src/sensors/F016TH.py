# Interval between readings appears to be ~53s

# processes Inside Temperature and Humidity
import config
from src.helpers import *

import json
import sys
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
import datetime
import traceback

from src import influxdb_client

# sample sLine
# '{"time" : "2021-06-07 23:32:43", "model" : "SwitchDoc Labs F016TH Thermo-Hygrometer", "device" : 187, "modelnumber" : 5, "channel" : 1, "battery" : "OK", "temperature_F" : 77.200, "humidity" : 67, "mic" : "CRC"}\n'


def processF016TH(json_data, ReadingCountArray):
    if (config.SWDEBUG):
        sys.stdout.write('Processing F016TH data' + '\n')
        sys.stdout.write(json.dumps(json_data))
        print(ReadingCountArray)

    var = json_data

    lastIndoorReading = nowStr()

    # check for reading count per device
    # indoor T/H sensors support channels 1-8
    # the sensor channel needs to be lowered by one
    chan_array_pos = var['channel'] - 1

    #if ((ReadingCountArray[var["channel"]] % config.IndoorRecordEveryXReadings) != 0):
    if (ReadingCountArray[chan_array_pos] % config.IndoorRecordEveryXReadings) != 0:
        if config.SWDEBUG:
            print("skipping write to database for channel=", var["channel"])
        # increment ReadingCountArray
        # ReadingCountArray[var["channel"]] = ReadingCountArray[var["channel"]] + 1
        ReadingCountArray[chan_array_pos] += 1
        return ""
    # increment ReadingCountArray
    # ReadingCountArray[var["channel"]] = ReadingCountArray[var["channel"]] + 1
    ReadingCountArray[chan_array_pos] += 1

    IndoorTemperature = fahrenheit_to_celsius(var["temperature_F"])
    #IndoorTemperature = var["temperature_F"]

    if (config.enable_InfluxDB == True):
        database = config.INFLUX_INDOOR_DATABASE
        temp_record = influxdb_client.json_format('temperature', var["time"], var["device"], IndoorTemperature)
        humidity_record = influxdb_client.json_format('humidity', var["time"], var["device"], var["humidity"])
        influxdb_client.insert_records(database, [temp_record, humidity_record])


    return
