import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/telegram_stats")

if not TOKEN:
    raise ValueError("Error: TELEGRAM_BOT_TOKEN is not set in .env file.")
if not MONGO_URI:
    raise ValueError("Error: MONGO_URI is not set in .env file.")
