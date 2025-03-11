import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'your_default_host'),
    'port': os.getenv('DB_PORT', 'your_default_port'),
    'database': os.getenv('DB_DATABASE', 'your_default_database'),
    'user': os.getenv('DB_USER', 'your_default_user'),
    'password': os.getenv('DB_PASSWORD', 'your_default_password')
}