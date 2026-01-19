# Legion Power Manager Applet - Quick Start

## Installation (3 Steps)

### 1. Install the Applet
```bash
cd /home/moodliszka/Desktop/repos/linux/power/applet/legion-power@moodliszka
./install.sh
```
Choose option **1** (user installation)

### 2. Restart Cinnamon
Press **Alt+F2**, type `r`, press **Enter**

### 3. Add to Panel
1. Right-click on panel → "Applets"
2. Search for "Legion"
3. Click **+** to add

## Features at a Glance

| Feature | How to Use |
|---------|------------|
| **Battery Status** | Shows automatically in panel |
| **Brightness** | Scroll wheel on applet OR use slider in menu |
| **Keyboard Light** | Middle-click applet OR use slider in menu |
| **Power Profile** | Click applet → Select profile |
| **Conservation Mode** | Click applet → Toggle switch |
| **Rapid Charge** | Click applet → Toggle switch |
| **Fan Mode** | Click applet → Select mode |

## Legion D-Bus Service

Required for Conservation, Rapid Charge, and Fan Mode:

```bash
cd /home/moodliszka/Desktop/repos/linux/power/backend
sudo python3 install_service.py
sudo systemctl enable --now legion-power.service
```

## Testing

Verify everything works:
```bash
cd /home/moodliszka/Desktop/repos/linux/power/applet/legion-power@moodliszka
./test-dbus.sh
```

All items should show ✓

## Common Actions

**Adjust Brightness**:
- Scroll wheel on applet (up/down)
- OR click applet → drag brightness slider

**Toggle Keyboard Backlight**:
- Middle-click on applet

**Enable Conservation Mode** (recommended for AC use):
- Click applet → Toggle "Conservation Mode" ON

**Switch to Performance Mode**:
- Click applet → Click "Performance"

**Set Fan to Quiet**:
- Click applet → Click "Quiet" under Fan Mode

## Troubleshooting

**Applet not in list?**
```bash
ls ~/.local/share/cinnamon/applets/legion-power@moodliszka/
# Should show files
# If empty, re-run ./install.sh
```

**Legion features missing?**
```bash
sudo systemctl status legion-power.service
# Should show "active (running)"
# If not, install the service (see above)
```

**Brightness not working?**
```bash
ps aux | grep cinnamon-settings-daemon
# Should show process running
```

## Configuration

Right-click applet → "Configure..." → Adjust:
- Display format (percentage/time/both)
- Show all batteries or primary only
- Show/hide Legion features

## Documentation

- **README.md** - Full documentation
- **INSTALL.md** - Detailed installation guide
- **FEATURES.md** - Complete feature list
- **SUMMARY.md** - Technical summary

## Quick Tips

💡 **Conservation Mode** extends battery life - use when plugged in most of the time

💡 **Scroll wheel** on applet adjusts brightness - no need to open menu

💡 **Middle-click** toggles keyboard backlight instantly

💡 **Rapid Charge** and **Conservation Mode** can't both be on (automatic)

💡 **Fan Mode** changes take effect immediately - experiment to find your preference

## Support

Check logs if issues occur:
```bash
journalctl -f | grep -i "legion-power"
```

Or use Cinnamon's Looking Glass:
- Press **Alt+F2**
- Type `lg`
- Press **Enter**
- Check "Log" tab

---

**Enjoy your Legion Power Manager!** 🚀
