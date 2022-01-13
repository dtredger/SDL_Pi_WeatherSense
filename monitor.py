import time
import apscheduler.events
from apscheduler.schedulers.background import BackgroundScheduler

import config
from src.read_sdr import read_sensors

SOFTWAREVERSION = "V006"

print("WeatherSense Monitoring Software Version ", SOFTWAREVERSION)

# print out faults inside events
def ap_my_listener(event):
    if event.exception:
        print(event.exception)
        print(event.traceback)

scheduler = BackgroundScheduler()
# for debugging
scheduler.add_listener(ap_my_listener, apscheduler.events.EVENT_JOB_ERROR)
scheduler.add_job(read_sensors)  # run in background

# start scheduler
scheduler.start()
print("Scheduled Jobs")
scheduler.print_jobs()
