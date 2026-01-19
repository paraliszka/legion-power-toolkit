# Changelog - External Monitor Brightness Control

## 🎉 NEW FEATURE: DDC/CI Monitor Brightness Control

**Date:** 2026-01-17  
**Version:** 1.1.0

### What's New

Added support for controlling external monitor brightness directly from the Cinnamon applet using DDC/CI protocol via `ddcutil`.

### Features Added

#### 🖥️ External Monitor Control
- **Auto-detection** of DDC/CI capable monitors
- **Individual brightness sliders** for each detected monitor
- **Real-time brightness adjustment** via ddcutil
- **Multi-monitor support** - control multiple displays independently
- **Smart caching** - monitors detected once and cached for 30s for performance
- **Auto-refresh** - brightness values updated every 30 seconds
- **Graceful degradation** - applet works even if DDC is unavailable

#### 🔧 Technical Implementation
- **Backend Module:** `backend/ddc_monitor.py`
  - DDCController class for monitor management
  - Parser for ddcutil detect output
  - Brightness control via VCP code 0x10
  - Error handling and timeout management

- **D-Bus Methods:** Added to `com.legion.Power.Manager`
  - `GetExternalMonitors()` - returns array of detected monitors
  - `GetMonitorBrightness(display_id)` - get brightness (0-100)
  - `SetMonitorBrightness(display_id, brightness)` - set brightness
  - `RefreshExternalMonitors()` - invalidate cache
  - `MonitorBrightnessChanged` - signal on brightness change

- **Frontend:** Cinnamon Applet (`applet.js`)
  - `MonitorBrightnessSlider` class - custom slider for external monitors
  - Auto-setup on applet initialization
  - Settings toggle to show/hide monitor controls
  - Section header "External Monitors" in menu

#### ⚙️ Configuration
- **New Setting:** "Show external monitor brightness controls"
  - Default: Enabled
  - Can be toggled in applet configuration

### Files Added

```
backend/ddc_monitor.py              # DDC/CI controller module
scripts/update_backend.sh           # Backend update script
test_ddc_integration.py             # Integration test script
DEPLOYMENT.md                       # Deployment & troubleshooting guide
CHANGES.md                          # This file
```

### Files Modified

```
backend/legion_power_service.py    # Added DDC D-Bus methods
applet.js                           # Added MonitorBrightnessSlider
settings-schema.json                # Added show-external-monitors option
INSTALL.md                          # Added DDC/CI setup instructions
README.md                           # Added external monitor features
```

### Requirements

#### New Dependencies
- **ddcutil** - Required for DDC/CI communication
  ```bash
  sudo apt install ddcutil
  ```

#### Permissions
- User must be in `i2c` group:
  ```bash
  sudo usermod -aG i2c $USER
  ```
  (Requires logout/login to take effect)

#### Hardware
- Monitor connected via **DisplayPort** or **HDMI** (not VGA)
- Monitor must support **DDC/CI** (check OSD settings)

### Usage

1. **Install ddcutil and setup permissions** (see INSTALL.md)
2. **Update backend:**
   ```bash
   sudo ./scripts/update_backend.sh
   ```
3. **Update applet** (copy to ~/.local/share/cinnamon/applets/)
4. **Reload Cinnamon:** Alt+F2, type `r`, Enter
5. **Enable in settings:** Right-click applet → Configure → Enable "Show external monitor brightness controls"
6. **Use:** Click applet → See "External Monitors" section with sliders

### Testing

Run the integration test:
```bash
python3 test_ddc_integration.py
```

Should output:
```
✅ Direct DDC:      ✅ PASS
✅ D-Bus Service:   ✅ PASS
🎉 All tests passed!
```

### Known Limitations

1. **Speed:** DDC/CI via I2C is inherently slow (~0.5-1s per command)
   - This is normal and expected
   - Brightness changes are not instant like internal display

2. **Compatibility:** Not all monitors support DDC/CI
   - USB-C to HDMI adapters may not support DDC
   - Some monitors have DDC disabled by default in OSD

3. **Permissions:** Requires i2c group membership
   - Must logout/login after adding to group

4. **Detection:** Monitors detected via ddcutil
   - May take 2-5 seconds on first detection
   - Cached for 30 seconds for performance

### Troubleshooting

See detailed troubleshooting in `DEPLOYMENT.md`

**Common issues:**
- "No monitors detected" → Check `ddcutil detect`
- "Permission denied" → Add to i2c group and logout/login
- "Method not found" → Run `sudo ./scripts/update_backend.sh`

### Future Enhancements

Potential improvements for future versions:
- [ ] Faster DDC implementation using libddcutil directly
- [ ] Monitor profiles (save/restore brightness per monitor)
- [ ] Ambient light sensor integration
- [ ] Keyboard shortcuts for brightness control
- [ ] Support for other VCP codes (contrast, input source, etc.)

### Credits

Implementation by moodliszka, powered by:
- **ddcutil** by Sanford Rockowitz
- **D-Bus** by freedesktop.org
- **Cinnamon** desktop environment

---

**Upgrade from 1.0.x:**
No breaking changes. All existing features remain fully functional.
External monitor control is an optional feature that can be disabled.
