# Installation Guide

This guide covers the installation, configuration, and removal of the Legion Power Manager.

## Prerequisites

Before installing, ensure your system meets the following requirements:

1.  **Operating System**: Linux (Ubuntu 20.04+, Debian 11+, Fedora 34+, or Arch Linux recommended).
2.  **Hardware**: Lenovo Legion Laptop (Verified on Legion 5 15ARH05).
3.  **Kernel Module**: `acpi_call` must be installed and loaded.

### Installing `acpi_call`

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install acpi-call-dkms
sudo modprobe acpi_call
```

**Arch Linux:**
```bash
sudo pacman -S acpi_call
sudo modprobe acpi_call
```

**Fedora:**
```bash
sudo dnf install acpi_call
sudo modprobe acpi_call
```

*Note: You may need to disable Secure Boot if you are unable to load unsigned kernel modules.*

## Step-by-Step Installation

### 1. Clone the Repository
Clone the project to your local machine:
```bash
git clone https://github.com/moodliszka/legion-power.git
cd legion-power
```

### 2. Install System Dependencies
Install the required Python and GTK libraries.

**Ubuntu/Debian:**
```bash
sudo apt install python3-gi python3-gi-cairo python3-dbus gir1.2-gtk-3.0
```

#### Optional: External Monitor Brightness Control (DDC/CI)

For controlling external monitor brightness via the applet:

**Ubuntu/Debian:**
```bash
sudo apt install ddcutil
```

**Setup i2c permissions:**
```bash
sudo usermod -aG i2c $USER
```
*Note: You need to log out and log back in for group changes to take effect.*

**Verify ddcutil works:**
```bash
ddcutil detect        # Should list your external monitors
ddcutil getvcp 10     # Read brightness (VCP code 0x10)
```

If `ddcutil detect` doesn't find your monitors:
- Check your monitor's OSD settings and enable DDC/CI support
- Ensure the monitor is connected via DisplayPort or HDMI (not VGA)
- Try loading the i2c-dev kernel module: `sudo modprobe i2c-dev`

### 3. Run the Installer script
The included installer script sets up the D-Bus service, systemd units, and permissions.

```bash
cd applet/legion-power@moodliszka
chmod +x install.sh
./install.sh
```

The script performs the following actions:
- Copies the D-Bus configuration to `/etc/dbus-1/system.d/`
- Installs the systemd service to `/etc/systemd/system/`
- Sets up Polkit policies for permission management
- Enables and starts the `legion-power.service`

### 4. Verify the Service
Check if the background service is running correctly:

```bash
systemctl status legion-power.service
```
You should see `Active: active (running)`.

### 5. Install the GNOME Extension (Optional)
If you are using the GNOME Desktop Environment:
1.  Copy the `applet/legion-power@moodliszka` folder to `~/.local/share/gnome-shell/extensions/`.
2.  Restart GNOME Shell (Alt+F2, type `r`, Enter) or log out and log back in.
3.  Enable the extension using **Gnome Extensions** app or **Extension Manager**.

## Post-Install Configuration

The service automatically creates a configuration file at `~/.config/legion-power/config.json` (or similar, managed internally).

By default:
- **Conservation Mode**: Off
- **Rapid Charge**: Off
- **Power Profile**: Balanced
- **Settings Restore**: Enabled (Settings persist across reboot)
- **External Monitors**: Enabled (if ddcutil is installed)

You can change these settings using the GUI application:
```bash
python3 gui/legion_power_gui.py
```

### External Monitor Settings

Right-click the applet icon and select "Configure..." to access:
- **Show external monitor brightness controls**: Enable/disable DDC/CI brightness sliders
- Each detected monitor will appear as a separate slider in the applet menu
- Brightness changes are applied in real-time via ddcutil

## Uninstallation

To remove the application and service:

1.  **Stop and Disable Service**:
    ```bash
    sudo systemctl stop legion-power.service
    sudo systemctl disable legion-power.service
    ```

2.  **Remove System Files**:
    ```bash
    sudo rm /etc/systemd/system/legion-power.service
    sudo rm /etc/dbus-1/system.d/com.legion.Power.conf
    sudo rm /usr/share/polkit-1/actions/com.legion.power.policy
    ```

3.  **Reload Daemons**:
    ```bash
    sudo systemctl daemon-reload
    ```

4.  **Remove Extension**:
    Delete the extension folder from `~/.local/share/gnome-shell/extensions/`.
