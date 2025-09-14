from telegram import Update
from telegram.ext import ContextTypes

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE, ssh_server=None):
    user = update.effective_user
    return await update.message.reply_text(f"Ваш user_id: {user.id}")