# Shadowsocks-libev Installation Guide

## Quick Installation

### 1. Install shadowsocks-libev
```bash
sudo apt update
sudo apt install shadowsocks-libev
```

### 2. Change configuration file
```bash
sudo nano /etc/shadowsocks-libev/config.json
```

### 3. Basic configuration (replace with your values)
```json
{
    "server":"0.0.0.0",
    "server_port":8388,
    "password":"your_password_here",
    "timeout":300,
    "method":"aes-256-gcm",
    "fast_open":true
}
```

### 4. Restart or start the service
```bash
sudo systemctl restart shadowsocks-libev
sudo systemctl start shadowsocks-libev
```

### 5. Check status
```bash
sudo systemctl status shadowsocks-libev@config
```

### 6. (Optional) Open firewall port (if using UFW)
```bash
sudo ufw allow 8388
```

## Notes
- Replace `your_password_here` with a strong password
- Change `server_port` if port 8388 is already in use
- The bot will connect to this server via SSH for monitoring