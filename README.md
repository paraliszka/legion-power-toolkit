# Legion Power Manager

A comprehensive power management solution for Linux on Lenovo Legion laptops (specifically tested on Legion 5 15ARH05). This project provides a D-Bus service, a desktop GUI, and a GNOME Shell extension to control hardware features like battery conservation mode, rapid charge, and thermal power profiles.

## Features

- **Battery Management**
  - **Conservation Mode**: Limits battery charge to ~60% to prolong battery lifespan when plugged in for extended periods.
  - **Rapid Charge**: Increases charging speed (mutually exclusive with Conservation Mode).
  - **Smart Logic**: Automatically handles the mutex between Conservation Mode and Rapid Charge to prevent conflicts.

- **Thermal Control**
  - **Power Profiles**: Switch between Quiet (Blue), Balanced (White), and Performance (Red) modes.
  - **Fan Control**: Monitor and adjust fan behavior (where supported).

- **External Monitor Control (NEW! 🎉)**
  - **DDC/CI Brightness Control**: Adjust external monitor brightness directly from the applet.
  - **Multi-Monitor Support**: Control multiple external displays independently.
  - **Real-time Adjustments**: Changes apply instantly via ddcutil.
  - **Auto-Detection**: Automatically discovers DDC/CI capable monitors.

- **System Integration**
  - **D-Bus Service**: Robust backend service (`com.legion.Power`) for system-wide control.
  - **Settings Persistence**: Automatically restores your last used settings on boot.
  - **Modern UI**: Clean Python/GTK3 interface for easy configuration.
  - **Cinnamon Applet**: Quick access directly from your system tray.

## Screenshots

*(Placeholders for screenshots of the GUI and Applet)*
> ![Main GUI](docs/assets/gui_placeholder.png)
> *The main control panel*

> ![GNOME Applet](docs/assets/applet_placeholder.png)
> *System tray integration*

## Requirements

- **Hardware**: Lenovo Legion Laptop (Legion 5 15ARH05 or similar models with compatible EC).
- **OS**: Linux (tested on Ubuntu/Debian based distributions).
- **Kernel Module**: `acpi_call` (Essential for hardware communication).
- **Software**: Python 3, GTK3, D-Bus.

## Quick Start

1. **Install Dependencies**:
   Ensure you have the `acpi_call` kernel module installed and loaded.
   ```bash
   sudo apt install acpi-call-dkms
   sudo modprobe acpi_call
   ```

2. **Run the Installer**:
   Use the provided script to set up the service, udev rules, and permissions.
   ```bash
   cd applet/legion-power@moodliszka
   ./install.sh
   ```

3. **Start the GUI**:
   Launch the application from your application menu or terminal.
   ```bash
   python3 gui/legion_power_gui.py
   ```

For detailed installation instructions, please refer to [INSTALL.md](INSTALL.md).

## Documentation

- [Installation Guide](INSTALL.md)
- [ACPI Methods & Technical Details](docs/ACPI_METHODS.md)
- [Battery Management Guide](docs/BATTERY_MANAGEMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Credits

Special thanks to the **LenovoLegionLinux** project for their extensive research on ACPI calls and hardware behavior, which made this tool possible.
