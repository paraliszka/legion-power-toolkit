#!/bin/bash
# Test ACPI calls for Lenovo Legion 5

set -e

echo "🧪 Testing ACPI calls for Lenovo Legion 5..."
echo ""

# Check if acpi_call is loaded
if [ ! -e /proc/acpi/call ]; then
    echo "❌ acpi_call module not loaded"
    echo "   Loading module..."
    sudo modprobe acpi_call || {
        echo "❌ Failed to load acpi_call module"
        echo "   Install with: sudo apt install acpi-call-dkms"
        exit 1
    }
fi

echo "✅ acpi_call module loaded"
echo ""

# Test conservation mode read
echo "Testing Conservation Mode (read)..."
echo '\_SB.PCI0.LPC0.EC0.BTSG' | sudo tee /proc/acpi/call > /dev/null
RESULT=$(sudo cat /proc/acpi/call | tr -d '\0')
echo "  Result: $RESULT"
if [ "$RESULT" = "0x0" ]; then
    echo "  ✅ Conservation mode: OFF"
elif [ "$RESULT" = "0x1" ]; then
    echo "  ✅ Conservation mode: ON"
else
    echo "  ⚠️  Unexpected result: $RESULT"
fi
echo ""

# Test rapid charge read
echo "Testing Rapid Charge (read)..."
echo '\_SB.PCI0.LPC0.EC0.FCGM' | sudo tee /proc/acpi/call > /dev/null
RESULT=$(sudo cat /proc/acpi/call | tr -d '\0')
echo "  Result: $RESULT"
if [ "$RESULT" = "0x0" ]; then
    echo "  ✅ Rapid charge: OFF"
elif [ "$RESULT" = "0x1" ]; then
    echo "  ✅ Rapid charge: ON"
else
    echo "  ⚠️  Unexpected result: $RESULT"
fi
echo ""

# Test sysfs access
echo "Testing Sysfs access..."
VPC_PATH="/sys/devices/pci0000:00/0000:00:14.3/PNP0C09:00/VPC2004:00"

if [ ! -d "$VPC_PATH" ]; then
    echo "  ❌ VPC device not found at $VPC_PATH"
    exit 1
fi

echo "  ✅ VPC device found"

# Test conservation mode via sysfs
if [ -f "$VPC_PATH/conservation_mode" ]; then
    CONS=$(cat $VPC_PATH/conservation_mode)
    echo "  ✅ Conservation mode (sysfs): $CONS"
else
    echo "  ⚠️  conservation_mode not available via sysfs"
fi

# Test fan mode via sysfs
if [ -f "$VPC_PATH/fan_mode" ]; then
    FAN=$(cat $VPC_PATH/fan_mode)
    echo "  ✅ Fan mode (sysfs): $FAN"
else
    echo "  ⚠️  fan_mode not available via sysfs"
fi

echo ""
echo "✅ ACPI tests complete!"
