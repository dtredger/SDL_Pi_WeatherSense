# orphan sensor-reading methods


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
