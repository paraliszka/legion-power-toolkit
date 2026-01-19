# Legion Power Manager Applet - Installation Guide

## Quick Install (Recommended)

### Step 1: Run the Installation Script
```bash
cd /home/moodliszka/Desktop/repos/linux/power/applet/legion-power@moodliszka
./install.sh
```

Follow the prompts to install the applet to either:
- **Option 1**: User directory (recommended) - `~/.local/share/cinnamon/applets/`
- **Option 2**: System directory (requires sudo) - `/usr/share/cinnamon/applets/`

### Step 2: Restart Cinnamon
Press **Alt+F2**, type `r`, and press **Enter**

OR log out and log back in.

### Step 3: Add the Applet to Panel

1. **Remove the old power applet** (optional but recommended):
   - Right-click on the system power applet in your panel
   - Select "Remove from panel"

2. **Add Legion Power applet**:
   - Right-click anywhere on your panel
   - Select "Applets"
   - In the search box, type "Legion"
   - Find "Legion Power Manager"
   - Click the **+** button to add it to your panel

### Step 4: Configure the Applet
- Right-click on the Legion Power applet
- Select "Configure..."
- Adjust settings to your preference

---

## Manual Installation

If you prefer to install manually:

### User Installation
```bash
# Create directory if it doesn't exist
mkdir -p ~/.local/share/cinnamon/applets/

# Copy applet files
cp -r /home/moodliszka/Desktop/repos/linux/power/applet/legion-power@moodliszka/files/legion-power@moodliszka \
     ~/.local/share/cinnamon/applets/

# Set permissions
chmod -R 755 ~/.local/share/cinnamon/applets/legion-power@moodliszka

# Restart Cinnamon (Alt+F2, type 'r', press Enter)
```

### System Installation
```bash
# Copy to system directory
sudo cp -r /home/moodliszka/Desktop/repos/linux/power/applet/legion-power@moodliszka/files/legion-power@moodliszka \
          /usr/share/cinnamon/applets/

# Set ownership and permissions
sudo chown -R root:root /usr/share/cinnamon/applets/legion-power@moodliszka
sudo chmod -R 755 /usr/share/cinnamon/applets/legion-power@moodliszka

# Restart Cinnamon (Alt+F2, type 'r', press Enter)
```

---

## Installing the Legion D-Bus Service

The Legion-specific features (Conservation Mode, Rapid Charge, Fan Control) require the Legion Power D-Bus service.

### Check if Service is Running
```bash
sudo systemctl status legion-power.service
```

### Install the Service (if not already installed)
```bash
# Navigate to backend directory
cd /home/moodliszka/Desktop/repos/linux/power/backend

# Run installation script
sudo python3 install_service.py

# Enable service to start on boot
sudo systemctl enable legion-power.service

# Start the service now
sudo systemctl start legion-power.service

# Verify it's running
sudo systemctl status legion-power.service
```

---

## Testing the Installation

### Test D-Bus Services
Run the test script to verify all required services are available:

```bash
cd /home/moodliszka/Desktop/repos/linux/power/applet/legion-power@moodliszka
./test-dbus.sh
```

Expected output:
```
=========================================
Legion Power Applet - D-Bus Service Test
=========================================

1. Testing Screen Brightness Service...
   ✓ Screen brightness service is available

2. Testing Keyboard Brightness Service...
   ✓ Keyboard brightness service is available

3. Testing UPower Service...
   ✓ UPower service is available

4. Testing Power Profiles Service (Hadess)...
   ✓ Hadess PowerProfiles service is available
     Current profile: balanced

5. Testing Legion Power Service...
   ✓ Legion Power service is running
     Conservation Mode: false
     Rapid Charge: false
     Fan Mode: 1 (0=Quiet, 1=Auto, 2=Performance)
```

### Test the Applet
```bash
# Check if applet is installed
ls -la ~/.local/share/cinnamon/applets/legion-power@moodliszka/

# Check Cinnamon logs for errors
journalctl -f | grep -i "legion-power"
```

---

## Troubleshooting

### Applet Not Appearing in Applets List

**Problem**: Cannot find "Legion Power Manager" in Applets menu

**Solution**:
```bash
# Check installation
ls -la ~/.local/share/cinnamon/applets/legion-power@moodliszka/

# Verify metadata.json exists
cat ~/.local/share/cinnamon/applets/legion-power@moodliszka/metadata.json

# Restart Cinnamon
# Press Alt+F2, type 'r', press Enter

# Check for JavaScript errors in Looking Glass
# Press Alt+F2, type 'lg', press Enter
# Go to "Log" tab
```

