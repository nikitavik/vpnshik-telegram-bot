from telegram import Update
from telegram.ext import ContextTypes

from .restricted_handler import restricted


@restricted
async def report_status(update: Update, context: ContextTypes.DEFAULT_TYPE, ssh_server=None):
    """
    Check server status with essential VPN metrics.
    """
    if not ssh_server or not ssh_server.is_connected():
        await update.message.reply_text("❌ Server connection not available")
        return

    try:
        # Get daily bandwidth usage
        try:
            # Try to get default interface and check vnstat
            interface_cmd = ssh_server.exec_command("ip route | grep default | awk '{print $5}' | head -1")
            default_interface = interface_cmd.strip()

            if default_interface:
                bandwidth = ssh_server.exec_command(f"vnstat -i {default_interface} --oneline 2>/dev/null | cut -d';' -f4")
                daily_bandwidth = bandwidth.strip() if bandwidth.strip() else "vnstat not available"
            else:
                daily_bandwidth = "no default interface"
        except:
            daily_bandwidth = "vnstat not available"

        # Check systemd service status
        try:
            service_status = ssh_server.exec_command("systemctl is-active shadowsocks-libev").strip()
        except:
            service_status = "service not found"

        # Check configuration file presence
        try:
            config_check = ssh_server.exec_command("test -f /etc/shadowsocks-libev/config.json && echo 'present' || echo 'missing'")
            config_status = config_check.strip()
        except:
            config_status = "check failed"

        status_message = f"""🟢 Server Status:
📊 Daily bandwidth: {daily_bandwidth}
⚙️ Service status: {service_status}
📄 Config file: {config_status}
"""

        await update.message.reply_text(status_message)

    except Exception as e:
        await update.message.reply_text(f"❌ Error checking server status: {str(e)}")