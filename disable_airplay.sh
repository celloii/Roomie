#!/bin/bash
# Helper script to check AirPlay Receiver status and provide instructions

echo "🔍 Checking AirPlay Receiver status..."
echo ""

# Check if port 5000 is in use by AirPlay
if lsof -i:5000 2>/dev/null | grep -q "ControlCe"; then
    echo "⚠️  AirPlay Receiver is currently ENABLED and using port 5000"
    echo ""
    echo "📋 To disable AirPlay Receiver:"
    echo "   1. Open System Settings (click Apple menu → System Settings)"
    echo "   2. Click 'General' in the sidebar"
    echo "   3. Click 'AirDrop & Handoff'"
    echo "   4. Toggle OFF 'AirPlay Receiver'"
    echo ""
    echo "After disabling, run this script again to verify."
else
    echo "✅ AirPlay Receiver appears to be DISABLED"
    echo "✅ Port 5000 should be available for your server"
fi

echo ""
echo "Checking if port 5000 is available..."
if lsof -i:5000 2>/dev/null | grep -q "Python"; then
    echo "✅ Your Python server is running on port 5000"
elif ! lsof -i:5000 2>/dev/null | grep -q "ControlCe"; then
    echo "✅ Port 5000 is free and ready to use"
else
    echo "⚠️  Port 5000 is still in use"
fi