### Legion Features Not Working

**Problem**: Conservation Mode, Rapid Charge, and Fan Mode are missing or not working

**Solution**:
```bash
# Check if Legion service is running
sudo systemctl status legion-power.service

# If not running, start it
sudo systemctl start legion-power.service

# Check service logs
sudo journalctl -u legion-power.service -f

# Test D-Bus connection manually
dbus-send --system --print-reply \
  --dest=com.legion.Power \
  /com/legion/Power/Manager \
  org.freedesktop.DBus.Properties.Get \
  string:"com.legion.Power.Manager" \
  string:"ConservationMode"
```

### Brightness Sliders Not Working

**Problem**: Screen or keyboard brightness sliders are missing

**Solution**:
```bash
# Check if cinnamon-settings-daemon is running
ps aux | grep cinnamon-settings-daemon

# If not running, start it
cinnamon-settings-daemon &

# Test screen brightness D-Bus
dbus-send --session --print-reply \
  --dest=org.cinnamon.SettingsDaemon.Power.Screen \
  /org/cinnamon/SettingsDaemon/Power/Screen \
  org.cinnamon.SettingsDaemon.Power.Screen.GetPercentage
```

### Applet Shows Error Icon

**Problem**: Applet appears but shows error icon or missing battery icon

**Solution**:
```bash
# Check UPower service
systemctl status upower

# Restart UPower if needed
sudo systemctl restart upower

# Check Looking Glass for errors
# Alt+F2, type 'lg', press Enter
# Go to "Log" tab, look for errors
```

### Power Profiles Not Available

**Problem**: Power profile section is missing

**Solution**:
```bash
# Check if power-profiles-daemon is installed
systemctl status power-profiles-daemon

# Or check for TLP (alternative power management)
systemctl status tlp

# Install power-profiles-daemon if needed (Debian/Ubuntu)
sudo apt install power-profiles-daemon

# Enable and start service
sudo systemctl enable power-profiles-daemon
sudo systemctl start power-profiles-daemon
```

---

## Uninstallation

### Remove the Applet

1. Remove from panel:
   - Right-click on Legion Power applet
   - Select "Remove from panel"

2. Delete applet files:

   **User installation**:
   ```bash
   rm -rf ~/.local/share/cinnamon/applets/legion-power@moodliszka
   ```

   **System installation**:
   ```bash
   sudo rm -rf /usr/share/cinnamon/applets/legion-power@moodliszka
   ```

3. Restart Cinnamon:
   - Press Alt+F2, type 'r', press Enter

### Re-add Standard Power Applet

1. Right-click on panel
2. Select "Applets"
3. Search for "Power Manager"
4. Click **+** to add the standard power applet

---

## Verification Checklist

After installation, verify the following:

- [ ] Applet appears in panel
- [ ] Battery percentage shows correctly
- [ ] Screen brightness slider works
- [ ] Scroll wheel on applet adjusts brightness
- [ ] Keyboard brightness slider appears (if supported)
- [ ] Middle-click toggles keyboard backlight
- [ ] Power profiles section appears
- [ ] Can switch between power profiles
- [ ] Peripheral battery devices appear (if any)
- [ ] Legion Controls section appears
- [ ] Conservation Mode toggle works
- [ ] Rapid Charge toggle works (if supported)
- [ ] Fan Mode selector works
- [ ] "Open Legion Power Manager" button works

---

## Getting Help

### Check Logs
```bash
# Cinnamon logs
journalctl -f | grep -i cinnamon

# Legion service logs
sudo journalctl -u legion-power.service -f

# Looking Glass (Cinnamon's built-in debugger)
# Press Alt+F2, type 'lg', press Enter
```

### Report Issues
If you encounter issues, include:
1. Your Linux distribution and version
2. Cinnamon version (`cinnamon --version`)
3. Legion laptop model
4. Output of `./test-dbus.sh`
5. Relevant log excerpts

---

## Next Steps

After successful installation:
1. Configure display preferences (right-click applet → Configure)
2. Set your preferred power profile
3. Enable Conservation Mode if you use AC power primarily
4. Adjust fan mode based on your noise preference
5. Explore keyboard shortcuts (if configured)

Enjoy your Legion Power Manager!
