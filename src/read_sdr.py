import json
import sys
import traceback
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
from queue import Queue, Empty

import config
from src.sensors.F016TH import process_F016TH
from src.sensors.FT020T import process_FT020T

ON_POSIX = 'posix' in sys.builtin_module_names
SCAN_TIMEOUT = 5


# protocol [146] "SwitchDoc Labs Weather FT020T Sensors"
# protocol [147] "SwitchDoc Labs F016TH Temperature Humidity Sensor"
# protocol [148] "SwitchDoc Labs SolarMAX"
# protocol [150] "SwitchDoc Labs WeatherSenseAQI"
# protocol [151] "SwitchDoc Labs WeatherSenseTB"
rtl_433_cmd = ['/usr/local/bin/rtl_433', '-q', '-F', 'json', '-R', '146', '-R', '147', '-R', '148', '-R', '150', '-R', '151']

def enqueue_output(src, out, queue):
    for line in iter(out.readline, b''):
        queue.put((src, line))
    out.close()

def try_read_sdr():
    try:
        read_sdr()
    except Exception as ex:
        config.LOGGER.error(ex)



# main read 433HMz Sensor Loop
def read_sdr():
    print("Read Wireless Sensors")

    # either ignore output from STDERR or merge it with STDOUT due to subprocess bug
    pipe_opn = Popen(rtl_433_cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, close_fds=ON_POSIX)
    queue_obj = Queue()
    daemon_thread = Thread(target=enqueue_output, args=('stdout', pipe_opn.stdout, queue_obj))
    daemon_thread.daemon = True  # thread dies with the program
    daemon_thread.start()
    print("starting 433MHz scanning")
    print(f"reading timeout is #{SCAN_TIMEOUT} seconds")
    print("######")

    last_F016TH = ''
    last_FT020T = ''

    while True:
        try:
            src, line = queue_obj.get(timeout=SCAN_TIMEOUT)
        except Empty:
            if config.SWDEBUG:
                print("queue empty")
        else:  # got line
            sLine = line.decode()

            try:
                json_data = json.loads(sLine)
                model_name = json_data["model"]
            except Exception as e:
                model_name = '<not found>'

            # F016TH data found (small indoor sensor)
            if ('F016TH' in model_name):
                if json_data["time"] == last_F016TH:
                    if config.SWDEBUG:
                        print("duplicate F016TH reading")
                elif process_F016TH(json_data):
                    last_F016TH = json_data["time"]

            # FT020T data found (outdoor sensor with anemometer)
            elif ('FT020T' in model_name):
                if json_data["time"] == last_FT020T:
                    if config.SWDEBUG:
                        print("duplicate FT020T reading")
                elif process_FT020T(json_data):
                    last_FT020T = json_data["time"]

            else:
                print(sLine)

        sys.stdout.flush()
