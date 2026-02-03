#!/bin/bash

echo "🚀 Infoins V4 Chatbot - Quick Start Script"
echo "=========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "✅ .env file created!"
    echo "📌 Please edit the .env file and add your GEMINI_API_KEY"
    echo "   You can get your API key from: https://aistudio.google.com/"
    echo ""
    echo "After adding your API key, run this script again."
    exit 1
fi

# Check if API key is set
source .env
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_api_key_here" ]; then
    echo "⚠️  GEMINI_API_KEY not configured!"
    echo "📌 Please edit the .env file and add your actual API key"
    echo "   You can get your API key from: https://aistudio.google.com/"
    exit 1
fi

echo "✅ API key found!"
echo ""

# Check if Python packages are installed
echo "📦 Checking Python packages..."
pip install -r requirements.txt --quiet

echo "✅ Packages installed!"
echo ""

# Get local IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo "🌐 Starting server..."
echo ""
echo "📱 Access URLs:"
echo "   Local:   http://localhost:5000"
echo "   Network: http://$IP_ADDRESS:5000"
echo ""
echo "💡 Tip: Use the Network URL to access from your phone!"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Run the server
python chatbot_server.py
