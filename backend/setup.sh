#!/bin/bash

# Quick Setup Script for Live Interview Copilot Backend
# This script sets up the Python environment and installs dependencies

set -e

echo "🚀 Setting up Live Interview Copilot Backend..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env and add your API keys:"
echo "   - DEEPGRAM_API_KEY=your_key_here"
echo "   - GROQ_API_KEY=your_key_here"
echo ""
echo "3. Start the server:"
echo "   python main.py"
echo ""
