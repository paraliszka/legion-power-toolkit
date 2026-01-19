#!/usr/bin/env python3
"""
Legion Sysfs Interface
Handles sysfs operations for Lenovo Legion 5 15ARH05
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SysfsError(Exception):
    """Raised when sysfs operation fails"""
    pass


class LegionSysfs:
    """
    Sysfs interface for Lenovo Legion 5
    
    Manages:
    - Conservation mode (via sysfs as fallback)
    - Fan mode (quiet/auto/performance)
    - Camera power
    - USB charging
    - Fn lock
    """
    
    # Base path for Lenovo IdeaPad ACPI
    VPC_BASE = "/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00"
    
    # Sysfs attributes
    CONSERVATION_MODE = "conservation_mode"
    FAN_MODE = "fan_mode"
    CAMERA_POWER = "camera_power"
    USB_CHARGING = "usb_charging"
    FN_LOCK = "fn_lock"
    
    # Fan mode values
    FAN_AUTO = 0
    FAN_QUIET = 1
    FAN_PERFORMANCE = 2
    
    def __init__(self):
        """Initialize sysfs interface"""
        self._check_vpc_available()
        self._vpc_path = Path(self.VPC_BASE)
    
    def _check_vpc_available(self):
        """Check if VPC device is available"""
        if not os.path.exists(self.VPC_BASE):
            raise SysfsError(
                f"VPC device not found at {self.VPC_BASE}. "
                f"Is ideapad_laptop module loaded?"
            )
    
    def _read_sysfs(self, attribute: str) -> str:
        """
        Read value from sysfs attribute
        
        Args:
            attribute: Attribute name (e.g., "conservation_mode")
        
        Returns:
            Value as string
        
        Raises:
            SysfsError: If read fails
        """
        path = self._vpc_path / attribute
        
        try:
            with open(path, 'r') as f:
                value = f.read().strip()
            logger.debug(f"Read {attribute}: {value}")
            return value
        except FileNotFoundError:
            raise SysfsError(f"Attribute {attribute} not found at {path}")
        except PermissionError:
            raise SysfsError(f"Permission denied reading {attribute}")
        except Exception as e:
            raise SysfsError(f"Failed to read {attribute}: {e}")
    
    def _write_sysfs(self, attribute: str, value: str) -> None:
        """
        Write value to sysfs attribute
        
        Args:
            attribute: Attribute name (e.g., "conservation_mode")
            value: Value to write
        
        Raises:
            SysfsError: If write fails
        """
        path = self._vpc_path / attribute
        
        try:
            with open(path, 'w') as f:
                f.write(str(value))
            logger.debug(f"Wrote {attribute}: {value}")
        except FileNotFoundError:
            raise SysfsError(f"Attribute {attribute} not found at {path}")
        except PermissionError:
            raise SysfsError(
                f"Permission denied writing {attribute}. "
                f"Check udev rules or run with appropriate permissions."
            )
        except Exception as e:
            raise SysfsError(f"Failed to write {attribute}: {e}")
    
    def get_conservation_mode(self) -> bool:
        """
        Get conservation mode status via sysfs
        
        Returns:
            True if enabled, False otherwise
        """
        try:
            value = self._read_sysfs(self.CONSERVATION_MODE)
            return value == "1"
        except SysfsError as e:
            logger.error(f"Failed to get conservation mode: {e}")
            raise
    
    def set_conservation_mode(self, enable: bool) -> None:
        """
        Set conservation mode via sysfs
        
        Args:
            enable: True to enable, False to disable
        """
        try:
            value = "1" if enable else "0"
            self._write_sysfs(self.CONSERVATION_MODE, value)
            logger.info(f"Conservation mode {'enabled' if enable else 'disabled'} (sysfs)")
        except SysfsError as e:
            logger.error(f"Failed to set conservation mode: {e}")
            raise
    
    def get_fan_mode(self) -> str:
        """
        Get current fan mode
        
        Returns:
            One of "auto", "quiet", "performance"
        """
        try:
            value = int(self._read_sysfs(self.FAN_MODE))
            
            mode_map = {
                self.FAN_AUTO: "auto",
                self.FAN_QUIET: "quiet",
                self.FAN_PERFORMANCE: "performance"
            }
            
            return mode_map.get(value, "unknown")
        except SysfsError as e:
            logger.error(f"Failed to get fan mode: {e}")
            raise
    
    def set_fan_mode(self, mode: str) -> None:
        """
        Set fan mode
        
        Args:
            mode: One of "auto", "quiet", "performance"
        
        Raises:
            ValueError: If mode is invalid
        """
        mode_map = {
            "auto": self.FAN_AUTO,
            "quiet": self.FAN_QUIET,
            "performance": self.FAN_PERFORMANCE
        }
        
        if mode not in mode_map:
            raise ValueError(
                f"Invalid fan mode: {mode}. "
                f"Must be one of: {', '.join(mode_map.keys())}"
            )
        
        try:
            value = mode_map[mode]
            self._write_sysfs(self.FAN_MODE, str(value))
            logger.info(f"Fan mode set to: {mode}")
        except SysfsError as e:
            logger.error(f"Failed to set fan mode: {e}")
            raise
    
    def get_camera_power(self) -> bool:
        """Get camera power status"""
        try:
            value = self._read_sysfs(self.CAMERA_POWER)
            return value == "1"
        except SysfsError:
            return False  # Not critical
    
    def set_camera_power(self, enable: bool) -> None:
        """Set camera power"""
        try:
            value = "1" if enable else "0"
            self._write_sysfs(self.CAMERA_POWER, value)
        except SysfsError as e:
            logger.warning(f"Failed to set camera power: {e}")
    
    def get_usb_charging(self) -> bool:
        """Get USB charging status"""
        try:
            value = self._read_sysfs(self.USB_CHARGING)
            return value == "1"
        except SysfsError:
            return False
    
    def set_usb_charging(self, enable: bool) -> None:
        """Set USB charging"""
        try:
            value = "1" if enable else "0"
            self._write_sysfs(self.USB_CHARGING, value)
        except SysfsError as e:
            logger.warning(f"Failed to set USB charging: {e}")
    
    def get_fn_lock(self) -> bool:
        """Get Fn lock status"""
        try:
            value = self._read_sysfs(self.FN_LOCK)
            return value == "1"
        except SysfsError:
            return False
    
    def set_fn_lock(self, enable: bool) -> None:
        """Set Fn lock"""
        try:
            value = "1" if enable else "0"
            self._write_sysfs(self.FN_LOCK, value)
        except SysfsError as e:
            logger.warning(f"Failed to set Fn lock: {e}")
    
    def get_all_status(self) -> dict:
        """
        Get status of all sysfs attributes
        
        Returns:
            Dictionary with all statuses
        """
        return {
            'conservation_mode': self.get_conservation_mode(),
            'fan_mode': self.get_fan_mode(),
            'camera_power': self.get_camera_power(),
            'usb_charging': self.get_usb_charging(),
            'fn_lock': self.get_fn_lock()
        }


if __name__ == "__main__":
    # Test the sysfs interface
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        sysfs = LegionSysfs()
        print("✅ Sysfs interface initialized")
        
        print("\n📊 Current status:")
        status = sysfs.get_all_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
    except SysfsError as e:
        print(f"❌ Sysfs Error: {e}")
        exit(1)
