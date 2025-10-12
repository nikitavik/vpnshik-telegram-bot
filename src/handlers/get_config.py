import re
from telegram import Update
from telegram.ext import ContextTypes

from services.qr_generation import get_qr
from .restricted_handler import restricted


def escape_markdown_v2(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2 format."""
    # Characters that need escaping in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


@restricted
async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE, ssh_server=None):
    """
    Get Shadowsocks VPN configuration as QR code for Potatso app.
    """
    if not ssh_server or not ssh_server.is_connected():
        await update.message.reply_text("❌ Server connection not available")
        return

    try:
        # Read shadowsocks config from server
        config_json = ssh_server.exec_command("cat /etc/shadowsocks-libev/config.json")

        # Generate QR code using the service
        qr_buffer, ss_uri = get_qr(config_json, ssh_server.ip)

        # Send QR code as photo
        await update.message.reply_photo(
            photo=qr_buffer,
            caption="📱 Scan this QR code in Potatso app to import Shadowsocks VPN config"
        )

        # Send URI with spoiler formatting
        escaped_uri = escape_markdown_v2(ss_uri)
        await update.message.reply_text(
            f"URI: ||{escaped_uri}||",
            parse_mode='MarkdownV2'
        )

    except ValueError as e:
        await update.message.reply_text(f"❌ Configuration error: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating config QR code: {str(e)}")