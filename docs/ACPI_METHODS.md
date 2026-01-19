# ACPI Methods Documentation

This document details the ACPI (Advanced Configuration and Power Interface) methods used by Legion Power Manager to communicate with the laptop's Embedded Controller (EC). These methods are specific to the Lenovo Legion 5 15ARH05 and potentially compatible models.

## Overview

The application writes specific commands to `/proc/acpi/call` to trigger hardware functions. This requires the `acpi_call` kernel module.

### ACPI Call Interface
- **Path**: `/proc/acpi/call`
- **Mechanism**: Strings are written to this file (e.g., `\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x03`), and the result is read back.

## Method Reference

### 1. Battery Conservation Mode
Limits battery charging to approximately 60% capacity to extend battery lifespan.

- **Method**: `\_SB.PCI0.LPC0.EC0.VPC0.SBMC`
- **Read Status**: `\_SB.PCI0.LPC0.EC0.BTSG`
  - Returns `0x1`: Enabled
  - Returns `0x0`: Disabled

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `0x03`    | Enable Conservation Mode |
| `0x05`    | Disable Conservation Mode |

---

### 2. Rapid Charge
Increases charging current for faster battery replenishment.

- **Method**: `\_SB.PCI0.LPC0.EC0.VPC0.SBMC`
- **Read Status**: `\_SB.PCI0.LPC0.EC0.FCGM`
  - Returns `0x1`: Enabled
  - Returns `0x0`: Disabled

**Parameters:**
| Parameter | Description |
|-----------|-------------|
| `0x07`    | Enable Rapid Charge |
| `0x08`    | Disable Rapid Charge |

> **Important**: Conservation Mode and Rapid Charge are mutually exclusive. Enabling one must disable the other.

---

### 3. Power Profiles (DYTC)
Controls the Dynamic Thermal Control (DYTC) system, affecting fan curves and CPU/GPU power limits.

- **Method**: `\_SB.PCI0.LPC0.EC0.VPC0.DYTC`

**Parameters:**
| Mode | Parameter (Hex) | LED Color | Description |
|------|-----------------|-----------|-------------|
| **Quiet** | `0x0013B001` | Blue | Limits performance for silent operation and battery saving. |
| **Balanced** | `0x000FB001` | White | Default balance between noise and performance. |
| **Performance** | `0x0012B001` | Red | Max fan speed and higher power limits (often requires AC power). |

## Troubleshooting ACPI Calls

If ACPI calls fail, verify the following:

1.  **Module Loaded**:
    Check if `acpi_call` is loaded:
    ```bash
    lsmod | grep acpi_call
    ```

2.  **File Existence**:
    Ensure the interface file exists:
    ```bash
    ls -l /proc/acpi/call
    ```

3.  **Method Availability**:
    To test if a method exists on your specific hardware, try calling it manually (proceed with caution):
    ```bash
    echo '\_SB.PCI0.LPC0.EC0.BTSG' | sudo tee /proc/acpi/call
    sudo cat /proc/acpi/call
    ```
    If you get `Error: AE_NOT_FOUND`, your hardware uses different ACPI paths.

## References
- [Arch Wiki - Lenovo Legion 5](https://wiki.archlinux.org/title/Lenovo_Legion_5)
- [LenovoLegionLinux Project](https://github.com/antony-jr/lenovo-legion-linux)
