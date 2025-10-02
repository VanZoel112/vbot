#!/bin/bash
# VZ ASSISTANT v0.0.0.69
# Quick Start Script
#
# 2025© Vzoel Fox's Lutpan
# Founder & DEVELOPER : @VZLfxs

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              VZ ASSISTANT v0.0.0.69                      ║"
echo "║              2025© Vzoel Fox's Lutpan                    ║"
echo "║              Founder & DEVELOPER : @VZLfxs               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.9+ first"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "🐍 Python version: $PYTHON_VERSION"

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your SESSION_STRING"
    echo ""
    echo "Run: python3 stringgenerator.py to generate a session string"
    exit 0
fi

# Run the bot
echo ""
echo "🚀 Starting VZ ASSISTANT..."
echo ""
python3 main.py
