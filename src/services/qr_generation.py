import base64
import json
from io import BytesIO

import qrcode


def get_qr(config_json, ssh_server_ip):
    """
    Generate QR code for Shadowsocks VPN configuration.

    Args:
        config_json: JSON string containing Shadowsocks configuration
        ssh_server_ip: IP address of the server as fallback

    Returns:
        BytesIO buffer containing PNG QR code image
    """
    config = json.loads(config_json)

    server = config.get("server", ssh_server_ip)
    server_port = config.get("server_port", 8388)
    password = config.get("password", "")
    method = config.get("method", "aes-256-gcm")

    if not password:
        raise ValueError("Password not found in server config")

    # Create shadowsocks URI format: ss://method:password@server:port
    # Base64 encode the method:password part
    user_info = f"{method}:{password}"
    user_info_b64 = base64.urlsafe_b64encode(user_info.encode()).decode().rstrip("=")

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

    # Save to BytesIO buffer for Telegram
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer, ss_uri

if __name__ == "__main__":
    path = "./shadowsocks.json"
    try:
        with open(path, 'r') as f:
            config_json = f.read()
        qr_img, ss_uri = get_qr(config_json, "192.168.1.100")
        qr_img.save("shadowsocks_qr.png")
        print("QR code generated successfully and saved as shadowsocks_qr.png")
    except FileNotFoundError:
        print(f"Error: Configuration file '{path}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
