#!/bin/bash

# Legion Power Manager Applet Installation Script
# This script installs the Legion Power applet to Cinnamon

set -e

APPLET_UUID="legion-power@moodliszka"
APPLET_DIR="$(cd "$(dirname "$0")" && pwd)"
USER_APPLETS_DIR="$HOME/.local/share/cinnamon/applets"
SYSTEM_APPLETS_DIR="/usr/share/cinnamon/applets"

echo "========================================="
echo "Legion Power Manager Applet Installer"
echo "========================================="
echo ""

# Check if running in Cinnamon
if [ -z "$DESKTOP_SESSION" ] || ! echo "$DESKTOP_SESSION" | grep -qi "cinnamon"; then
    echo "Warning: This doesn't appear to be a Cinnamon desktop environment."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installation options:"
echo "  1. User installation (recommended) - ~/.local/share/cinnamon/applets/"
echo "  2. System installation (requires sudo) - /usr/share/cinnamon/applets/"
echo ""
read -p "Choose installation type (1 or 2): " INSTALL_TYPE

if [ "$INSTALL_TYPE" = "1" ]; then
    # User installation
    INSTALL_DIR="$USER_APPLETS_DIR"
    NEEDS_SUDO=false
    echo ""
    echo "Installing to: $INSTALL_DIR"
elif [ "$INSTALL_TYPE" = "2" ]; then
    # System installation
    INSTALL_DIR="$SYSTEM_APPLETS_DIR"
    NEEDS_SUDO=true
    echo ""
    echo "Installing to: $INSTALL_DIR (requires sudo)"
else
    echo "Invalid option. Exiting."
    exit 1
fi

# Create installation directory if it doesn't exist
if [ "$NEEDS_SUDO" = true ]; then
    sudo mkdir -p "$INSTALL_DIR"
else
    mkdir -p "$INSTALL_DIR"
fi

# Remove old installation if it exists
if [ -d "$INSTALL_DIR/$APPLET_UUID" ]; then
    echo ""
    echo "Found existing installation at $INSTALL_DIR/$APPLET_UUID"
    read -p "Remove and replace? (Y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        if [ "$NEEDS_SUDO" = true ]; then
            sudo rm -rf "$INSTALL_DIR/$APPLET_UUID"
        else
            rm -rf "$INSTALL_DIR/$APPLET_UUID"
        fi
        echo "Removed old installation."
    else
        echo "Installation cancelled."
        exit 0
    fi
fi

# Copy applet files
echo ""
echo "Copying applet files..."
if [ "$NEEDS_SUDO" = true ]; then
    sudo cp -r "$APPLET_DIR/files/$APPLET_UUID" "$INSTALL_DIR/"
else
    cp -r "$APPLET_DIR/files/$APPLET_UUID" "$INSTALL_DIR/"
fi

# Set correct permissions
if [ "$NEEDS_SUDO" = true ]; then
    sudo chmod -R 755 "$INSTALL_DIR/$APPLET_UUID"
    sudo chown -R root:root "$INSTALL_DIR/$APPLET_UUID"
else
    chmod -R 755 "$INSTALL_DIR/$APPLET_UUID"
fi

echo "Applet files copied successfully!"

# Check if Legion D-Bus service is running
echo ""
echo "Checking Legion D-Bus service..."
if systemctl is-active --quiet legion-power.service; then
    echo "✓ Legion Power D-Bus service is running"
else
    echo "✗ Legion Power D-Bus service is NOT running"
    echo ""
    echo "Legion-specific features (Conservation Mode, Rapid Charge, Fan Control) require"
    echo "the Legion Power D-Bus service to be installed and running."
    echo ""
    echo "To install the service:"
    echo "  cd $HOME/Desktop/repos/linux/power/backend"
    echo "  sudo python3 install_service.py"
    echo "  sudo systemctl enable legion-power.service"
    echo "  sudo systemctl start legion-power.service"
fi

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Restart Cinnamon (Alt+F2, type 'r', press Enter)"
echo "     OR log out and log back in"
echo ""
echo "  2. Remove the old power applet (if present):"
echo "     - Right-click on the system power applet"
echo "     - Select 'Remove from panel'"
echo ""
echo "  3. Add the Legion Power applet:"
echo "     - Right-click on your panel"
echo "     - Select 'Applets'"
echo "     - Search for 'Legion Power Manager'"
echo "     - Click the '+' button to add it"
echo ""
echo "  4. Configure the applet:"
echo "     - Right-click on the Legion Power applet"
echo "     - Select 'Configure...'"
echo ""
echo "Enjoy your Legion Power Manager!"
echo ""
