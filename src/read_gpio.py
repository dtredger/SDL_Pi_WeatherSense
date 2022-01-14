import json
import sys
import traceback
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
from queue import Queue, Empty

import config

            from gpiozero import CPUTemperature


ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(queue):
    cpu = CPUTemperature()
    temp = (cpu.temperature)
    queue.put(temp)



# main read 433HMz Sensor Loop
def read_gpio():
    print("Read Wireless Sensors")

    # either ignore output from STDERR or merge it with STDOUT due to subprocess bug
    queue_obj = Queue()
    daemon_thread = Thread(target=enqueue_output, args=(queue_obj))
    daemon_thread.daemon = True  # thread dies with the program
    daemon_thread.start()
    print("starting read_gpio()")
    print(f"reading timeout is #{SCAN_TIMEOUT} seconds")
    print("######")


    while True:
        try:
            src, line = queue_obj.get(timeout=SCAN_TIMEOUT)
        except Empty:
            if config.SWDEBUG:
                print("queue empty")
        else:  # got line
            print(src)
            print(line)
