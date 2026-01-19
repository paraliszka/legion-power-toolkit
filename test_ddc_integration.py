#!/usr/bin/env python3
"""
Test DDC/CI Integration with D-Bus
This test simulates what the applet will do
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import dbus
from ddc_monitor import DDCController

def test_ddc_direct():
    """Test DDC controller directly"""
    print("=" * 60)
    print("TEST 1: Direct DDC Controller")
    print("=" * 60)
    print()
    
    try:
        controller = DDCController()
        print("✅ DDC Controller initialized")
        print()
        
        # Detect monitors
        print("🔍 Detecting monitors...")
        monitors = controller.detect_monitors(use_cache=False)
        
        if not monitors:
            print("❌ No DDC/CI monitors found")
            return False
        
        print(f"✅ Found {len(monitors)} monitor(s):")
        print()
        
        for mon in monitors:
            print(f"  📺 Display {mon.id}: {mon.name}")
            print(f"     Bus: {mon.bus}")
            print(f"     Manufacturer: {mon.manufacturer}")
            print(f"     Model: {mon.model}")
            print(f"     Serial: {mon.serial}")
            print(f"     VCP: {mon.vcp_version}")
            print()
            
            # Test brightness
            brightness = controller.get_brightness(mon.id)
            print(f"     Current brightness: {brightness}%")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dbus_service():
    """Test DDC via D-Bus service"""
    print()
    print("=" * 60)
    print("TEST 2: D-Bus Service Integration")
    print("=" * 60)
    print()
    
    try:
        # Connect to Legion Power D-Bus service
        bus = dbus.SystemBus()
        
        try:
            proxy = bus.get_object('com.legion.Power', '/com/legion/Power')
            interface = dbus.Interface(proxy, 'com.legion.Power.Manager')
            print("✅ Connected to Legion Power D-Bus service")
            print()
        except dbus.exceptions.DBusException as e:
            print(f"❌ Could not connect to D-Bus service: {e}")
            print()
            print("The service might not be running. Start it with:")
            print("  sudo systemctl start legion-power.service")
            print()
            print("Or run directly for testing:")
            print("  cd backend && sudo python3 legion_power_service.py")
            return False
        
        # Test GetExternalMonitors
        print("🔍 Calling GetExternalMonitors()...")
        monitors = interface.GetExternalMonitors()
        
        if not monitors:
            print("⚠️  No monitors returned from D-Bus (DDC might not be initialized)")
            return False
        
        print(f"✅ Got {len(monitors)} monitor(s) from D-Bus:")
        print()
        
        for mon in monitors:
            mon_dict = dict(mon)
            print(f"  📺 Display {mon_dict['id']}: {mon_dict['name']}")
            print(f"     Manufacturer: {mon_dict['manufacturer']}")
            print(f"     Model: {mon_dict['model']}")
            print()
            
            # Test GetMonitorBrightness
            display_id = mon_dict['id']
            brightness = interface.GetMonitorBrightness(display_id)
            print(f"     Current brightness: {brightness}%")
            print()
        
        print("✅ D-Bus integration working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print()
    print("🖥️  Legion Power - DDC/CI Integration Test")
    print()
    
    # Test 1: Direct DDC
    test1_ok = test_ddc_direct()
    
    # Test 2: D-Bus service
    test2_ok = test_dbus_service()
    
    # Summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print(f"  Direct DDC:      {'✅ PASS' if test1_ok else '❌ FAIL'}")
    print(f"  D-Bus Service:   {'✅ PASS' if test2_ok else '❌ FAIL'}")
    print()
    
    if test1_ok and test2_ok:
        print("🎉 All tests passed! The applet should work.")
        print()
        print("Next steps:")
        print("  1. Reload Cinnamon: Alt+F2, type 'r', Enter")
        print("  2. Right-click the applet → Configure")
        print("  3. Enable 'Show external monitor brightness controls'")
        print("  4. Open the applet menu and look for monitor sliders")
        return 0
    elif test1_ok:
        print("⚠️  DDC works but D-Bus service needs update")
        print()
        print("Run the update script:")
        print("  cd /home/moodliszka/Desktop/repos/linux/power")
        print("  sudo ./scripts/update_backend.sh")
        return 1
    else:
        print("❌ DDC/CI not working properly")
        print()
        print("Troubleshooting:")
        print("  - Check ddcutil is installed: which ddcutil")
        print("  - Check monitor detected: ddcutil detect")
        print("  - Check i2c permissions: groups | grep i2c")
        return 1


if __name__ == '__main__':
    exit(main())
