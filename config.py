from dotenv import load_dotenv
import os
import json
load_dotenv()

class Config:
    APP_NAME = os.environ.get("APP_NAME","My App")
    JOBS = json.load(open("jobs.json"))
    CHROME_PROFILE_PATH = os.environ.get("CHROME_PROFILE_PATH", "~/Library/Application Support/Google/Chrome/Default")
    IMPLICIT_WAIT=2.0
    SLEEP_TIME=2.0
    QUICK_APPLY = os.environ.get("QUICK_APPLY", False)

    # CHROME_PROFILE = os.environ.get("CHROME_PROFILE", "Default")