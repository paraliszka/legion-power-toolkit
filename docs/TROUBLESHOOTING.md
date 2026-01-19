# Troubleshooting Guide

This document lists common issues and solutions for Legion Power Manager.

## Common Issues

### 1. "Service not running" or D-Bus Error

**Symptoms:**
- GUI shows a connection error.
- GNOME extension shows a warning icon.
- Logs show `dbus.exceptions.DBusException: com.legion.Power was not provided`.

**Solution:**
The background service is not running.
1.  Check service status:
    ```bash
    systemctl status legion-power.service
    ```
2.  Start the service if inactive:
    ```bash
    sudo systemctl start legion-power.service
    ```
3.  Check logs for crash reasons:
    ```bash
    journalctl -u legion-power.service -b
    ```

### 2. "Permission denied" for ACPI calls

**Symptoms:**
- Logs show `PermissionError: [Errno 13] Permission denied: '/proc/acpi/call'`.
- Settings don't change.

**Solution:**
The service runs as root (via systemd), so this shouldn't happen normally. If you are running the backend script manually:
1.  Use `sudo`.
2.  Or ensure udev rules are installed to allow write access to `/proc/acpi/call` (not recommended for security).

### 3. Settings are not saved/restored

**Symptoms:**
- Conservation mode resets after reboot.

**Solution:**
1.  Check if `restore_on_boot` is enabled in configuration.
2.  Check the config file: `~/.config/legion-power/config.json`.
3.  Ensure the `legion-restore.service` is enabled (if applicable) or that `legion-power.service` is starting correctly on boot.

### 4. ACPI Error: AE_NOT_FOUND

**Symptoms:**
- Logs show `ACPI call failed`.

**Solution:**
Your laptop model might not support the specific ACPI paths used by this tool.
- Verify your model is a Lenovo Legion (Gen 5/6).
- Check `docs/ACPI_METHODS.md` to verify paths manually.

## Logs Location

- **Service Logs**: `~/.local/share/legion-power/service.log` (or system journal if running as system service).
- **System Journal**: `journalctl -u legion-power`

## Reporting Bugs

If you encounter a bug not listed here, please open an issue on the repository with:
1.  Your laptop model (e.g., Legion 5 15ARH05).
2.  Output of `uname -a`.
3.  Service logs (`journalctl -u legion-power`).
4.  Description of the behavior.
