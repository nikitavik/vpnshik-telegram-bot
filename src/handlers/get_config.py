from telegram import Update
from telegram.ext import ContextTypes

from services.qr_generation import get_qr
from .restricted_handler import restricted


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
        config_json = ssh_server.exec_command("cat /etc/shadowsocks/shadowsocks.json")

        # Generate QR code using the service
        qr_buffer, ss_uri = get_qr(config_json, ssh_server.ip)

        # Send QR code as photo
        await update.message.reply_photo(
            photo=qr_buffer,
            caption="📱 Scan this QR code in Potatso app to import Shadowsocks VPN config"
        )
        await update.message.reply_text(f"📱 Shadowsocks URI: ||{ss_uri}||")

    except ValueError as e:
        await update.message.reply_text(f"❌ Configuration error: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating config QR code: {str(e)}")