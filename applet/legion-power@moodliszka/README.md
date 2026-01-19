# Legion Power Manager Applet

A complete Cinnamon panel applet for Legion laptop power management. This applet is a **full replacement** for the system `power@cinnamon.org` applet with additional Legion-specific features.

## Features

### Standard Power Management Features
- **Battery Status Display**: Shows battery percentage, time remaining, and charging state
- **Screen Brightness Control**: Slider and scroll wheel support
- **Keyboard Backlight Control**: Slider with middle-click toggle
- **Multiple Battery Devices**: Support for wireless mouse, keyboard, headphones, etc.
- **Power Profiles**: Quick switching between Power Saver, Balanced, and Performance modes
- **Dynamic Icons**: Battery icon changes based on charge level and state

### Legion-Specific Features
- **Conservation Mode**: Toggle battery conservation (caps charging at 60%)
- **Rapid Charge**: Enable rapid charging mode
- **Fan Mode Control**: Switch between Quiet, Auto, and Performance fan profiles
- **Mutex Logic**: Conservation Mode and Rapid Charge are mutually exclusive
- **Quick Access**: "Open Legion Power Manager" button launches the full GUI

## Installation

### Method 1: Copy to User Directory
```bash
# Copy the applet to your local applets directory
cp -r legion-power@moodliszka ~/.local/share/cinnamon/applets/

# Restart Cinnamon (Alt+F2, type 'r', press Enter)
# Or log out and log back in
```

### Method 2: Copy to System Directory (requires sudo)
```bash
# Copy to system applets directory
sudo cp -r legion-power@moodliszka /usr/share/cinnamon/applets/

# Restart Cinnamon
```

### Activating the Applet

1. **Remove the old power applet** (if present):
   - Right-click on the system power applet in your panel
   - Select "Remove from panel"

2. **Add the Legion Power applet**:
   - Right-click on your panel
   - Select "Applets"
   - Search for "Legion Power Manager"
   - Click the "+" button to add it to your panel

3. **Configure the applet**:
   - Right-click on the applet
   - Select "Configure..."
   - Adjust display options and enable/disable Legion features

## Requirements

### Required D-Bus Services

The applet requires these D-Bus services to be running:

1. **org.cinnamon.SettingsDaemon.Power** (standard, usually already running)
2. **net.hadess.PowerProfiles** or **org.freedesktop.UPower.PowerProfiles** (for power profiles)
3. **com.legion.Power** (for Legion-specific features)

### Installing the Legion D-Bus Service

The Legion-specific features require the Legion Power D-Bus service to be running:

```bash
# Navigate to the backend directory
cd /home/moodliszka/Desktop/repos/linux/power/backend

# Install the service
sudo python3 install_service.py

# Enable and start the service
sudo systemctl enable legion-power.service
sudo systemctl start legion-power.service

# Check service status
sudo systemctl status legion-power.service
```

## Configuration Options

### Display Options
- **Show percentage**: Display battery percentage in panel
- **Show time remaining**: Display time until full/empty
- **Show percentage and time**: Display both
- **Hide label**: Only show icon

### Advanced Options
- **Always show all batteries**: Display all battery devices in panel
- **Show Legion-specific features**: Enable/disable Legion controls

## Troubleshooting

### Applet not appearing
```bash
# Check if files are in the correct location
ls -la ~/.local/share/cinnamon/applets/legion-power@moodliszka/

# Check Cinnamon logs
journalctl -f | grep -i legion
```

### Legion features not working
```bash
# Check if Legion D-Bus service is running
sudo systemctl status legion-power.service

# Test D-Bus connection
dbus-send --system --print-reply \
  --dest=com.legion.Power \
  /com/legion/Power/Manager \
  org.freedesktop.DBus.Properties.Get \
  string:"com.legion.Power.Manager" \
  string:"ConservationMode"
```

### Brightness controls not working
```bash
# Check if cinnamon-settings-daemon is running
ps aux | grep cinnamon-settings-daemon

# Restart it if needed
killall cinnamon-settings-daemon
cinnamon-settings-daemon &
```

## File Structure

```
legion-power@moodliszka/
├── metadata.json                              # Outer metadata
└── files/
    └── legion-power@moodliszka/
        ├── metadata.json                      # Inner metadata
        ├── applet.js                          # Main applet code
        ├── settings-schema.json               # Settings configuration
        ├── stylesheet.css                     # CSS styling
        └── icon.svg                           # Applet icon
```

## D-Bus Interfaces Used

### Screen Brightness
- **Service**: org.cinnamon.SettingsDaemon.Power.Screen
- **Methods**: GetPercentage, SetPercentage, StepUp, StepDown, Toggle

### Keyboard Brightness
- **Service**: org.cinnamon.SettingsDaemon.Power.Keyboard
- **Methods**: GetPercentage, SetPercentage, StepUp, StepDown, Toggle

### Legion Controls
- **Service**: com.legion.Power.Manager
- **Properties**: ConservationMode (bool), RapidCharge (bool), FanMode (int)
- **Signals**: PropertiesChanged

### UPower
- **Service**: org.freedesktop.UPower
- **Interface**: UPowerGlib for battery device enumeration

## Development

### Debugging
Enable debug logging in Cinnamon:
```bash
# Watch logs in real-time
journalctl -f | grep -i "legion-power"

# Or check Looking Glass (Alt+F2, type 'lg', press Enter)
# Go to "Log" tab to see JavaScript errors
```

### Reloading Changes
After editing the applet:
```bash
# Quick reload (Alt+F2, type 'r', press Enter)
# Or:
cinnamon --replace &
```

## License

This applet follows the same license as Cinnamon (GPL-2.0+).

## Credits

Based on the official Cinnamon `power@cinnamon.org` applet with Legion-specific enhancements.
