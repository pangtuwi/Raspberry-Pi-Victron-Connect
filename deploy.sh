#!/bin/bash
# Deployment script for Raspberry Pi Pico W
# Copies all files to the Pico using mpremote

echo "=================================================="
echo "Deploying Victron Cerbo GX Reader to Pico W"
echo "=================================================="
echo ""

# Check if mpremote is installed
if ! command -v mpremote &> /dev/null; then
    echo "ERROR: mpremote not found"
    echo "Install with: pip install mpremote"
    exit 1
fi

# Check if Pico is connected
if ! mpremote ls &> /dev/null; then
    echo "ERROR: Pico W not detected"
    echo "Please connect your Pico W via USB"
    exit 1
fi

echo "✓ Pico W detected"
echo ""

# Copy all files
echo "Copying files to Pico W..."
mpremote fs cp main.py :main.py && echo "  ✓ main.py"
mpremote fs cp boot.py :boot.py && echo "  ✓ boot.py"
mpremote fs cp config.py :config.py && echo "  ✓ config.py"
mpremote fs cp wifi_manager.py :wifi_manager.py && echo "  ✓ wifi_manager.py"
mpremote fs cp victron_client.py :victron_client.py && echo "  ✓ victron_client.py"

echo ""
echo "=================================================="
echo "Deployment complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Install micropython-modbus library on Pico W:"
echo "   - Connect Pico W to any WiFi network temporarily"
echo "   - In REPL: import mip; mip.install('github:brainelectronics/micropython-modbus')"
echo ""
echo "2. Enable services on Cerbo GX:"
echo "   - Enable WiFi hotspot"
echo "   - Enable Modbus TCP (Settings → Services)"
echo ""
echo "3. Reset Pico W to run the application"
echo ""
echo "To monitor output: mpremote"
