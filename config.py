import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


DB_PATH = "database/tasks.db"

DAILY_REPORT_TIME = "22:00"
WEEKLY_REPORT_DAY = "FRIDAY"
WEEKLY_REPORT_TIME = "22:00"


