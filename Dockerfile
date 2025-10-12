FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for SSH and image processing
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create SSH directory and set permissions
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Create directory for users.json if it doesn't exist
RUN mkdir -p /app/data

# Set the default command
CMD ["python", "src/bot.py"]
