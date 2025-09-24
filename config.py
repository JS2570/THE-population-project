import json, os
from datetime import datetime


SETTINGS_FILE = "settings.json"
LOG_FILE = "log.txt"

LOG_BUFFER = []


def get_datetimestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_timestamp():
    return datetime.now().strftime("%H:%M:%S")


def write_log(level, message):
    line = f"[{get_timestamp()}] {level}: {message}"
    print(line)
    LOG_BUFFER.append(line)


def log(message):  write_log("LOG", message)
def error(message): write_log("ERROR", message)


# initiate settings as global variable
with open(SETTINGS_FILE, "r") as f:
    SETTINGS = json.load(f)


# find next avaible output data folder
i = 1
while True:
    candidate = os.path.join(SETTINGS["output_folder"], f"data{i}")
    if os.path.isdir(candidate):
        i += 1
    else:
        os.makedirs(candidate, exist_ok=True)
        OUTPUT_PATH =  candidate
        break


log("successfully loaded settings file")
log("successfully created directory")