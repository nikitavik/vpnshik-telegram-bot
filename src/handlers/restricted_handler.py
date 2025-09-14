import logging
from infrastructure.config import ALLOWED_USERS


def restricted(func):
    async def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            logging.warning(f"Unauthorized access attempt by user {user_id}")
            if update.message:
                await update.message.reply_text("⛔ У вас нет доступа к этому боту")
            elif update.callback_query:
                await update.callback_query.answer("⛔ У вас нет доступа к этому боту")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
