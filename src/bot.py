import logging
import signal
import sys

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers import get_id, report_status, get_config
from services.ssh_server import SSHServer
from infrastructure.config import (
    BOT_TOKEN,
    LOG_LEVEL,
    SERVER_IP,
    SERVER_USERNAME,
    SERVER_PASSWORD,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
)

# Global SSH server instance for cleanup
ssh_server_instance = None

application = None  # Telegram application instance


def cleanup(signum=None, frame=None):
    """Cleanup function to close SSH connection on exit."""
    global ssh_server_instance, application
    if ssh_server_instance and ssh_server_instance.is_connected():
        logging.info("Closing SSH connection...")
        ssh_server_instance.close()
    if application:
        logging.info("Stopping application...")
        try:
            import asyncio
            # Try to get current event loop and stop the application
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(application.stop())
            except RuntimeError:
                # No running loop, try to stop synchronously
                try:
                    asyncio.run(application.stop())
                except Exception:
                    pass  # Ignore errors during shutdown
        except Exception:
            pass  # Ignore errors during shutdown
    if signum:
        sys.exit(0)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to the VPN Server Bot! Use /help to see available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
        Available commands:
        /start - Welcome message
        /help - Show this help
        /status - Check server status
        /config - Get VPN config as QR code
    """
    await update.message.reply_text(help_text)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def main():
    """Start the bot."""
    global ssh_server_instance, application

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
    application.add_handler(
        CommandHandler(
            "status",
            lambda update, context: report_status(update, context, ssh_server_instance),
        )
    )
    application.add_handler(
        CommandHandler(
            "config",
            lambda update, context: get_config(update, context, ssh_server_instance),
        )
    )

    application.add_handler(CommandHandler("id", get_id))
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    try:
        logging.info("Starting bot in polling mode")
        application.run_polling()

    except Exception as e:
        logging.error(f"Failed to start bot: {type(e).__name__}: {e}")
        if "TimedOut" in str(type(e)) or "ConnectTimeout" in str(e):
            logging.error("NETWORK TIMEOUT - check your internet connection")
        elif "Unauthorized" in str(e):
            logging.error("BOT TOKEN REJECTED - invalid or unauthorized")
        else:
            logging.error(f"Unexpected error: {e}")
        raise
    finally:
        # Ensure cleanup happens even if bot crashes
        cleanup()


if __name__ == "__main__":
    main()
