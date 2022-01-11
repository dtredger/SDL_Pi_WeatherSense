#
# wireless sensor routines


import config

import json
import random

import sys
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
import datetime
# import MySQLdb as mdb
import traceback
# import state
import gpiozero

# from paho.mqtt import publish


try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------

# cmd = [ '/usr/local/bin/rtl_433', '-q', '-F', 'json', '-R', '147']
cmd = ['/usr/local/bin/rtl_433', '-q', '-F', 'json', '-R', '146', '-R', '147', '-R', '148', '-R', '150', '-R', '151']


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------
#   A few helper functions...

def nowStr():
    return (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


# stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)


#   We're using a queue to capture output as it occurs


def enqueue_output(src, out, queue):
    for line in iter(out.readline, b''):
        queue.put((src, line))
    out.close()


def randomadd(value, spread):
    return round(value + random.uniform(-spread, spread), 2)




def processFT020T(sLine, lastFT020TTimeStamp, ReadingCount):
    var = json.loads(sLine)

    if (lastFT020TTimeStamp == var["time"]):
        # duplicate
        if (config.SWDEBUG):
            sys.stdout.write("duplicate found\n")

        return ""
    lastFT0202TTimeStamp = var["time"]

    # now check for adding record

    if ((ReadingCount % config.RecordEveryXReadings) != 0):
        # skip write to database
        if (config.SWDEBUG):
            sys.stdout.write("skipping write to database \n")

        return ""

    # outside temperature and Humidity
    mainID = var["id"]
    lastMainReading = nowStr()
    wTemp = var["temperature"]
    ucHumi = var["humidity"]
    wTemp = (wTemp - 400) / 10.0
    # deal with error condtions
    if (wTemp > 140.0):
        # error condition from sensor
        wtemp = OutdoorTemperature
        # print("wTemp=%s %s", (str(wTemp),nowStr() ));
    if (ucHumi > 100.0):
        # bad humidity
        # put in previous humidity
        ucHumi = OutdoorHumidity

    # convert temperature reading to Celsius but why?
    # OutdoorTemperature = round(((wTemp - 32.0) / (9.0 / 5.0)), 2)
    OutdoorTemperature = round(wTemp, 2)
    OutdoorHumidity = ucHumi
    WindSpeed = round(var["avewindspeed"] / 10.0, 1)
    WindGust = round(var["gustwindspeed"] / 10.0, 1)
    WindDirection = var["winddirection"]
    TotalRain = round(var["cumulativerain"] / 10.0, 1)
    Rain60Minutes = 0.0

    wLight = var["light"]
    if (wLight >= 0x1fffa):
        wLight = wLight | 0x7fff0000

    wUVI = var["uv"]
    if (wUVI >= 0xfa):
        wUVI = wUVI | 0x7f00

    SunlightVisible = wLight
    SunlightUVIndex = round(wUVI / 10.0, 1)

    if (var['batterylow'] == 0):
        BatteryOK = "OK"
    else:
        BatteryOK = "LOW"

    return lastFT0202TTimeStamp


# processes Inside Temperature and Humidity
def processF016TH(sLine, ReadingCountArray):
    var = json.loads(sLine)
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

    IndoorTemperature = round(((var["temperature_F"] - 32.0) / (9.0 / 5.0)), 2)
    #IndoorTemperature = var["temperature_F"]


# main read 433HMz Sensor Loop
def readSensors():
    print("Read Wireless Sensors")
    print("######")

    # either ignore output from STDERR or merge it with STDOUT due to subprocess bug
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, close_fds=ON_POSIX)
    qyuu = Queue()
    t = Thread(target=enqueue_output, args=('stdout', p.stdout, qyuu))
    t.daemon = True  # thread dies with the program
    t.start()

    pulse = 0
    print("starting 433MHz scanning")
    print("######")
    # last timestamp for FT020T to remove duplicates
    lastFT020TTimeStamp = ""
    FT020Count = 0
    IndoorReadingCountArray = [0, 0, 0, 0, 0, 0, 0, 0]

    while True:
        try:
            src, line = qyuu.get(timeout=1)
        except Empty:
            pulse += 1
        else:  # got line
            pulse -= 1
            sLine = line.decode()

            if "No supported devices found" in sLine:
                print("###### Error ######")
                print("No supported devices found.")
                print("is SDR Radio Dongle connected?")
                print("###### -_-; ######")

            try:
                json_data = json.loads(sLine)
                model_name = json_data["model"]
            except Exception as e:
                model_name = ''

            if ('F016TH' in model_name):
                # F007TH or F016TH data found (indoor data)
                processF016TH(json_data, IndoorReadingCountArray)
            if ('FT0300' in model_name):
                # FT0300 or FT020T data found (outdoor data)
                lastFT020TTimeStamp = processFT020T(json_data, lastFT020TTimeStamp, FT020Count)
                FT020Count = FT020Count + 1
            else:
                print("Unknow model_name found:", model_name)

        sys.stdout.flush()
