import json
import base64
import qrcode
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes

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
        config = json.loads(config_json)
        print(config)

        # Extract required fields
        server = config.get('server', ssh_server.ip)
        server_port = config.get('server_port', 8388)
        password = config.get('password', '')
        method = config.get('method', 'aes-256-gcm')

        if not password:
            await update.message.reply_text("❌ Password not found in server config")
            return

        # Create shadowsocks URI format: ss://method:password@server:port
        # Base64 encode the method:password part
        user_info = f"{method}:{password}"
        user_info_b64 = base64.urlsafe_b64encode(user_info.encode()).decode().rstrip('=')

        ss_uri = f"ss://{user_info_b64}@{server}:{server_port}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(ss_uri)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Send QR code as photo
        await update.message.reply_photo(
            photo=buffer,
            caption="📱 Scan this QR code in Potatso app to import Shadowsocks VPN config"
        )

    except json.JSONDecodeError:
        await update.message.reply_text("❌ Failed to parse server config JSON")
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating config QR code: {str(e)}")