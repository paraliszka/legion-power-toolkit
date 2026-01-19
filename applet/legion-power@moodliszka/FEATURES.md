# Legion Power Manager Applet - Complete Feature List

## Overview
This Cinnamon applet is a **complete replacement** for the system `power@cinnamon.org` applet with additional Legion laptop-specific features.

## Standard Power Management Features

### 1. Battery Status Display
- **Primary Battery**: Shows main laptop battery status
- **Peripheral Devices**: Displays battery level for wireless devices:
  - Wireless Mouse
  - Wireless Keyboard
  - Bluetooth Headphones
  - Gaming Controllers
  - Other Bluetooth devices
- **Status Information**:
  - Battery percentage
  - Time remaining (charging/discharging)
  - Charging state (charging, discharging, fully charged)
- **Panel Display Options**:
  - Show percentage only
  - Show time remaining only
  - Show percentage + time
  - Hide label (icon only)
- **Dynamic Icons**: Battery icon changes based on:
  - Charge level (empty, low, medium, high, full)
  - Charging state (bolt symbol when charging)

### 2. Screen Brightness Control
- **D-Bus Service**: `org.cinnamon.SettingsDaemon.Power.Screen`
- **Features**:
  - Interactive slider in menu
  - Scroll wheel on applet icon to adjust brightness
  - Step-based adjustment (respects system step value)
  - Minimum brightness protection
  - Real-time percentage display
  - Tooltip shows current brightness level

### 3. Keyboard Backlight Control
- **D-Bus Service**: `org.cinnamon.SettingsDaemon.Power.Keyboard`
- **Features**:
  - Interactive slider in menu
  - Middle-click on applet icon to toggle on/off
  - Step-based adjustment
  - Real-time percentage display
  - Automatically hidden if keyboard backlight not supported

### 4. Power Profiles
- **D-Bus Services**: 
  - `net.hadess.PowerProfiles` (primary)
  - `org.freedesktop.UPower.PowerProfiles` (fallback)
- **Available Profiles**:
  - **Power Saver**: Maximum battery life, reduced performance
  - **Balanced**: Balance between performance and battery life
  - **Performance**: Maximum performance, higher power consumption
- **Features**:
  - Quick profile switching from menu
  - Visual indicator shows current active profile
  - Persists across reboots

### 5. Multiple Battery Support
- **Setting**: "Always show all batteries"
- **When Enabled**: Shows all battery devices in panel
- **When Disabled**: Shows only primary battery
- **Supports**: Up to multiple battery devices with individual status

## Legion-Specific Features

### 6. Conservation Mode
- **D-Bus Property**: `com.legion.Power.Manager.ConservationMode`
- **Type**: Boolean (true/false)
- **Function**: Limits battery charging to 60% to extend battery lifespan
- **Use Case**: When laptop is primarily used on AC power
- **Mutex**: Automatically disables Rapid Charge when enabled
- **Toggle**: Simple switch in menu

### 7. Rapid Charge
- **D-Bus Property**: `com.legion.Power.Manager.RapidCharge`
- **Type**: Boolean (true/false)
- **Function**: Enables faster charging (typically 80% in 30 minutes)
- **Use Case**: When you need to charge battery quickly
- **Mutex**: Automatically disables Conservation Mode when enabled
- **Toggle**: Simple switch in menu
- **Note**: Some Legion models don't support this feature

### 8. Fan Mode Control
- **D-Bus Property**: `com.legion.Power.Manager.FanMode`
- **Type**: Integer (0, 1, or 2)
- **Available Modes**:
  - **0 - Quiet**: Minimal fan noise, lower cooling performance
  - **1 - Auto**: Automatic fan control based on temperature
  - **2 - Performance**: Maximum cooling, higher fan noise
- **Visual Indicator**: Dot shows currently active mode
- **Quick Switching**: Click any mode to activate immediately

### 9. Open Legion Power Manager
- **Button**: "Open Legion Power Manager"
- **Function**: Launches the full Legion Power Manager GUI
- **Command**: `legion-power-gui`
- **Use Case**: Access additional settings and monitoring

## User Interface Features

