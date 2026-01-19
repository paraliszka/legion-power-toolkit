#!/usr/bin/env python3
"""
Legion ACPI Interface
Handles ACPI calls for Lenovo Legion 5 15ARH05
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

ACPI_CALL_PATH = "/proc/acpi/call"


class ACPIError(Exception):
    """Raised when ACPI call fails"""
    pass


class LegionACPI:
    """
    ACPI interface for Lenovo Legion 5
    
    Based on Arch Wiki and LenovoLegionLinux project research:
    - Conservation Mode: \_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x03/0x05
    - Rapid Charge: \_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x07/0x08
    - Power Profile: \_SB.PCI0.LPC0.EC0.VPC0.DYTC (DYTC modes)
    """
    
    # ACPI method paths
    SBMC_METHOD = r"\_SB.PCI0.LPC0.EC0.VPC0.SBMC"
    BTSG_METHOD = r"\_SB.PCI0.LPC0.EC0.BTSG"
    FCGM_METHOD = r"\_SB.PCI0.LPC0.EC0.FCGM"
    DYTC_METHOD = r"\_SB.PCI0.LPC0.EC0.VPC0.DYTC"
    
    # SBMC parameters
    CONSERVATION_ON = "0x03"
    CONSERVATION_OFF = "0x05"
    RAPID_CHARGE_ON = "0x07"
    RAPID_CHARGE_OFF = "0x08"
    
    # DYTC parameters (Dynamic Thermal Control)
    DYTC_QUIET = "0x0013B001"          # Battery Saving
    DYTC_BALANCED = "0x000FB001"       # Intelligent Cooling
    DYTC_PERFORMANCE = "0x0012B001"    # Extreme Performance
    
    def __init__(self):
        """Initialize ACPI interface"""
        self._check_acpi_call_available()
    
    def _check_acpi_call_available(self):
        """Check if acpi_call module is loaded"""
        if not os.path.exists(ACPI_CALL_PATH):
            raise ACPIError(
                f"acpi_call module not loaded. "
                f"Run: sudo modprobe acpi_call"
            )
        
        if not os.access(ACPI_CALL_PATH, os.W_OK):
            raise ACPIError(
                f"No write permission to {ACPI_CALL_PATH}. "
                f"Check udev rules or run with appropriate permissions."
            )
    
    def _execute_acpi_call(self, method: str, parameter: Optional[str] = None) -> str:
        """
        Execute an ACPI call and return the result
        
        Args:
            method: ACPI method path (e.g., "\\_SB.PCI0.LPC0.EC0.BTSG")
            parameter: Optional parameter (e.g., "0x03")
        
        Returns:
            Result from ACPI call (e.g., "0x0", "0x1")
        
        Raises:
            ACPIError: If ACPI call fails
        """
        try:
            # Construct the call string
            if parameter:
                call_str = f"{method} {parameter}"
            else:
                call_str = method
            
            logger.debug(f"ACPI call: {call_str}")
            
            # Write to acpi_call
            with open(ACPI_CALL_PATH, 'w') as f:
                f.write(call_str)
            
            # Read result
            with open(ACPI_CALL_PATH, 'r') as f:
                result = f.read().strip().rstrip('\x00')
            
            logger.debug(f"ACPI result: {result}")
            return result
            
        except PermissionError as e:
            raise ACPIError(f"Permission denied: {e}")
        except Exception as e:
            raise ACPIError(f"ACPI call failed: {e}")
    
    def get_conservation_mode(self) -> bool:
        """
        Get conservation mode status
        
        Returns:
            True if conservation mode is enabled, False otherwise
        """
        try:
            result = self._execute_acpi_call(self.BTSG_METHOD)
            # Result is "0x0" (off) or "0x1" (on)
            return result == "0x1"
        except ACPIError as e:
            logger.error(f"Failed to get conservation mode: {e}")
            raise
    
    def set_conservation_mode(self, enable: bool) -> None:
        """
        Set conservation mode (60% charge limit)
        
        Args:
            enable: True to enable, False to disable
        """
        try:
            param = self.CONSERVATION_ON if enable else self.CONSERVATION_OFF
            self._execute_acpi_call(self.SBMC_METHOD, param)
            logger.info(f"Conservation mode {'enabled' if enable else 'disabled'}")
        except ACPIError as e:
            logger.error(f"Failed to set conservation mode: {e}")
            raise
    
    def get_rapid_charge(self) -> bool:
        """
        Get rapid charge status
        
        Returns:
            True if rapid charge is enabled, False otherwise
        """
        try:
            result = self._execute_acpi_call(self.FCGM_METHOD)
            # Result is "0x0" (off) or "0x1" (on)
            return result == "0x1"
        except ACPIError as e:
            logger.error(f"Failed to get rapid charge: {e}")
            raise
    
    def set_rapid_charge(self, enable: bool) -> None:
        """
        Set rapid charge mode
        
        Args:
            enable: True to enable, False to disable
        """
        try:
            param = self.RAPID_CHARGE_ON if enable else self.RAPID_CHARGE_OFF
            self._execute_acpi_call(self.SBMC_METHOD, param)
            logger.info(f"Rapid charge {'enabled' if enable else 'disabled'}")
        except ACPIError as e:
            logger.error(f"Failed to set rapid charge: {e}")
            raise
    
    def set_power_profile(self, profile: str) -> None:
        """
        Set power profile via DYTC (Dynamic Thermal Control)
        
        Args:
            profile: One of "quiet", "balanced", "performance"
        
        Raises:
            ValueError: If profile is invalid
            ACPIError: If ACPI call fails
        """
        profile_map = {
            "quiet": self.DYTC_QUIET,
            "balanced": self.DYTC_BALANCED,
            "performance": self.DYTC_PERFORMANCE,
        }
        
        if profile not in profile_map:
            raise ValueError(
                f"Invalid profile: {profile}. "
                f"Must be one of: {', '.join(profile_map.keys())}"
            )
        
        try:
            param = profile_map[profile]
            self._execute_acpi_call(self.DYTC_METHOD, param)
            logger.info(f"Power profile set to: {profile}")
        except ACPIError as e:
            logger.error(f"Failed to set power profile: {e}")
            raise
    
    def test_acpi_methods(self) -> dict:
        """
        Test all ACPI methods (read-only operations)
        
        Returns:
            Dictionary with test results
        """
        results = {}
        
        # Test conservation mode read
        try:
            conservation = self.get_conservation_mode()
            results['conservation_mode'] = {
                'status': 'OK',
                'value': conservation
            }
        except Exception as e:
            results['conservation_mode'] = {
                'status': 'FAILED',
                'error': str(e)
            }
        
        # Test rapid charge read
        try:
            rapid = self.get_rapid_charge()
            results['rapid_charge'] = {
                'status': 'OK',
                'value': rapid
            }
        except Exception as e:
            results['rapid_charge'] = {
                'status': 'FAILED',
                'error': str(e)
            }
        
        return results


if __name__ == "__main__":
    # Test the ACPI interface
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        acpi = LegionACPI()
        print("✅ ACPI interface initialized")
        
        print("\n🧪 Testing ACPI methods...")
        results = acpi.test_acpi_methods()
        
        for method, result in results.items():
            status_icon = "✅" if result['status'] == 'OK' else "❌"
            print(f"{status_icon} {method}: {result}")
        
    except ACPIError as e:
        print(f"❌ ACPI Error: {e}")
        exit(1)
