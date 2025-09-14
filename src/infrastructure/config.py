import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Server Configuration
SERVER_IP = os.getenv('SERVER_IP')
if not SERVER_IP:
    raise ValueError("SERVER_IP environment variable is required")

SERVER_USERNAME = os.getenv('SERVER_USERNAME', 'root')
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Access Control
# Comma-separated list of allowed user IDs (Telegram user IDs)
ALLOWED_USERS_STR = os.getenv('ALLOWED_USERS', '').strip()

def parse_allowed_users(user_str: str) -> List[int]:
    """Parse comma-separated string of user IDs into list of integers."""
    if not user_str:
        return []

    user_ids = []
    for uid in user_str.split(','):
        uid = uid.strip()
        if uid and uid.isdigit():
            try:
                user_ids.append(int(uid))
            except ValueError:
                continue  # Skip invalid IDs
    return user_ids

ALLOWED_USERS = parse_allowed_users(ALLOWED_USERS_STR)
