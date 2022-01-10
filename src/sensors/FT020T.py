# FT020T Sensor
#
import config
from src.helpers import *
from src.mqtt import mqtt_publish_single

import json
import sys
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
import datetime
import traceback

# import gpiozero # process functions
# import MySQLdb as mdb
from src import influxdb_client

# Sample sLine:
# '{"time" : "2021-06-07 23:32:11", "model" : "SwitchDoc Labs FT020T AIO", "device" : 12, "id" : 0, "batterylow" : 0, "avewindspeed" : 0, "gustwindspeed" : 0, "winddirection" : 9, "cumulativerain" : 255, "temperature" : 1177, "humidity" : 66, "light" : 0, "uv" : 0, "mic" : "CRC"}\n'

def processFT020T(json_data, lastFT020TTimeStamp, ReadingCount):
    if (config.SWDEBUG):
        # sys.stdout.write("processing FT020T Data\n")
        sys.stdout.write(json.dumps(json_data))
        sys.stdout.write('ReadingCount=: ' + str(ReadingCount) + '\n')

    if (lastFT020TTimeStamp == json_data["time"]):
        # duplicate
        if (config.SWDEBUG):
            sys.stdout.write("duplicate found\n")

        return ""
    lastFT0202TTimeStamp = json_data["time"]

    # now check for adding record
    if ((ReadingCount % config.RecordEveryXReadings) != 0):
        # skip write to database
        if (config.SWDEBUG):
            sys.stdout.write("skipping write to database \n")

        return ""

    # outside temperature and Humidity
    # mainID = json_data["id"]  --TODO unused?
    # lastMainReading = nowStr()  --TODO unused?
    raw_temp = json_data["temperature"]
    ucHumi = json_data["humidity"]
    wTemp = (raw_temp - 400) / 10.0
    # deal with error condtions
    if (wTemp > 140.0):
        # error condition from sensor
        if (config.SWDEBUG):
            sys.stdout.write("error--->>> Temperature reading from FT020T\n")
            sys.stdout.write('This is the raw temperature: ' + str(wTemp) + '\n')
        # put in previous temperature
        wtemp = OutdoorTemperature
        # print("wTemp=%s %s", (str(wTemp),nowStr() ));
    if (ucHumi > 100.0):
        # bad humidity: put in previous humidity if exists
        if (config.SWDEBUG):
            sys.stdout.write("error--->>> Humidity reading from FT020T\n")
            sys.stdout.write('This is the raw humidity: ' + str(ucHumi) + '\n')

        if 'OutdoorHumidity' in vars():
            ucHumi = OutdoorHumidity
        else:
            ucHumi = 0

    # convert temperature reading to Celsius but why?
    OutdoorTemperature = fahrenheit_to_celsius(wTemp)


    WindSpeed = round(json_data["avewindspeed"] / 10.0, 1)
    WindGust = round(json_data["gustwindspeed"] / 10.0, 1)
    WindDirection = json_data["winddirection"]

    TotalRain = round(json_data["cumulativerain"] / 10.0, 1)
    Rain60Minutes = 0.0

    wLight = json_data["light"]
    if (wLight >= 0x1fffa):
        wLight = wLight | 0x7fff0000

    wUVI = json_data["uv"]
    if (wUVI >= 0xfa):
        wUVI = wUVI | 0x7f00

    SunlightVisible = wLight
    SunlightUVIndex = round(wUVI / 10.0, 1)

    if (json_data['batterylow'] == 0):
        BatteryOK = "OK"
    else:
        BatteryOK = "LOW"

    if config.enable_InfluxDB == True:
        print("writing to influxdb")
        INFLUX_INDOOR_DATABASE = 'indoor_db'
        INFLUX_OUTDOOR_DATABASE = 'outdoor_db'
        record = influxdb_client.json_format('WindSpeed', lastFT0202TTimeStamp, json_data['device'], WindSpeed)
        influxdb_client.insert_records(config.INFLUX_OUTDOOR_DATABASE, [record])


    return lastFT0202TTimeStamp
