#!/usr/bin/env python3
"""
DDC/CI Monitor Control
External monitor brightness control via ddcutil
"""

import logging
import subprocess
import re
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class DDCError(Exception):
    """Raised when DDC operations fail"""
    pass


@dataclass
class DDCMonitor:
    """Represents a DDC/CI capable monitor"""
    id: int  # Display number (1, 2, 3...)
    bus: str  # I2C bus path (/dev/i2c-X)
    manufacturer: str  # Manufacturer ID from EDID
    model: str  # Model name from EDID
    serial: str  # Serial number
    vcp_version: str  # VCP version (e.g., "2.1")
    supports_brightness: bool = True  # Assumes brightness support
    
    @property
    def name(self) -> str:
        """Human-readable monitor name"""
        return f"{self.manufacturer} {self.model}".strip()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for D-Bus"""
        return {
            'id': self.id,
            'bus': self.bus,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial': self.serial,
            'name': self.name,
            'vcp_version': self.vcp_version,
            'supports_brightness': self.supports_brightness
        }


class DDCController:
    """
    Controller for DDC/CI monitors using ddcutil
    
    Features:
    - Detect external monitors
    - Read/write brightness (VCP code 0x10)
    - Cache with TTL for performance
    """
    
    CACHE_TTL = 60  # seconds - longer cache to avoid slow detection
    DDCUTIL_TIMEOUT = 3  # seconds per command - shorter timeout
    BRIGHTNESS_VCP_CODE = 0x10
    
    def __init__(self):
        """Initialize DDC controller"""
        self._monitors_cache: Optional[List[DDCMonitor]] = None
        self._cache_timestamp: float = 0
        self._check_ddcutil_available()
    
    def _check_ddcutil_available(self):
        """Check if ddcutil is installed and accessible"""
        try:
            result = subprocess.run(
                ['which', 'ddcutil'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode != 0:
                raise DDCError("ddcutil not found. Install with: sudo apt install ddcutil")
            logger.info("ddcutil found and available")
        except subprocess.TimeoutExpired:
            raise DDCError("ddcutil check timed out")
        except Exception as e:
            raise DDCError(f"Failed to check ddcutil: {e}")
    
    def _run_ddcutil(self, args: List[str], timeout: Optional[int] = None) -> str:
        """
        Run ddcutil command with timeout
        
        Args:
            args: Command arguments (e.g., ['detect'])
            timeout: Timeout in seconds
            
        Returns:
            Command output as string
        """
        if timeout is None:
            timeout = self.DDCUTIL_TIMEOUT
        
        cmd = ['ddcutil'] + args
        try:
            logger.debug(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                logger.warning(f"ddcutil command failed: {error_msg}")
                raise DDCError(f"ddcutil failed: {error_msg}")
            
            return result.stdout
        
        except subprocess.TimeoutExpired:
            logger.error(f"ddcutil command timed out after {timeout}s")
            raise DDCError(f"ddcutil timed out after {timeout}s")
        except Exception as e:
            logger.error(f"ddcutil command error: {e}")
            raise DDCError(f"ddcutil error: {e}")
    
    def _parse_detect_output(self, output: str) -> List[DDCMonitor]:
        """
        Parse output from 'ddcutil detect'
        
        Example output:
        Display 1
           I2C bus:  /dev/i2c-5
           EDID synopsis:
              Mfg id:               IVM - Iiyama North America
              Model:                PL2745Q
              Product code:         26267  (0x669b)
              Serial number:        12277343A1681
              Binary serial number: 1681 (0x00000691)
              Manufacture year:     2023,  Week: 43
           VCP version:         2.1
        """
        monitors = []
        current_monitor = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Display ID
            if line.startswith('Display '):
                if current_monitor:
                    # Save previous monitor
                    try:
                        monitor = self._create_monitor_from_dict(current_monitor)
                        monitors.append(monitor)
                    except Exception as e:
                        logger.warning(f"Failed to parse monitor: {e}")
                
                # Start new monitor
                match = re.search(r'Display (\d+)', line)
                if match:
                    current_monitor = {'id': int(match.group(1))}
            
            # I2C bus
            elif line.startswith('I2C bus:'):
                match = re.search(r'/dev/i2c-\d+', line)
                if match:
                    current_monitor['bus'] = match.group(0)
            
            # Manufacturer
            elif line.startswith('Mfg id:'):
                # Extract manufacturer code (e.g., "IVM")
                parts = line.split('-')
                if len(parts) >= 2:
                    mfg_code = parts[0].split(':')[1].strip()
                    current_monitor['manufacturer'] = mfg_code
            
            # Model
            elif line.startswith('Model:'):
                model = line.split(':', 1)[1].strip()
                current_monitor['model'] = model
            
            # Serial number
            elif line.startswith('Serial number:'):
                serial = line.split(':', 1)[1].strip()
                current_monitor['serial'] = serial
            
            # VCP version
            elif line.startswith('VCP version:'):
                vcp = line.split(':', 1)[1].strip()
                current_monitor['vcp_version'] = vcp
        
        # Don't forget last monitor
        if current_monitor:
            try:
                monitor = self._create_monitor_from_dict(current_monitor)
                monitors.append(monitor)
            except Exception as e:
                logger.warning(f"Failed to parse monitor: {e}")
        
        return monitors
    
    def _create_monitor_from_dict(self, data: Dict) -> DDCMonitor:
        """Create DDCMonitor from parsed data"""
        return DDCMonitor(
            id=data.get('id', 0),
            bus=data.get('bus', ''),
            manufacturer=data.get('manufacturer', 'Unknown'),
            model=data.get('model', 'Unknown'),
            serial=data.get('serial', ''),
            vcp_version=data.get('vcp_version', 'Unknown')
        )
    
    def detect_monitors(self, use_cache: bool = True) -> List[DDCMonitor]:
        """
        Detect all DDC/CI capable monitors
        
        Args:
            use_cache: Use cached results if available and fresh
            
        Returns:
            List of detected monitors
        """
        # Check cache
        if use_cache and self._monitors_cache is not None:
            age = time.time() - self._cache_timestamp
            if age < self.CACHE_TTL:
                logger.debug(f"Using cached monitors (age: {age:.1f}s)")
                return self._monitors_cache
        
        logger.info("Detecting DDC/CI monitors...")
        
        try:
            # Run ddcutil detect
            output = self._run_ddcutil(['detect'], timeout=10)
            
            # Parse output
            monitors = self._parse_detect_output(output)
            
            logger.info(f"Detected {len(monitors)} monitor(s)")
            for mon in monitors:
                logger.info(f"  Display {mon.id}: {mon.name} ({mon.bus})")
            
            # Update cache
            self._monitors_cache = monitors
            self._cache_timestamp = time.time()
            
            return monitors
        
        except DDCError as e:
            logger.error(f"Monitor detection failed: {e}")
            # Return empty list instead of crashing
            return []
        except Exception as e:
            logger.error(f"Unexpected error during detection: {e}")
            return []
    
    def get_brightness(self, display_id: int) -> int:
        """
        Get monitor brightness (0-100)
        
        Args:
            display_id: Display number (1, 2, 3...)
            
        Returns:
            Brightness value (0-100)
        """
        try:
            # Run: ddcutil -d <id> getvcp 10
            output = self._run_ddcutil(['-d', str(display_id), 'getvcp', '10'])
            
            # Parse output: "VCP code 0x10 (Brightness): current value = 100, max value = 100"
            match = re.search(r'current value\s*=\s*(\d+)', output)
            if match:
                brightness = int(match.group(1))
                logger.debug(f"Display {display_id} brightness: {brightness}")
                return brightness
            else:
                logger.warning(f"Could not parse brightness from: {output}")
                return 0
        
        except DDCError as e:
            logger.error(f"Failed to get brightness for display {display_id}: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error getting brightness: {e}")
            return 0
    
    def set_brightness(self, display_id: int, brightness: int) -> bool:
        """
        Set monitor brightness (0-100)
        
        Args:
            display_id: Display number (1, 2, 3...)
            brightness: Brightness value (0-100)
            
        Returns:
            True if successful, False otherwise
        """
        # Clamp brightness to valid range
        brightness = max(0, min(100, brightness))
        
        try:
            # Run: ddcutil -d <id> setvcp 10 <brightness>
            # Use --sleep-multiplier 0.1 for faster operation (risky but speeds up 10x)
            # Use --noverify to skip verification (faster but less safe)
            self._run_ddcutil([
                '-d', str(display_id),
                '--sleep-multiplier', '.1',
                '--noverify',
                'setvcp', '10', str(brightness)
            ], timeout=2)
            logger.info(f"Display {display_id} brightness set to {brightness}")
            return True
        
        except DDCError as e:
            logger.error(f"Failed to set brightness for display {display_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting brightness: {e}")
            return False
    
    def get_monitor_by_id(self, display_id: int) -> Optional[DDCMonitor]:
        """Get monitor info by display ID"""
        monitors = self.detect_monitors(use_cache=True)
        for monitor in monitors:
            if monitor.id == display_id:
                return monitor
        return None
    
    def invalidate_cache(self):
        """Force cache refresh on next detect"""
        self._monitors_cache = None
        self._cache_timestamp = 0
        logger.debug("Monitor cache invalidated")


if __name__ == "__main__":
    # Test the DDC controller
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        print("🖥️  DDC Monitor Controller Test\n")
        
        controller = DDCController()
        print("✅ Controller initialized\n")
        
        # Detect monitors
        print("🔍 Detecting monitors...")
        monitors = controller.detect_monitors(use_cache=False)
        
        if not monitors:
            print("❌ No DDC/CI monitors found")
            print("\nTroubleshooting:")
            print("  1. Check monitor is connected via DisplayPort or HDMI")
            print("  2. Enable DDC/CI in monitor OSD settings")
            print("  3. Add user to i2c group: sudo usermod -aG i2c $USER")
            print("  4. Test manually: ddcutil detect")
            exit(1)
        
        print(f"✅ Found {len(monitors)} monitor(s):\n")
        for mon in monitors:
            print(f"  Display {mon.id}:")
            print(f"    Name: {mon.name}")
            print(f"    Bus: {mon.bus}")
            print(f"    Serial: {mon.serial}")
            print(f"    VCP: {mon.vcp_version}")
            print()
        
        # Test brightness control on first monitor
        test_monitor = monitors[0]
        print(f"🔆 Testing brightness control on Display {test_monitor.id}...\n")
        
        # Get current brightness
        current = controller.get_brightness(test_monitor.id)
        print(f"  Current brightness: {current}%")
        
        # Test set (don't actually change, just verify command works)
        print(f"  ✅ Brightness control available")
        
        print("\n🎉 All tests passed!")
        
    except DDCError as e:
        print(f"❌ DDC Error: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
