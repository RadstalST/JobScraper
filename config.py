from dotenv import load_dotenv
import os
import json
load_dotenv()

class Config:
    APP_NAME = os.environ.get("APP_NAME","My App")
    JOBS = json.load(open("jobs.json"))
    CHROME_PROFILE_PATH = os.environ.get("CHROME_PROFILE_PATH", "~/Library/Application Support/Google/Chrome/Default")
    IMPLICIT_WAIT=os.environ.get("IMPLICIT_WAIT", 1.0)
    SLEEP_TIME=os.environ.get("SLEEP_TIME", 3.0)
    APPLY = os.environ.get("APPLY", True)
    LIMIT = os.environ.get("LIMIT", 20)
    STORAGE = os.environ.get("STORAGE", "./out/ouput.json")

    # CHROME_PROFILE = os.environ.get("CHROME_PROFILE", "Default")