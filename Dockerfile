FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional packages that might not be in requirements.txt
RUN pip install --no-cache-dir \
    pyrogram \
    tgcrypto \
    pytgcalls \
    yt-dlp \
    python-dotenv \
    aiohttp \
    aiofiles \
    pillow \
    requests \
    psutil

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p sessions downloads logs data

# Set permissions
RUN chmod +x main.py

# Expose port (optional, if needed for web interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Run the bot
CMD ["python3", "main.py"]
