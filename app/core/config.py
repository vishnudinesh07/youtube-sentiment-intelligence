import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
APP_NAME = "YouTube Sentiment Intelligence"
APP_VERSION = "1.0.0"