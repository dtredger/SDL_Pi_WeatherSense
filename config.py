# configuration file - contains customization for WeatherSense

import os
import logging

LOG_NAME = "/home/pi/debugger.log"
# TODO(fix relative naming)
if LOG_NAME:
    filename_base = config.LOG_NAME
else:
    filename_base = os.getcwd() + "/debugger.log"

logging.basicConfig(filename=filename_base,
                    level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

LOGGER = logging.getLogger(__name__)


SWDEBUG = True
ENABLE_INFLUXDB = True


# INFLUX_INDOOR_DATABASE = 'indoor_db'
# INFLUX_OUTDOOR_DATABASE = 'outdoor_db'

INFLUX_DATABASE = 'montrose_data'
LOG_ABSOLUTE_HUMIDITY = True
