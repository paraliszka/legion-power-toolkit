#!/bin/bash
# Update Legion Power Backend
# Run this script to update the installed backend with new changes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_DIR/backend"
INSTALL_DIR="/usr/local/lib/legion-power"

echo "🔄 Legion Power Backend Update"
echo "================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root or with sudo"
    echo "   Usage: sudo $0"
    exit 1
fi

# Check if backend is installed
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ Backend not installed at $INSTALL_DIR"
    echo "   Run the installer first: ./install.sh"
    exit 1
fi

echo "📦 Copying updated backend files..."
echo ""

# Copy all backend Python files
for file in "$BACKEND_DIR"/*.py; do
    filename=$(basename "$file")
    if [ "$filename" != "__init__.py" ] && [ "$filename" != "test_backend.py" ]; then
        echo "   Copying: $filename"
        cp "$file" "$INSTALL_DIR/"
        chmod +x "$INSTALL_DIR/$filename"
    fi
done

echo ""
echo "✅ Backend files updated successfully!"
echo ""
echo "🔄 Restarting legion-power.service..."
systemctl restart legion-power.service

echo ""
echo "✅ Service restarted!"
echo ""
echo "📊 Service status:"
systemctl status legion-power.service --no-pager -l | head -15
echo ""
echo "🎉 Update complete!"
echo ""
echo "Test the new DDC monitor features:"
echo "  1. Open the applet menu"
echo "  2. Look for 'External Monitors' section"
echo "  3. Adjust brightness sliders for your monitors"
echo ""
