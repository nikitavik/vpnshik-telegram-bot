import json
import logging
from telegram import Update
from telegram.ext import ContextTypes

from infrastructure.config import ALLOW_PASSWORD, users_json_path, reload_allowed_users


def save_user_to_json(user_id: int, user_name: str = None) -> bool:
    """Add a user to the JSON file if not already present."""
    try:
        # Load existing data
        try:
            with open(users_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default structure if file doesn't exist or is invalid
            data = {"allowed_users": [], "version": "1.0"}

        allowed_users = data.get("allowed_users", [])

        # Check if user already exists
        for user in allowed_users:
            if isinstance(user, dict) and user.get("id") == user_id:
                return False  # User already exists

        # Add new user
        new_user = {
            "id": user_id,
            "name": user_name or f"User {user_id}",
            "role": "user",
        }
        allowed_users.append(new_user)

        # Save back to file
        data["allowed_users"] = allowed_users
        with open(users_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        logging.error(f"Error saving user to JSON: {e}")
        return False


async def allow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Allow a user to access the bot by adding them to the allowed users list.
    Usage: /allow <password>
    Only existing allowed users can use this command.
    """
    user = update.effective_user

    # Check if password was provided
    if not context.args or len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /allow <password>")
        return

    provided_password = context.args[0]

    # Validate password
    if provided_password != ALLOW_PASSWORD:
        logging.warning(f"Invalid allow password attempt by user {user.id}")
        await update.message.reply_text("❌ Invalid password")
        return

    # Add user to JSON
    user_name = user.first_name or user.username or f"User {user.id}"
    success = save_user_to_json(user.id, user_name)

    if success:
        logging.info(f"User {user.id} ({user_name}) added to allowed users")
        # Reload allowed users to make the new user immediately available
        reload_allowed_users()
        await update.message.reply_text(f"✅ Access granted! Welcome {user_name}!")
    else:
        await update.message.reply_text("❌ You are already in the allowed users list")
