import os
import logging
import signal
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from handlers import get_id, report_status
from services.ssh_server import SSHServer

# Load environment variables
load_dotenv('.env')

# Configuration with defaults
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_USERNAME = os.getenv('SERVER_USERNAME', 'root')
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO)
)

# Validate required environment variables
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Global SSH server instance for cleanup
ssh_server_instance = None

def cleanup(signum=None, frame=None):
    """Cleanup function to close SSH connection on exit."""
    global ssh_server_instance
    if ssh_server_instance and ssh_server_instance.is_connected():
        logging.info("Closing SSH connection...")
        ssh_server_instance.close()
    if signum:
        sys.exit(0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Welcome to the VPN Server Bot! Use /help to see available commands.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
        Available commands:
        /start - Welcome message
        /help - Show this help
        /status - Check server status
    """
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def main():
    """Start the bot."""
    global ssh_server_instance

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Initialize SSH server connection
    ssh_server_instance = SSHServer(SERVER_IP, SERVER_USERNAME, SERVER_PASSWORD)

    # Connect to SSH server
    try:
        ssh_server_instance.connect()
        logging.info("Successfully connected to SSH server")
    except ValueError as e:
        logging.error(f"Failed to connect to SSH server: {e}")
        # Continue without SSH functionality for now

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", lambda update, context: report_status(update, context, ssh_server_instance)))



    application.add_handler(CommandHandler("id", get_id))
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    try:
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
    finally:
        # Ensure cleanup happens even if bot crashes
        cleanup()

if __name__ == '__main__':
    main()