#!/usr/bin/env python3
"""
Quick test script for Legion Power backend
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from legion_acpi import LegionACPI, ACPIError
        print("  ✓ legion_acpi")
    except ImportError as e:
        print(f"  ✗ legion_acpi: {e}")
        return False
    
    try:
        from legion_sysfs import LegionSysfs, SysfsError
        print("  ✓ legion_sysfs")
    except ImportError as e:
        print(f"  ✗ legion_sysfs: {e}")
        return False
    
    try:
        from legion_monitor import LegionMonitor, MonitorError
        print("  ✓ legion_monitor")
    except ImportError as e:
        print(f"  ✗ legion_monitor: {e}")
        return False
    
    try:
        from legion_config import LegionConfig, ConfigError
        print("  ✓ legion_config")
    except ImportError as e:
        print(f"  ✗ legion_config: {e}")
        return False
    
    return True

def test_acpi():
    """Test ACPI interface"""
    print("\nTesting ACPI interface...")
    try:
        from legion_acpi import LegionACPI, ACPIError
        acpi = LegionACPI()
        print("  ✓ ACPI initialized")
        
        # Test read operations
        conservation = acpi.get_conservation_mode()
        print(f"  Conservation mode: {conservation}")
        
        rapid = acpi.get_rapid_charge()
        print(f"  Rapid charge: {rapid}")
        
        return True
    except Exception as e:
        print(f"  ✗ ACPI test failed: {e}")
        return False

def test_sysfs():
    """Test sysfs interface"""
    print("\nTesting Sysfs interface...")
    try:
        from legion_sysfs import LegionSysfs, SysfsError
        sysfs = LegionSysfs()
        print("  ✓ Sysfs initialized")
        
        status = sysfs.get_all_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        return True
    except Exception as e:
        print(f"  ✗ Sysfs test failed: {e}")
        return False

def test_monitor():
    """Test monitor"""
    print("\nTesting Monitor...")
    try:
        from legion_monitor import LegionMonitor, MonitorError
        monitor = LegionMonitor()
        print("  ✓ Monitor initialized")
        
        battery = monitor.get_battery_status()
        print(f"  Battery: {battery['capacity']}% - {battery['state']}")
        
        temps = monitor.get_temperatures()
        if temps:
            for sensor, temp in temps.items():
                print(f"  {sensor}: {temp:.1f}°C")
        
        return True
    except Exception as e:
        print(f"  ✗ Monitor test failed: {e}")
        return False

def test_config():
    """Test config manager"""
    print("\nTesting Config manager...")
    try:
        from legion_config import LegionConfig, ConfigError
        config = LegionConfig()
        print("  ✓ Config initialized")
        print(f"  Config file: {config.CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Legion Power Backend Test Suite")
    print("=" * 50)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("ACPI", test_acpi()))
    results.append(("Sysfs", test_sysfs()))
    results.append(("Monitor", test_monitor()))
    results.append(("Config", test_config()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
