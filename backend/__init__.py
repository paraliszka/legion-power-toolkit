"""
Legion Power Manager Backend
Python backend for Lenovo Legion 5 power management
"""

from .legion_acpi import LegionACPI, ACPIError
from .legion_sysfs import LegionSysfs, SysfsError
from .legion_monitor import LegionMonitor, MonitorError
from .legion_config import LegionConfig, ConfigError

__all__ = [
    'LegionACPI',
    'LegionSysfs',
    'LegionMonitor',
    'LegionConfig',
    'ACPIError',
    'SysfsError',
    'MonitorError',
    'ConfigError',
]

__version__ = '1.0.0'
