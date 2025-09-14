from telegram import Update
from telegram.ext import ContextTypes


async def report_status(update: Update, context: ContextTypes.DEFAULT_TYPE, ssh_server=None):
    """
    Check server status via SSH connection.
    """
    if not ssh_server or not ssh_server.is_connected():
        await update.message.reply_text("❌ Server connection not available")
        return

    try:
        # Check system load
        load_output = ssh_server.exec_command("uptime")
        load_line = load_output.strip().split()[-3:]

        # Check disk usage
        disk_output = ssh_server.exec_command("df -h / | tail -1")
        disk_usage = disk_output.strip().split()

        # Check memory usage
        mem_output = ssh_server.exec_command("free -h | grep '^Mem:'")
        mem_info = mem_output.strip().split()

        status_message = "🟢 Server Status:\n\n"
        status_message += f"⏱️ Load Average: {', '.join(load_line)}\n"
        status_message += f"💾 Disk Usage: {disk_usage[4]} used ({disk_usage[3]} free)\n"
        status_message += f"🧠 Memory: {mem_info[2]}/{mem_info[1]} used\n"
        status_message += "\n✅ Server is operational"

        await update.message.reply_text(status_message)

    except Exception as e:
        await update.message.reply_text(f"❌ Error checking server status: {str(e)}")