from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    APP_NAME = os.environ.get("APP_NAME","My App")