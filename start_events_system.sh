#!/bin/bash

# Startup script for the Events System
# This script starts both the Dedalus FastAPI server and the main Flask server

echo "🚀 Starting Events System..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Creating template..."
    echo "# Events System Configuration" > .env
    echo "DEDALUS_BASE_URL=http://localhost:8000" >> .env
    echo "ANTHROPIC_API_KEY=your_claude_api_key_here" >> .env
    echo "CLAUDE_MODEL=claude-3-5-sonnet-20241022" >> .env
    echo ""
    echo "📝 Please edit .env file with your API keys before running."
    echo ""
fi

# Start Dedalus Events API (FastAPI) in background
echo "📡 Starting Dedalus Events API (port 8000)..."
python dedalus_events.py &
DEDALUS_PID=$!

# Wait a moment for Dedalus to start
sleep 2

# Start Flask server (main app)
echo "🌐 Starting Flask Server (port 5000)..."
echo "📱 Events page will be available at: http://localhost:5000/events"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

python server.py

# Cleanup: kill Dedalus when Flask server stops
kill $DEDALUS_PID 2>/dev/null


