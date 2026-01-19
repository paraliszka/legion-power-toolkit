#!/bin/bash
set -e

echo "🚀 Legion Power Manager Installer"
echo "=================================="

# 1. Pre-flight checks
check_system() {
    echo "🔍 Checking system..."
    # Check if Linux Mint (simplified)
    if [ ! -f /etc/linuxmint/info ]; then
        echo "⚠️  Warning: Not running on Linux Mint. Continuing anyway..."
    fi
}

# 2. Install dependencies
install_deps() {
    echo "📦 Installing dependencies..."
    sudo apt update
    sudo apt install -y \
        python3 python3-pip python3-gi python3-dbus \
        gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 \
        gir1.2-notify-0.7 libnotify-bin \
        tlp tlp-rdw powertop acpi-call-dkms \
        policykit-1
    
    echo "📦 Installing Python dependencies..."
    pip3 install --user --break-system-packages -r backend/requirements.txt || \
    pip3 install --user -r backend/requirements.txt
    
    # Load acpi_call
    echo "🔧 Loading acpi_call module..."
    sudo modprobe acpi_call || echo "⚠️  Failed to load acpi_call immediately, will load on reboot"
    echo "acpi_call" | sudo tee /etc/modules-load.d/acpi-call.conf > /dev/null
}

# 3. Test ACPI
test_acpi() {
    echo "🧪 Testing ACPI..."
    chmod +x scripts/test-acpi.sh
    ./scripts/test-acpi.sh || echo "⚠️  ACPI tests failed, but continuing installation..."
}

# 4. Backup original files
backup_system() {
    echo "💾 Backing up configuration..."
    mkdir -p configs/backup
    timestamp=$(date +%Y%m%d_%H%M%S)
    echo $timestamp > configs/backup/timestamp.txt
    
    # Backup original power applet (optional reference)
    if [ -d /usr/share/cinnamon/applets/power@cinnamon.org ]; then
        cp -r /usr/share/cinnamon/applets/power@cinnamon.org \
              configs/backup/ 2>/dev/null || true
    fi
    
    # Backup TLP config
    [ -f /etc/tlp.conf ] && \
        sudo cp /etc/tlp.conf configs/backup/tlp.conf.original
}

# 5. Install backend
install_backend() {
    echo "⚙️  Installing backend..."
    sudo mkdir -p /usr/local/lib/legion-power
    sudo cp -r backend/* /usr/local/lib/legion-power/
    
    # Install D-Bus service files
    sudo cp system/dbus/com.legion.Power.service \
            /usr/share/dbus-1/system-services/
    sudo cp system/dbus/com.legion.Power.conf \
            /etc/dbus-1/system.d/
            
    # Link main executable
    sudo ln -sf /usr/local/lib/legion-power/legion_power_service.py \
                /usr/local/bin/legion-power-service
    sudo chmod +x /usr/local/bin/legion-power-service
}

# 6. Install applet
install_applet() {
    echo "📱 Installing Cinnamon applet..."
    mkdir -p ~/.local/share/cinnamon/applets
    cp -r applet/legion-power@moodliszka \
          ~/.local/share/cinnamon/applets/
}

# 7. Install GUI
install_gui() {
    echo "🖥️  Installing GUI..."
    sudo cp gui/legion_power_gui.py /usr/local/bin/legion-power-gui
    sudo chmod +x /usr/local/bin/legion-power-gui
    
    # Copy widgets and assets to /usr/local/lib/legion-power/gui/
    sudo mkdir -p /usr/local/lib/legion-power/gui
    sudo cp -r gui/widgets /usr/local/lib/legion-power/gui/
    sudo cp -r gui/assets /usr/local/lib/legion-power/gui/
    sudo cp -r gui/ui /usr/local/lib/legion-power/gui/
    
    # Update the GUI script to look in the right place or just symlink
    # Simpler: Install desktop file pointing to local bin
    mkdir -p ~/.local/share/applications
    cp gui/legion-power-gui.desktop ~/.local/share/applications/
}

# 8. System integration
setup_system() {
    echo "🔧 Configuring system integration..."
    
    # PolicyKit
    sudo cp system/polkit/com.legion.power.policy \
            /usr/share/polkit-1/actions/
    
    # Udev
    sudo cp system/udev/99-legion-power.rules \
            /etc/udev/rules.d/
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    
    # Systemd
    sudo cp system/systemd/legion-power.service \
            /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable legion-power.service
    
    # TLP
    sudo mkdir -p /etc/tlp.d
    sudo cp system/tlp.d/50-legion.conf /etc/tlp.d/
    
    # User group
    sudo usermod -a -G users $USER
}

# 9. Disable power-profiles-daemon (conflicts with TLP)
disable_conflicts() {
    echo "⚠️  Disabling conflicting services (power-profiles-daemon)..."
    sudo systemctl stop power-profiles-daemon.service 2>/dev/null || true
    sudo systemctl disable power-profiles-daemon.service 2>/dev/null || true
    sudo systemctl mask power-profiles-daemon.service 2>/dev/null || true
}

# 10. Start services
start_services() {
    echo "🚀 Starting services..."
    sudo systemctl start legion-power.service
    sudo tlp start
}

# Main
main() {
    check_system
    install_deps
    test_acpi
    backup_system
    install_backend
    install_applet
    install_gui
    setup_system
    disable_conflicts
    start_services
    
    echo ""
    echo "✅ INSTALLATION COMPLETE!"
    echo ""
    echo "📝 Next steps:"
    echo "  1. Log out and log back in (for group permissions)"
    echo "  2. Right-click panel → Applets → Add applets"
    echo "  3. Find 'Legion Power Manager' and add it"
    echo "  4. REMOVE or HIDE the old 'Power Manager' applet"
    echo "  5. Click the Legion icon to test!"
    echo ""
    echo "📖 Documentation: ~/Desktop/repos/linux/power/README.md"
}

main
