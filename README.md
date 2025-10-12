# VPN Server Management Telegram Bot

A Telegram bot for monitoring and managing VPN servers via SSH connection.

## Features

- 🟢 **Server Status Monitoring**: Check system load, disk usage, and memory usage
- 🔧 **SSH-based Server Management**: Connect to your server securely
- 📊 **Real-time System Information**: Get live server statistics
- 🤖 **Telegram Integration**: Easy-to-use bot interface

## Setup

### Prerequisites

1. Create a new bot and get your token from [@BotFather](https://t.me/botfather) on Telegram
2. Have SSH access to your VPN server

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd vpnshik
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   SERVER_IP=your_server_ip
   SERVER_USERNAME=your_ssh_username
   SERVER_PASSWORD=your_ssh_password
   LOG_LEVEL=INFO
   ALLOWED_USERS=123456789,987654321

## Configuration

### Environment Variables

- `TELEGRAM_BOT_TOKEN` (required): Your Telegram bot token from BotFather
- `SERVER_IP` (required): IP address of your VPN server
- `SERVER_USERNAME` (optional): SSH username (defaults to 'root')
- `SERVER_PASSWORD` (required): SSH password for authentication
- `LOG_LEVEL` (optional): Logging level (defaults to 'INFO')
- `ALLOWED_USERS` (optional): Comma-separated list of allowed Telegram user IDs (leave empty for no restrictions)

## Running the Bot

### Development (Polling Mode)
For local development and testing, run the bot in polling mode:

```bash
python src/bot.py
```

The bot will continuously poll Telegram's servers for new messages.

```bash
python src/bot.py
```

### Docker Deployment (Recommended for Production)

For production deployment, use Docker for easy scaling and management:

#### Quick Start with Docker Compose

1. **Create environment file**:
   ```bash
   cp .env.example .env  # Copy example file
   nano .env             # Edit with your values
   ```

3. **Deploy with Docker Compose**:
   ```bash
   # Build and start the container
   docker-compose up -d

   # View logs
   docker-compose logs -f vpn-bot

   # Stop the bot
   docker-compose down
   ```

#### Manual Docker Commands

```bash
# Build the image
docker build -t vpn-bot .

# Run the container
docker run -d --name vpn-bot \
  --restart unless-stopped \
  -v $(pwd)/users.json:/app/users.json \
  --env-file .env \
  vpn-bot

# View logs
docker logs -f vpn-bot

# Stop and remove
docker stop vpn-bot && docker rm vpn-bot
```

#### Docker Volume Mappings

- `users.json`: Stores allowed users (read-write)
- `.env`: Environment variables (passed via `--env-file`)

## Available Commands

- `/start` - Welcome message and bot introduction
- `/help` - Show available commands
- `/status` - Check server status (load, disk, memory)

## Architecture

```
src/
├── bot.py              # Main Telegram bot application
└── services/
    ├── ssh_server.py  # SSH connection management
    └── status_report.py # Server status checking
```

## Security Notes

- Store your `.env` file securely and never commit it to version control
- Use strong SSH passwords or key-based authentication
- Consider using SSH keys instead of passwords for production use
- The bot connects to your server on startup and maintains the connection

## Troubleshooting

- **Connection Issues**: Check your SSH credentials and server IP
- **Permission Denied**: Ensure your SSH user has necessary permissions
- **Bot Not Responding**: Verify your Telegram bot token is correct

## Development

The bot uses:
- `python-telegram-bot` for Telegram API integration
- `paramiko` for SSH connections
- `python-dotenv` for environment variable management

## Future Enhancements

- Add VPN-specific monitoring (OpenVPN, WireGuard status)
- Implement user management commands
- Add server restart/shutdown capabilities
- Include network traffic monitoring
- Add alert system for server issues
