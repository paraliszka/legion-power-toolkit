#!/usr/bin/env python3
"""
Legion Power D-Bus Service
Main daemon providing D-Bus interface for Legion Power Manager
"""

import dbus
import dbus.service
import dbus.mainloop.glib
try:
    from gi.repository import GLib
except ImportError:
    import gobject as GLib
import logging
import sys
from pathlib import Path

from legion_acpi import LegionACPI, ACPIError
from legion_sysfs import LegionSysfs, SysfsError
from legion_monitor import LegionMonitor, MonitorError
from legion_config import LegionConfig, ConfigError
from ddc_monitor import DDCController, DDCError

logger = logging.getLogger(__name__)


class LegionPowerService(dbus.service.Object):
    """
    D-Bus service for Legion Power Management
    
    Service name: com.legion.Power
    Object path: /com/legion/Power
    Interface: com.legion.Power.Manager
    """
    
    def __init__(self, bus_name):
        """Initialize the service"""
        super().__init__(bus_name, '/com/legion/Power')
        
        # Initialize components
        try:
            self.acpi = LegionACPI()
            logger.info("ACPI interface initialized")
        except ACPIError as e:
            logger.error(f"ACPI initialization failed: {e}")
            self.acpi = None
        
        try:
            self.sysfs = LegionSysfs()
            logger.info("Sysfs interface initialized")
        except SysfsError as e:
            logger.error(f"Sysfs initialization failed: {e}")
            self.sysfs = None
        
        try:
            self.monitor = LegionMonitor()
            logger.info("Monitor initialized")
        except MonitorError as e:
            logger.error(f"Monitor initialization failed: {e}")
            self.monitor = None
        
        try:
            self.config = LegionConfig()
            logger.info("Config manager initialized")
        except ConfigError as e:
            logger.error(f"Config initialization failed: {e}")
            self.config = None
        
        # Initialize DDC/CI monitor controller
        try:
            self.ddc = DDCController()
            logger.info("DDC monitor controller initialized")
        except DDCError as e:
            logger.warning(f"DDC monitor control not available: {e}")
            self.ddc = None
        except Exception as e:
            logger.warning(f"DDC initialization failed: {e}")
            self.ddc = None
        
        # Restore settings on startup
        if self.config:
            if self.config.get('restore_on_boot', True):
                self._restore_settings()
        
        logger.info("Legion Power Service initialized")
    
    def _restore_settings(self):
        """Restore settings from config"""
        if not self.config:
            return
            
        try:
            # Restore conservation mode
            conservation = self.config.get('conservation_mode_enabled', False)
            if self.sysfs:
                self.sysfs.set_conservation_mode(conservation)
                logger.info(f"Restored conservation mode: {conservation}")
            
            # Restore fan mode
            fan_mode = self.config.get('fan_mode', 'auto')
            if self.sysfs:
                self.sysfs.set_fan_mode(fan_mode)
                logger.info(f"Restored fan mode: {fan_mode}")
            
            # Restore power profile
            power_profile = self.config.get('power_profile', 'balanced')
            if self.acpi:
                try:
                    self.acpi.set_power_profile(power_profile)
                    logger.info(f"Restored power profile: {power_profile}")
                except:
                    logger.warning("Failed to restore power profile via ACPI")
            
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}")
    
    # ========================================
    # Battery Management Methods
    # ========================================
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='b')
    def GetConservationMode(self):
        """Get conservation mode status"""
        try:
            if self.sysfs:
                return self.sysfs.get_conservation_mode()
            elif self.acpi:
                return self.acpi.get_conservation_mode()
            return False
        except Exception as e:
            logger.error(f"GetConservationMode failed: {e}")
            return False
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='b')
    def SetConservationMode(self, enable):
        """Set conservation mode"""
        try:
            # Mutex check: disable rapid charge if enabling conservation
            if enable and self.GetRapidCharge():
                logger.info("Disabling rapid charge (mutex with conservation mode)")
                self.SetRapidCharge(False)
            
            # Set via sysfs (preferred) or ACPI
            if self.sysfs:
                self.sysfs.set_conservation_mode(enable)
            elif self.acpi:
                self.acpi.set_conservation_mode(enable)
            
            # Save to config
            if self.config:
                self.config.set('conservation_mode_enabled', enable)
            
            # Emit signal
            self.ConservationModeChanged(enable)
            logger.info(f"Conservation mode set to: {enable}")
            
        except Exception as e:
            logger.error(f"SetConservationMode failed: {e}")
            raise dbus.exceptions.DBusException(f"Failed to set conservation mode: {e}")
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='b')
    def GetRapidCharge(self):
        """Get rapid charge status"""
        try:
            if self.acpi:
                return self.acpi.get_rapid_charge()
            return False
        except Exception as e:
            logger.error(f"GetRapidCharge failed: {e}")
            return False
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='b')
    def SetRapidCharge(self, enable):
        """Set rapid charge"""
        try:
            # Mutex check: disable conservation if enabling rapid charge
            if enable and self.GetConservationMode():
                logger.info("Disabling conservation mode (mutex with rapid charge)")
                self.SetConservationMode(False)
            
            if self.acpi:
                self.acpi.set_rapid_charge(enable)
            
            # Save to config
            if self.config:
                self.config.set('rapid_charge_enabled', enable)
            
            # Emit signal
            self.RapidChargeChanged(enable)
            logger.info(f"Rapid charge set to: {enable}")
            
        except Exception as e:
            logger.error(f"SetRapidCharge failed: {e}")
            raise dbus.exceptions.DBusException(f"Failed to set rapid charge: {e}")
    
    # ========================================
    # Fan Control Methods
    # ========================================
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='s')
    def GetFanMode(self):
        """Get fan mode"""
        try:
            if self.sysfs:
                return self.sysfs.get_fan_mode()
            return 'auto'
        except Exception as e:
            logger.error(f"GetFanMode failed: {e}")
            return 'auto'
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='s')
    def SetFanMode(self, mode):
        """Set fan mode (and power profile as they are linked)"""
        try:
            # Map fan mode to power profile
            # fan: quiet, auto, performance
            # profile: quiet, balanced, performance
            profile_map = {
                'auto': 'balanced',
                'quiet': 'quiet',
                'performance': 'performance'
            }
            
            # 1. Try sysfs fan control (might not work on all models)
            if self.sysfs:
                try:
                    self.sysfs.set_fan_mode(mode)
                except Exception as e:
                    logger.warning(f"Sysfs fan control failed (ignoring): {e}")
            
            # 2. Set Power Profile via ACPI (Main method for Legion 5)
            # This corresponds to Fn+Q behavior
            if self.acpi:
                profile = profile_map.get(mode, 'balanced')
                self.acpi.set_power_profile(profile)
                logger.info(f"Syncing fan mode '{mode}' to power profile '{profile}'")
            
            # Save to config
            if self.config:
                self.config.set('fan_mode', mode)
                self.config.set('power_profile', profile_map.get(mode, 'balanced'))
            
            # Emit signals
            self.FanModeChanged(mode)
            self.PowerProfileChanged(profile_map.get(mode, 'balanced'))
            
            logger.info(f"Fan mode set to: {mode}")
            
        except Exception as e:
            logger.error(f"SetFanMode failed: {e}")
            raise dbus.exceptions.DBusException(f"Failed to set fan mode: {e}")
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='i')
    def GetFanSpeed(self):
        """Get fan speed in RPM (not implemented yet)"""
        # TODO: Implement fan speed reading via EC
        return 0
    
    # ========================================
    # Power Profile Methods
    # ========================================
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='s')
    def GetPowerProfile(self):
        """Get current power profile"""
        if self.config:
            return self.config.get('power_profile', 'balanced')
        return 'balanced'
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='s')
    def SetPowerProfile(self, profile):
        """Set power profile"""
        try:
            if self.acpi:
                self.acpi.set_power_profile(profile)
            
            # Save to config
            if self.config:
                self.config.set('power_profile', profile)
            
            # Emit signal
            self.PowerProfileChanged(profile)
            logger.info(f"Power profile set to: {profile}")
            
        except Exception as e:
            logger.error(f"SetPowerProfile failed: {e}")
            raise dbus.exceptions.DBusException(f"Failed to set power profile: {e}")
    
    # ========================================
    # Monitoring Methods
    # ========================================
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='a{sv}')
    def GetBatteryStatus(self):
        """Get battery status"""
        try:
            if self.monitor:
                status = self.monitor.get_battery_status()
                # Convert to D-Bus types
                return dbus.Dictionary({
                    'capacity': dbus.Int32(status.get('capacity', 0)),
                    'state': dbus.String(status.get('state', 'Unknown')),
                    'voltage': dbus.Double(status.get('voltage', 0.0)),
                    'power_now': dbus.Double(status.get('power_now', 0.0)),
                    'health': dbus.Double(status.get('health', 100.0)),
                    'cycle_count': dbus.Int32(status.get('cycle_count', 0)),
                    'time_remaining_minutes': dbus.Int32(
                        status.get('time_remaining_minutes', 0)
                    ),
                }, signature='sv')
            return dbus.Dictionary({}, signature='sv')
        except Exception as e:
            logger.error(f"GetBatteryStatus failed: {e}")
            return dbus.Dictionary({}, signature='sv')
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='a{sd}')
    def GetTemperatures(self):
        """Get system temperatures"""
        try:
            if self.monitor:
                temps = self.monitor.get_temperatures()
                return dbus.Dictionary(
                    {k: dbus.Double(v) for k, v in temps.items()},
                    signature='sd'
                )
            return dbus.Dictionary({}, signature='sd')
        except Exception as e:
            logger.error(f"GetTemperatures failed: {e}")
            return dbus.Dictionary({}, signature='sd')
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='b')
    def GetACAdapterOnline(self):
        """Check if AC adapter is connected"""
        try:
            if self.monitor:
                return self.monitor.get_ac_adapter_online()
            return False
        except Exception as e:
            logger.error(f"GetACAdapterOnline failed: {e}")
            return False
    
    # ========================================
    # Settings Methods
    # ========================================
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='a{sv}')
    def GetSettings(self):
        """Get all settings"""
        try:
            if self.config:
                settings = self.config.get_all()
                # Convert to D-Bus types
                return dbus.Dictionary(
                    {k: v for k, v in settings.items()},
                    signature='sv'
                )
            return dbus.Dictionary({}, signature='sv')
        except Exception as e:
            logger.error(f"GetSettings failed: {e}")
            return dbus.Dictionary({}, signature='sv')
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='sv')
    def SetSetting(self, key, value):
        """Set a setting"""
        try:
            if self.config:
                self.config.set(key, value)
            logger.info(f"Setting updated: {key} = {value}")
        except Exception as e:
            logger.error(f"SetSetting failed: {e}")
            raise dbus.exceptions.DBusException(f"Failed to set setting: {e}")
    
    # ========================================
    # External Monitor Methods (DDC/CI)
    # ========================================
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='aa{sv}')
    def GetExternalMonitors(self):
        """Get list of external DDC/CI monitors"""
        try:
            if not self.ddc:
                logger.debug("DDC controller not available")
                return dbus.Array([], signature='a{sv}')
            
            monitors = self.ddc.detect_monitors(use_cache=True)
            
            # Convert to D-Bus format
            result = []
            for mon in monitors:
                monitor_dict = dbus.Dictionary({
                    'id': dbus.Int32(mon.id),
                    'bus': dbus.String(mon.bus),
                    'manufacturer': dbus.String(mon.manufacturer),
                    'model': dbus.String(mon.model),
                    'serial': dbus.String(mon.serial),
                    'name': dbus.String(mon.name),
                    'vcp_version': dbus.String(mon.vcp_version),
                    'supports_brightness': dbus.Boolean(mon.supports_brightness)
                }, signature='sv')
                result.append(monitor_dict)
            
            logger.debug(f"Returning {len(result)} external monitor(s)")
            return dbus.Array(result, signature='a{sv}')
        
        except Exception as e:
            logger.error(f"GetExternalMonitors failed: {e}")
            return dbus.Array([], signature='a{sv}')
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='i', out_signature='i')
    def GetMonitorBrightness(self, display_id):
        """Get external monitor brightness (0-100)"""
        try:
            if not self.ddc:
                logger.debug("DDC controller not available")
                return dbus.Int32(0)
            
            brightness = self.ddc.get_brightness(display_id)
            logger.debug(f"Display {display_id} brightness: {brightness}")
            return dbus.Int32(brightness)
        
        except Exception as e:
            logger.error(f"GetMonitorBrightness failed for display {display_id}: {e}")
            return dbus.Int32(0)
    
    @dbus.service.method('com.legion.Power.Manager',
                         in_signature='ii')
    def SetMonitorBrightness(self, display_id, brightness):
        """Set external monitor brightness (0-100)"""
        try:
            if not self.ddc:
                logger.warning("DDC controller not available")
                raise dbus.exceptions.DBusException("DDC controller not available")
            
            success = self.ddc.set_brightness(display_id, brightness)
            
            if success:
                # Emit signal
                self.MonitorBrightnessChanged(display_id, brightness)
                logger.info(f"Display {display_id} brightness set to {brightness}")
            else:
                raise dbus.exceptions.DBusException(
                    f"Failed to set brightness for display {display_id}"
                )
        
        except dbus.exceptions.DBusException:
            raise
        except Exception as e:
            logger.error(f"SetMonitorBrightness failed: {e}")
            raise dbus.exceptions.DBusException(f"Failed to set monitor brightness: {e}")
    
    @dbus.service.method('com.legion.Power.Manager')
    def RefreshExternalMonitors(self):
        """Force refresh of external monitor list (invalidate cache)"""
        try:
            if self.ddc:
                self.ddc.invalidate_cache()
                logger.info("External monitor cache invalidated")
        except Exception as e:
            logger.error(f"RefreshExternalMonitors failed: {e}")
    
    @dbus.service.method('com.legion.Power.Manager',
                         out_signature='b')
    def IsDDCAvailable(self):
        """Check if DDC/CI support is available"""
        return self.ddc is not None
    
    # ========================================
    # Signals
    # ========================================
    
    @dbus.service.signal('com.legion.Power.Manager',
                         signature='b')
    def ConservationModeChanged(self, enabled):
        """Signal emitted when conservation mode changes"""
        pass
    
    @dbus.service.signal('com.legion.Power.Manager',
                         signature='b')
    def RapidChargeChanged(self, enabled):
        """Signal emitted when rapid charge changes"""
        pass
    
    @dbus.service.signal('com.legion.Power.Manager',
                         signature='s')
    def FanModeChanged(self, mode):
        """Signal emitted when fan mode changes"""
        pass
    
    @dbus.service.signal('com.legion.Power.Manager',
                         signature='s')
    def PowerProfileChanged(self, profile):
        """Signal emitted when power profile changes"""
        pass
    
    @dbus.service.signal('com.legion.Power.Manager',
                         signature='a{sv}')
    def BatteryStatusChanged(self, status):
        """Signal emitted when battery status changes"""
        pass
    
    @dbus.service.signal('com.legion.Power.Manager',
                         signature='ii')
    def MonitorBrightnessChanged(self, display_id, brightness):
        """Signal emitted when external monitor brightness changes"""
        pass


def setup_logging():
    """Setup logging configuration"""
    log_dir = Path.home() / ".local" / "share" / "legion-power"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "service.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point"""
    setup_logging()
    logger.info("Starting Legion Power Service")
    
    # Setup D-Bus main loop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    # Get system bus
    bus = dbus.SystemBus()
    
    # Request bus name
    try:
        bus_name = dbus.service.BusName('com.legion.Power', bus)
    except dbus.exceptions.NameExistsException:
        logger.error("Service already running")
        sys.exit(1)
    
    # Create service
    service = LegionPowerService(bus_name)
    
    # Run main loop
    logger.info("Service ready, entering main loop")
    mainloop = GLib.MainLoop()
    
    try:
        mainloop.run()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Service crashed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
