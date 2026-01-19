#!/bin/bash

# Test script to verify D-Bus services are available

echo "========================================="
echo "Legion Power Applet - D-Bus Service Test"
echo "========================================="
echo ""

# Test 1: Cinnamon Settings Daemon (Screen Brightness)
echo "1. Testing Screen Brightness Service..."
if dbus-send --session --print-reply \
    --dest=org.cinnamon.SettingsDaemon.Power.Screen \
    /org/cinnamon/SettingsDaemon/Power/Screen \
    org.freedesktop.DBus.Properties.Get \
    string:"org.cinnamon.SettingsDaemon.Power.Screen" \
    string:"Brightness" 2>/dev/null | grep -q "variant"; then
    echo "   ✓ Screen brightness service is available"
else
    echo "   ✗ Screen brightness service is NOT available"
    echo "     (cinnamon-settings-daemon may not be running)"
fi

# Test 2: Keyboard Brightness
echo ""
echo "2. Testing Keyboard Brightness Service..."
if dbus-send --session --print-reply \
    --dest=org.cinnamon.SettingsDaemon.Power.Keyboard \
    /org/cinnamon/SettingsDaemon/Power/Keyboard \
    org.freedesktop.DBus.Properties.Get \
    string:"org.cinnamon.SettingsDaemon.Power.Keyboard" \
    string:"Brightness" 2>/dev/null | grep -q "variant"; then
    echo "   ✓ Keyboard brightness service is available"
else
    echo "   ✗ Keyboard brightness service is NOT available"
    echo "     (Your device may not have keyboard backlight)"
fi

# Test 3: UPower (Battery)
echo ""
echo "3. Testing UPower Service..."
if dbus-send --system --print-reply \
    --dest=org.freedesktop.UPower \
    /org/freedesktop/UPower \
    org.freedesktop.DBus.Properties.Get \
    string:"org.freedesktop.UPower" \
    string:"DaemonVersion" 2>/dev/null | grep -q "variant"; then
    echo "   ✓ UPower service is available"
else
    echo "   ✗ UPower service is NOT available"
fi

# Test 4: Power Profiles (Hadess)
echo ""
echo "4. Testing Power Profiles Service (Hadess)..."
if dbus-send --system --print-reply \
    --dest=net.hadess.PowerProfiles \
    /net/hadess/PowerProfiles \
    org.freedesktop.DBus.Properties.Get \
    string:"net.hadess.PowerProfiles" \
    string:"ActiveProfile" 2>/dev/null | grep -q "variant"; then
    echo "   ✓ Hadess PowerProfiles service is available"
    PROFILE=$(dbus-send --system --print-reply \
        --dest=net.hadess.PowerProfiles \
        /net/hadess/PowerProfiles \
        org.freedesktop.DBus.Properties.Get \
        string:"net.hadess.PowerProfiles" \
        string:"ActiveProfile" 2>/dev/null | grep "string" | awk -F'"' '{print $2}')
    echo "     Current profile: $PROFILE"
else
    echo "   ✗ Hadess PowerProfiles service is NOT available"
    echo "     (Trying UPower PowerProfiles...)"
    
    # Test 4b: Power Profiles (UPower alternative)
    if dbus-send --system --print-reply \
        --dest=org.freedesktop.UPower.PowerProfiles \
        /org/freedesktop/UPower/PowerProfiles \
        org.freedesktop.DBus.Properties.Get \
        string:"org.freedesktop.UPower.PowerProfiles" \
        string:"ActiveProfile" 2>/dev/null | grep -q "variant"; then
        echo "   ✓ UPower PowerProfiles service is available"
    else
        echo "   ✗ UPower PowerProfiles service is also NOT available"
    fi
fi

# Test 5: Legion Power Service
echo ""
echo "5. Testing Legion Power Service..."
if systemctl is-active --quiet legion-power.service; then
    echo "   ✓ Legion Power service is running"
    
    # Test Conservation Mode
    if CONSERV=$(dbus-send --system --print-reply \
        --dest=com.legion.Power \
        /com/legion/Power/Manager \
        org.freedesktop.DBus.Properties.Get \
        string:"com.legion.Power.Manager" \
        string:"ConservationMode" 2>/dev/null | grep "boolean" | awk '{print $2}'); then
        echo "     Conservation Mode: $CONSERV"
    fi
    
    # Test Rapid Charge
    if RAPID=$(dbus-send --system --print-reply \
        --dest=com.legion.Power \
        /com/legion/Power/Manager \
        org.freedesktop.DBus.Properties.Get \
        string:"com.legion.Power.Manager" \
        string:"RapidCharge" 2>/dev/null | grep "boolean" | awk '{print $2}'); then
        echo "     Rapid Charge: $RAPID"
    fi
    
    # Test Fan Mode
    if FAN=$(dbus-send --system --print-reply \
        --dest=com.legion.Power \
        /com/legion/Power/Manager \
        org.freedesktop.DBus.Properties.Get \
        string:"com.legion.Power.Manager" \
        string:"FanMode" 2>/dev/null | grep "int32" | awk '{print $2}'); then
        echo "     Fan Mode: $FAN (0=Quiet, 1=Auto, 2=Performance)"
    fi
else
    echo "   ✗ Legion Power service is NOT running"
    echo ""
    echo "     To install and start the service:"
    echo "     cd ~/Desktop/repos/linux/power/backend"
    echo "     sudo python3 install_service.py"
    echo "     sudo systemctl enable legion-power.service"
    echo "     sudo systemctl start legion-power.service"
fi

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
echo ""
