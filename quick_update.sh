#!/bin/bash
# Quick update script - updates backend and reloads Cinnamon

echo "🚀 Quick Update - Legion Power"
echo "================================"
echo ""

# Update backend
echo "📦 Updating backend..."
sudo cp backend/ddc_monitor.py /usr/local/lib/legion-power/
sudo chmod +x /usr/local/lib/legion-power/ddc_monitor.py

echo "🔄 Restarting service..."
sudo systemctl restart legion-power.service

echo ""
echo "✅ Backend updated!"
echo ""
echo "Now refresh Cinnamon:"
echo "  Alt+F2, type 'r', Enter"
echo ""
