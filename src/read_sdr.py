import json
import sys
import traceback
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
from queue import Queue, Empty

import config
import src.sensors.F016TH
import src.sensors.FT020T

ON_POSIX = 'posix' in sys.builtin_module_names


rtl_433_cmd = ['/usr/local/bin/rtl_433', '-q', '-F', 'json', '-R', '146', '-R', '147', '-R', '148', '-R', '150', '-R', '151']

def enqueue_output(src, out, queue):
    for line in iter(out.readline, b''):
        queue.put((src, line))
    out.close()


# main read 433HMz Sensor Loop
def read_sensors():
    print("Read Wireless Sensors")

    # either ignore output from STDERR or merge it with STDOUT due to subprocess bug
    pipe_opn = Popen(rtl_433_cmd, stdout=PIPE, stderr=STDOUT, bufsize=1, close_fds=ON_POSIX)
    queue_obj = Queue()
    daemon_thread = Thread(target=enqueue_output, args=('stdout', pipe_opn.stdout, queue_obj))
    daemon_thread.daemon = True  # thread dies with the program
    daemon_thread.start()
    print("starting 433MHz scanning")
    print("######")

    while True:
        try:
            src, line = queue_obj.get(timeout=1)
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

            if ('F016TH' in model_name):
                # F016TH data found (small indoor sensor)
                processF016TH(json_data, IndoorReadingCountArray)
            elif ('FT0300' in model_name):
                # FT020T data found (outdoor sensor with anemometer)
                processFT020T(json_data)
            else:
                print(sLine)

        sys.stdout.flush()
