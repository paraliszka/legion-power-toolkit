# Legion Power Manager GUI

A Python GTK3 application for managing power settings on Lenovo Legion laptops on Linux.

## Features

- **Battery Management**: Toggle Conservation Mode (60% limit) and Rapid Charge.
- **Performance Control**: Switch between Quiet, Balanced, and Performance power profiles.
- **Monitoring**: Real-time visualization of battery status, CPU/GPU temperatures, and Fan speed.
- **Settings**: Auto-switching profiles and notification preferences.

## Requirements

- Python 3.6+
- GTK 3
- PyGObject
- UPower (for battery info)
- Legion Power Backend (D-Bus service)

## Installation

1. Ensure dependencies are installed:
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
   ```

2. Run the application:
   ```bash
   python3 legion_power_gui.py
   ```

3. To install the desktop entry:
   ```bash
   cp legion-power-gui.desktop ~/.local/share/applications/
   ```

## Structure

- `legion_power_gui.py`: Main entry point
- `widgets/`: Custom GTK widgets (Gauges, Toggles)
- `assets/`: Icons and resources

## License

MIT
