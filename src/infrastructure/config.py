import json
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
# Use pathlib to construct path relative to project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

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

# Admin Configuration
ALLOW_PASSWORD = os.getenv('ALLOW_PASSWORD')
if not ALLOW_PASSWORD:
    raise ValueError("ALLOW_PASSWORD environment variable is required")

# Access Control
# Load allowed users from JSON file
users_json_path = project_root / 'users.json'

def load_allowed_users(json_path: Path) -> List[int]:
    """Load allowed user IDs from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract user IDs from the allowed_users list
        allowed_users = data.get('allowed_users', [])
        user_ids = []

        for user in allowed_users:
            if isinstance(user, dict) and 'id' in user:
                user_id = user['id']
                if isinstance(user_id, int):
                    user_ids.append(user_id)
            elif isinstance(user, int):
                # Support legacy format with just IDs
                user_ids.append(user)

        return user_ids

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load users.json: {e}. Using empty list.")
        return []
    except Exception as e:
        print(f"Error loading users.json: {e}. Using empty list.")
        return []


# Global variable to hold current allowed users
ALLOWED_USERS = []

def reload_allowed_users():
    """Reload allowed users from JSON file and update the global ALLOWED_USERS list."""
    global ALLOWED_USERS
    new_users = load_allowed_users(users_json_path)
    ALLOWED_USERS.clear()
    ALLOWED_USERS.extend(new_users)
    return ALLOWED_USERS

# Initial load
reload_allowed_users()
