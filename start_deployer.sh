#!/bin/bash
# VZ Deployer Bot Starter

echo "Starting VZ Deployer Bot..."

# Check if PM2 is available
if ! command -v pm2 &> /dev/null; then
    echo "⚠️  PM2 not found. Installing..."
    npm install -g pm2
fi

# Start with PM2
pm2 start deployer_bot.py \
    --name "vz_deployer_bot" \
    --interpreter python3 \
    --watch \
    --max-memory-restart 200M

pm2 save

echo "✅ Deployer bot started!"
echo "📊 Check status: pm2 status"
echo "📋 View logs: pm2 logs vz_deployer_bot"