### Panel Icon
- **Dynamic Battery Icon**: Changes based on charge level and state
- **Scroll Wheel Support**: Adjust screen brightness
- **Middle-Click**: Toggle keyboard backlight
- **Left-Click**: Open menu

### Popup Menu Structure
```
┌─────────────────────────────────────┐
│ Laptop Battery 85%                  │
│ Charging - 1 hour until fully ch... │
├─────────────────────────────────────┤
│ Mouse 95%                           │
│ Battery good                        │
├─────────────────────────────────────┤
│ [☀️] ══════════════○═══ 75%         │  ← Screen Brightness
│ [⌨️] ══════════════○═══ 50%         │  ← Keyboard Backlight
├─────────────────────────────────────┤
│ • Power Saver                       │
│   Balanced                          │
│   Performance                       │
├─────────────────────────────────────┤
│ Legion Controls                     │
│ [✓] Conservation Mode               │
│ [ ] Rapid Charge                    │
│ Fan Mode                            │
│ • Quiet                             │
│   Auto                              │
│   Performance                       │
│ Open Legion Power Manager           │
├─────────────────────────────────────┤
│ Power Settings                      │
└─────────────────────────────────────┘
```

## Settings Configuration

### Available Settings
1. **Display**: Choose what to show in panel
   - Show percentage
   - Show time remaining
   - Show percentage and time remaining
   - Hide label

2. **Always show all batteries**: 
   - Disabled: Show only primary battery
   - Enabled: Show all battery devices

3. **Show Legion-specific features**:
   - Disabled: Hide Legion controls (standard power applet)
   - Enabled: Show all Legion features

## Technical Implementation

### D-Bus Interfaces Used
1. **UPower** (`org.freedesktop.UPower`):
   - Battery device enumeration
   - Battery status monitoring
   - Device property queries

2. **Cinnamon Settings Daemon** (`org.cinnamon.SettingsDaemon.Power`):
   - Screen brightness control
   - Keyboard backlight control
   - Device management

3. **Power Profiles** (`net.hadess.PowerProfiles` or `org.freedesktop.UPower.PowerProfiles`):
   - Power profile management
   - Active profile queries
   - Profile switching

4. **Legion Power** (`com.legion.Power.Manager`):
   - Conservation Mode control
   - Rapid Charge control
   - Fan Mode control
   - Property change notifications

### Update Mechanism
- **Battery Status**: Updates via D-Bus signals
- **Brightness**: Real-time updates via D-Bus signals
- **Power Profiles**: Updates via D-Bus property change signals
- **Legion Controls**: Updates via custom PropertiesChanged signal
- **Menu Open**: Forced refresh when menu is opened

### Error Handling
- Graceful degradation if Legion service not available
- Continues to function as standard power applet
- Hides unsupported features automatically
- Logs errors to Cinnamon log (Looking Glass)

## Compatibility

### Cinnamon Version
- Tested on: Cinnamon 6.x
- Should work on: Cinnamon 4.x, 5.x, 6.x

### Legion Laptop Support
- **Conservation Mode**: Most Legion laptops (2019+)
- **Rapid Charge**: Select Legion models (check your model)
- **Fan Mode**: Legion laptops with ACPI platform driver

### Linux Kernel
- Requires: Legion laptop ACPI driver
- Kernel modules: `ideapad_laptop` or custom Legion driver

## Benefits Over Standard Power Applet

1. **Single Unified Interface**: No need for separate tools
2. **Persistent Settings**: Legion features accessible from panel
3. **Quick Access**: One click to change fan mode or enable conservation
4. **Integrated Experience**: Legion controls alongside standard power management
5. **Battery Longevity**: Easy access to conservation mode
6. **Performance Control**: Quick fan mode switching

## Future Enhancement Possibilities

- [ ] Battery health monitoring
- [ ] Custom fan curves
- [ ] Temperature display
- [ ] Power consumption graphs
- [ ] Charge limit customization (beyond 60%)
- [ ] Notification on battery events
- [ ] Auto-profile switching based on AC/battery
- [ ] GPU mode switching (hybrid/discrete)
