#!/usr/bin/env python3
"""
Legion Monitoring
Battery, temperature, and fan monitoring for Lenovo Legion 5
"""

import logging
from typing import Dict, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class MonitorError(Exception):
    """Raised when monitoring fails"""
    pass


class LegionMonitor:
    """
    Monitor battery, temperatures, and fan speed
    
    Uses:
    - /sys/class/power_supply/BAT0/ for battery
    - /sys/class/hwmon/ for temperatures
    - ACPI for fan speed (if available)
    """
    
    BATTERY_PATH = Path("/sys/class/power_supply/BAT0")
    HWMON_BASE = Path("/sys/class/hwmon")
    
    def __init__(self):
        """Initialize monitor"""
        self._check_battery_available()
    
    def _check_battery_available(self):
        """Check if battery is available"""
        if not self.BATTERY_PATH.exists():
            raise MonitorError(f"Battery not found at {self.BATTERY_PATH}")
    
    def _read_sysfs_value(self, path: Path) -> str:
        """Read value from sysfs file"""
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.debug(f"Failed to read {path}: {e}")
            return ""
    
    def get_battery_status(self) -> Dict:
        """
        Get comprehensive battery status
        
        Returns:
            Dictionary with battery information
        """
        status = {}
        
        # Capacity (percentage)
        try:
            capacity = self._read_sysfs_value(self.BATTERY_PATH / "capacity")
            status['capacity'] = int(capacity) if capacity else 0
        except:
            status['capacity'] = 0
        
        # State (Charging/Discharging/Full/etc)
        status['state'] = self._read_sysfs_value(self.BATTERY_PATH / "status")
        
        # Voltage
        try:
            voltage_now = self._read_sysfs_value(self.BATTERY_PATH / "voltage_now")
            if voltage_now:
                # Convert from µV to V
                status['voltage'] = float(voltage_now) / 1000000
            else:
                status['voltage'] = 0.0
        except:
            status['voltage'] = 0.0
        
        # Power consumption
        try:
            power_now = self._read_sysfs_value(self.BATTERY_PATH / "power_now")
            if power_now:
                # Convert from µW to W
                status['power_now'] = float(power_now) / 1000000
            else:
                status['power_now'] = 0.0
        except:
            status['power_now'] = 0.0
        
        # Energy
        try:
            energy_now = self._read_sysfs_value(self.BATTERY_PATH / "energy_now")
            energy_full = self._read_sysfs_value(self.BATTERY_PATH / "energy_full")
            energy_full_design = self._read_sysfs_value(
                self.BATTERY_PATH / "energy_full_design"
            )
            
            if energy_now:
                status['energy_now'] = float(energy_now) / 1000000  # Wh
            if energy_full:
                status['energy_full'] = float(energy_full) / 1000000  # Wh
            if energy_full_design:
                status['energy_full_design'] = float(energy_full_design) / 1000000  # Wh
            
            # Calculate health
            if energy_full and energy_full_design:
                health = (float(energy_full) / float(energy_full_design)) * 100
                status['health'] = min(100, max(0, health))
            else:
                status['health'] = 100
        except:
            status['health'] = 100
        
        # Cycle count
        try:
            cycle_count = self._read_sysfs_value(self.BATTERY_PATH / "cycle_count")
            status['cycle_count'] = int(cycle_count) if cycle_count else 0
        except:
            status['cycle_count'] = 0
        
        # Manufacturer & model
        status['manufacturer'] = self._read_sysfs_value(
            self.BATTERY_PATH / "manufacturer"
        )
        status['model_name'] = self._read_sysfs_value(
            self.BATTERY_PATH / "model_name"
        )
        status['technology'] = self._read_sysfs_value(
            self.BATTERY_PATH / "technology"
        )
        
        # Time remaining calculation
        if status['state'] == "Discharging" and status['power_now'] > 0:
            try:
                hours = status['energy_now'] / status['power_now']
                status['time_remaining_hours'] = hours
                status['time_remaining_minutes'] = int(hours * 60)
            except:
                status['time_remaining_hours'] = 0
                status['time_remaining_minutes'] = 0
        elif status['state'] == "Charging" and status['power_now'] > 0:
            try:
                remaining_energy = status['energy_full'] - status['energy_now']
                hours = remaining_energy / status['power_now']
                status['time_to_full_hours'] = hours
                status['time_to_full_minutes'] = int(hours * 60)
            except:
                status['time_to_full_hours'] = 0
                status['time_to_full_minutes'] = 0
        
        return status
    
    def get_temperatures(self) -> Dict[str, float]:
        """
        Get system temperatures
        
        Returns:
            Dictionary with temperatures in Celsius
        """
        temps = {}
        
        if not self.HWMON_BASE.exists():
            return temps
        
        # Scan all hwmon devices
        for hwmon_dir in self.HWMON_BASE.iterdir():
            if not hwmon_dir.is_dir():
                continue
            
            # Read device name
            name_file = hwmon_dir / "name"
            if name_file.exists():
                device_name = self._read_sysfs_value(name_file)
            else:
                device_name = hwmon_dir.name
            
            # Find temperature inputs
            for temp_input in hwmon_dir.glob("temp*_input"):
                try:
                    # Read temperature (in millidegrees)
                    temp_value = self._read_sysfs_value(temp_input)
                    if temp_value:
                        temp_celsius = float(temp_value) / 1000
                        
                        # Try to get label
                        temp_label_file = temp_input.parent / temp_input.name.replace(
                            "_input", "_label"
                        )
                        if temp_label_file.exists():
                            label = self._read_sysfs_value(temp_label_file)
                        else:
                            # Extract number from temp1_input -> temp1
                            match = re.search(r'temp(\d+)', temp_input.name)
                            if match:
                                label = f"{device_name}_temp{match.group(1)}"
                            else:
                                label = device_name
                        
                        temps[label] = temp_celsius
                except Exception as e:
                    logger.debug(f"Failed to read {temp_input}: {e}")
        
        # Try to identify CPU/GPU temps
        result = {}
        for key, value in temps.items():
            key_lower = key.lower()
            if 'k10temp' in key_lower or 'cpu' in key_lower or 'tctl' in key_lower:
                result['cpu'] = value
            elif 'gpu' in key_lower or 'radeon' in key_lower or 'amdgpu' in key_lower:
                result['gpu'] = value
            else:
                result[key] = value
        
        return result
    
    def get_ac_adapter_online(self) -> bool:
        """
        Check if AC adapter is connected
        
        Returns:
            True if AC is connected, False otherwise
        """
        ac_path = Path("/sys/class/power_supply/ADP0/online")
        if not ac_path.exists():
            # Fallback: check battery state
            status = self.get_battery_status()
            return status['state'] in ["Charging", "Full"]
        
        try:
            online = self._read_sysfs_value(ac_path)
            return online == "1"
        except:
            return False
    
    def format_time_remaining(self, minutes: int) -> str:
        """
        Format time remaining in human-readable format
        
        Args:
            minutes: Time in minutes
        
        Returns:
            Formatted string (e.g., "2h 15m")
        """
        if minutes <= 0:
            return "calculating..."
        
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"


if __name__ == "__main__":
    # Test the monitor
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        monitor = LegionMonitor()
        print("✅ Monitor initialized\n")
        
        print("🔋 Battery Status:")
        battery = monitor.get_battery_status()
        print(f"  Capacity: {battery['capacity']}%")
        print(f"  State: {battery['state']}")
        print(f"  Voltage: {battery['voltage']:.2f}V")
        print(f"  Power: {battery['power_now']:.2f}W")
        print(f"  Health: {battery.get('health', 100):.1f}%")
        print(f"  Cycles: {battery['cycle_count']}")
        
        if 'time_remaining_minutes' in battery:
            time_str = monitor.format_time_remaining(battery['time_remaining_minutes'])
            print(f"  Time remaining: {time_str}")
        
        print(f"\n🌡️  Temperatures:")
        temps = monitor.get_temperatures()
        for sensor, temp in temps.items():
            print(f"  {sensor}: {temp:.1f}°C")
        
        print(f"\n🔌 AC Adapter: {'Connected' if monitor.get_ac_adapter_online() else 'Disconnected'}")
        
    except MonitorError as e:
        print(f"❌ Monitor Error: {e}")
        exit(1)
