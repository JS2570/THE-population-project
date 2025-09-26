from datetime import datetime
import json5, os
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

SETTINGS_FILE = "settings.json5"

DOWNLOAD_FOLDER = "data/raw"
OUTPUT_FOLDER = "data/processed"


# timestamp functions
def get_datetimestamp(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def get_timestamp(): return datetime.now().strftime("%H:%M:%S")


# initiate settings as global variable
with open(SETTINGS_FILE, "r") as f:
    SETTINGS = json5.load(f)


# find next avaible output data folder
i = 1
while True:
    candidate = os.path.join(OUTPUT_FOLDER, f"data{i}")
    if os.path.isdir(candidate):
        i += 1
    else:
        os.makedirs(candidate, exist_ok=True)
        OUT_PATH =  candidate
        break