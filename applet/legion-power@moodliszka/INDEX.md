# Legion Power Manager Applet - Documentation Index

## Quick Navigation

### 🚀 Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Fast installation and basic usage (5 minutes)
- **[README.md](README.md)** - Overview and introduction
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions

### 📚 Documentation
- **[FEATURES.md](FEATURES.md)** - Complete feature documentation
- **[SUMMARY.md](SUMMARY.md)** - Technical summary and implementation details
- **[This File](INDEX.md)** - Documentation index

### 🛠️ Tools
- **[install.sh](install.sh)** - Automated installation script
- **[test-dbus.sh](test-dbus.sh)** - D-Bus service testing script

### 💻 Source Code
- **[files/legion-power@moodliszka/applet.js](files/legion-power@moodliszka/applet.js)** - Main applet code (1007 lines)
- **[files/legion-power@moodliszka/settings-schema.json](files/legion-power@moodliszka/settings-schema.json)** - Settings configuration
- **[files/legion-power@moodliszka/stylesheet.css](files/legion-power@moodliszka/stylesheet.css)** - CSS styling
- **[files/legion-power@moodliszka/metadata.json](files/legion-power@moodliszka/metadata.json)** - Applet metadata

## What Do You Need?

### "I just want to install it"
→ Read [QUICKSTART.md](QUICKSTART.md) and run `./install.sh`

### "I want to know what features it has"
→ Read [FEATURES.md](FEATURES.md)

### "I'm having installation problems"
→ Read [INSTALL.md](INSTALL.md) - Troubleshooting section

### "I want to understand how it works"
→ Read [SUMMARY.md](SUMMARY.md) and explore `applet.js`

### "I want to know if my Legion laptop is supported"
→ Read [README.md](README.md) - Requirements section

### "I need to verify D-Bus services"
→ Run `./test-dbus.sh`

### "I want to contribute or modify it"
→ Read [SUMMARY.md](SUMMARY.md) - Technical Implementation section

## File Organization

```
legion-power@moodliszka/
│
├── Documentation (Start Here!)
│   ├── QUICKSTART.md          ← Start here for fast setup
│   ├── README.md              ← Overview
│   ├── INSTALL.md             ← Detailed installation
│   ├── FEATURES.md            ← Feature documentation
│   ├── SUMMARY.md             ← Technical details
│   └── INDEX.md               ← This file
│
├── Installation Tools
│   ├── install.sh             ← Run this to install
│   └── test-dbus.sh           ← Run this to test services
│
├── Metadata
│   └── metadata.json          ← Applet package info
│
└── Applet Source Code
    └── files/legion-power@moodliszka/
        ├── applet.js          ← Main code (1007 lines!)
        ├── metadata.json      ← Applet metadata
        ├── settings-schema.json ← Settings config
        ├── stylesheet.css     ← Styling
        └── icon.svg           ← Icon
```

## Documentation Hierarchy

```
Start Here → QUICKSTART.md (5 min read)
    ↓
Need More? → README.md (10 min read)
    ↓
Installing? → INSTALL.md (detailed guide)
    ↓
Want Features? → FEATURES.md (complete list)
    ↓
Deep Dive? → SUMMARY.md (technical)
    ↓
Code Study → applet.js (source code)
```

## Common Workflows

### First Time Installation
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run `./install.sh`
3. Run `./test-dbus.sh` to verify
4. Add applet to panel

### Troubleshooting
1. Check [INSTALL.md](INSTALL.md) - Troubleshooting section
2. Run `./test-dbus.sh` to identify issue
3. Check logs: `journalctl -f | grep legion-power`

### Understanding Features
1. Read [FEATURES.md](FEATURES.md) for feature overview
2. Read [README.md](README.md) for context
3. Try each feature in the applet menu

### Development/Modification
1. Read [SUMMARY.md](SUMMARY.md) for architecture
2. Study `applet.js` source code
3. Test changes by running `cinnamon --replace`
4. Use Looking Glass (Alt+F2, type 'lg') for debugging

## Key Statistics

- **Documentation**: 6 markdown files
- **Source Code**: 1007 lines of JavaScript
- **Installation Scripts**: 2 bash scripts
- **Configuration Files**: 3 (metadata, settings, CSS)
- **Total Project Size**: ~50KB

## Feature Matrix

| Feature | Standard Power | Legion Power | Status |
|---------|---------------|--------------|--------|
| Battery Status | ✓ | ✓ | Complete |
| Screen Brightness | ✓ | ✓ | Complete |
| Keyboard Backlight | ✓ | ✓ | Complete |
| Power Profiles | ✓ | ✓ | Complete |
| Peripheral Batteries | ✓ | ✓ | Complete |
| Conservation Mode | ✗ | ✓ | Complete |
| Rapid Charge | ✗ | ✓ | Complete |
| Fan Control | ✗ | ✓ | Complete |
| GUI Integration | ✗ | ✓ | Complete |

## Support Resources

### Logs
```bash
# Applet logs
journalctl -f | grep -i "legion-power"

# Cinnamon logs
journalctl -f | grep -i cinnamon

# Looking Glass (built-in debugger)
# Press Alt+F2, type 'lg', press Enter
```

### Service Status
```bash
# Check Legion service
sudo systemctl status legion-power.service

# Check UPower
systemctl status upower

# Check Power Profiles
systemctl status power-profiles-daemon
```

### Testing Commands
```bash
# Test all services
./test-dbus.sh

# Test applet installation
ls -la ~/.local/share/cinnamon/applets/legion-power@moodliszka/

# Verify file count
find files/legion-power@moodliszka/ -type f | wc -l
# Should show 5 files
```

## Version Information

- **Applet Version**: 1.0
- **Cinnamon Target**: 6.x (compatible with 4.x, 5.x)
- **UUID**: legion-power@moodliszka
- **Based On**: power@cinnamon.org (Cinnamon official)

## Dependencies

### Required
- Cinnamon Desktop
- UPower
- cinnamon-settings-daemon

### Optional (for full features)
- power-profiles-daemon (for power profiles)
- Legion Power D-Bus service (for Legion features)

### For Development
- gjs (for testing JavaScript syntax)
- Looking Glass (built into Cinnamon)

## Credits

- Based on Cinnamon's official power@cinnamon.org applet
- Legion-specific features added
- Integrates with Legion Power D-Bus service
- Created for Linux Mint / Cinnamon desktop users with Legion laptops

---

**Remember**: Start with [QUICKSTART.md](QUICKSTART.md) for fastest results! 🚀
