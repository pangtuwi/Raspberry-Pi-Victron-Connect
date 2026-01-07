# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Raspberry Pi Pico - Victron Cerbo GX Interface**: MicroPython application that connects to a Victron Cerbo GX energy management system to read solar/battery data.

**Hardware Target**: Raspberry Pi Pico W (WiFi required)

**Network Setup**: Connects to Cerbo GX WiFi hotspot (venus-HQ2449Y9R23-b05)

**Communication Protocol**: Modbus TCP (default port 502)

## Development Workflow

### Deploying Code to Raspberry Pi Pico

**Using VS Code** (Recommended for this project):
```bash
# 1. Install the MicroPico extension (or Pico-W-Go)
#    - Open VS Code Extensions (Cmd+Shift+X)
#    - Search for "MicroPico" or "Pico-W-Go"
#    - Install the extension
#
# 2. Connect Pico W via USB
#
# 3. Configure MicroPico:
#    - Cmd+Shift+P → "MicroPico: Connect"
#    - Select your Pico W from the device list
#
# 4. Upload files:
#    - Right-click on file → "Upload current file to Pico"
#    - Or use "MicroPico: Upload project to Pico" for all files
#
# 5. Run and monitor:
#    - MicroPico automatically opens a terminal showing Pico output
#    - Use "MicroPico: Run current file" to test without uploading
#    - Hard reset: Cmd+Shift+P → "MicroPico: Reset"
```

**Using Thonny IDE** (Alternative for beginners):
```bash
# 1. Open Thonny IDE
# 2. Select "MicroPython (Raspberry Pi Pico)" interpreter
# 3. Connect Pico via USB
# 4. Use File → Save to device to copy files
```

**Using mpremote** (Command line):
```bash
# Install mpremote
pip install mpremote

# Quick deployment: use the provided script
./deploy.sh

# Or manually copy all files to Pico
mpremote fs cp main.py :main.py
mpremote fs cp boot.py :boot.py
mpremote fs cp config.py :config.py
mpremote fs cp wifi_manager.py :wifi_manager.py
mpremote fs cp victron_client.py :victron_client.py

# Install dependencies on Pico (requires internet connection)
mpremote exec "import mip; mip.install('github:brainelectronics/micropython-modbus')"

# Run main.py without copying
mpremote run main.py

# Access REPL
mpremote
```

**Using ampy**:
```bash
# Install ampy
pip install adafruit-ampy

# Copy file to Pico
ampy --port /dev/tty.usbmodem1234 put main.py

# Run file
ampy --port /dev/tty.usbmodem1234 run main.py
```

### Testing Without Hardware

Since this is embedded code, testing without the Pico or Cerbo GX requires mocking:
- Use `unittest.mock` for unit tests
- Create stub implementations of hardware interfaces
- Test business logic separately from hardware I/O

### Serial Monitor / REPL Access

```bash
# Using mpremote
mpremote

# Using screen (macOS/Linux)
screen /dev/tty.usbmodem1234 115200

# Exit screen: Ctrl-A then K
```

## Project Structure

```
.
├── .vscode/
│   ├── extensions.json   # Recommended VS Code extensions
│   ├── settings.json     # VS Code workspace settings
│   └── launch.json       # Debug configuration (if using debugpy)
├── main.py               # Main application entry point
├── boot.py               # Runs on startup before main.py
├── config.py             # Configuration (IP, ports, registers, WiFi credentials)
├── wifi_manager.py       # WiFi connection handler for Pico W
├── victron_client.py     # Victron Modbus TCP client wrapper
├── deploy.sh             # Automated deployment script (mpremote)
├── .gitignore            # Git ignore patterns
└── README.md             # Project documentation
```

### Dependencies

**micropython-modbus** (external library):
- GitHub: https://github.com/brainelectronics/micropython-modbus
- Provides Modbus TCP and RTU client functionality
- Install via: `import mip; mip.install('github:brainelectronics/micropython-modbus')`
- Must be installed on the Pico W (requires internet connection during setup)
- Import statement: `from umodbus.tcp import TCP as ModbusTCPMaster`

**VS Code Extensions** (recommended):
- **Pico-W-Go**: MicroPython support for Pico W (upload, run, REPL)
  - Alternative: **MicroPico** (newer, actively maintained)
- **Python**: General Python language support
- **Pylance**: Python IntelliSense and type checking

## Victron Cerbo GX Integration

### Communication Protocol

**Modbus TCP** is the primary protocol:
- Default port: 502
- Must be enabled in Cerbo GX: Settings → Services → Modbus TCP
- Uses standard Modbus register addressing

**Key Victron Modbus Registers** (implemented in `victron_client.py`):
- Battery Voltage: Register 840 (0.01V units) → converted to volts
- Battery Current: Register 841 (0.1A units, signed) → converted to amps
- Battery SOC: Register 843 (1% units) → percentage 0-100
- Solar Power: Register 850 (1W units) → watts

**Important Notes**:
- Most registers use input registers (function code 4), not holding registers
- Values require scaling (e.g., 1234 at register 840 = 12.34V)
- Signed values use two's complement (e.g., negative current = discharging)

Reference: [Victron Modbus TCP Documentation](https://www.victronenergy.com/live/ccgx:modbustcp_faq)

### Alternative Protocols

- **MQTT**: Publish/subscribe model, requires MQTT broker
- **VE.Direct**: Serial protocol via UART (requires physical connection)

## MicroPython on Raspberry Pi Pico

### Memory Constraints

- Limited RAM (~264KB available)
- Be mindful of string concatenation and large data structures
- Use generators for large datasets
- Consider garbage collection: `import gc; gc.collect()`

### Network Connectivity

**This project uses Pico W** connecting to the Cerbo GX WiFi hotspot.

The `wifi_manager.py` module handles:
- Automatic connection to Cerbo GX hotspot
- Connection monitoring and auto-reconnect
- Network diagnostics and scanning

**Cerbo GX Hotspot Details**:
- When Cerbo GX runs as a WiFi hotspot, it assigns itself an IP (typically gateway IP)
- Common IP ranges: `172.24.24.x` or `192.168.2.x` (varies by Cerbo GX configuration)
- **Important:** Check the "Gateway" IP shown in WiFi connection output - that's your Cerbo GX IP
- DHCP assigns client IPs in the same subnet
- Hotspot SSID format: `venus-<serial>-<suffix>`

### Common Pitfalls

- **Modbus library installation**: The micropython-modbus library must be installed on the Pico via `mip`. This requires the Pico to have internet connectivity during setup (can use any WiFi network temporarily).
- **Blocking operations**: Modbus TCP operations are blocking. The current implementation uses simple polling with timeouts.
- **Time synchronization**: Pico has no RTC battery; time resets on power loss. Timestamps show local time since boot.
- **Exception handling**: All network operations are wrapped in try/except for resilience
- **Unit IDs**: Victron devices use different Modbus unit IDs (100=System, 225=Battery, 226=Solar, 227=Inverter)

## Configuration

Edit `config.py` for environment-specific settings:
- `CERBO_IP`: Victron Cerbo GX IP address (check Gateway IP from WiFi connection output)
- `CERBO_PORT`: Modbus TCP port (default: 502)
- `WIFI_SSID`: Cerbo GX hotspot network name
- `WIFI_PASSWORD`: Cerbo GX hotspot WiFi key
- `WIFI_TIMEOUT`: WiFi connection timeout in seconds
- `POLL_INTERVAL`: How often to read data (seconds)
- `REGISTERS`: Modbus register addresses to read

**Finding Your Cerbo GX IP:**
When the Pico W connects to WiFi, it displays network info including the Gateway IP.
The Gateway IP is your Cerbo GX IP address - update `CERBO_IP` in config.py to match this.

For local development overrides, create `config_local.py` (gitignored).

**Security Note**: The WiFi credentials are stored in plaintext in `config.py`. For production use, consider alternative credential storage methods.

## Victron Client API

The `VictronClient` class in `victron_client.py` provides a high-level interface:

```python
from victron_client import VictronClient

# Initialize and connect
victron = VictronClient()
victron.connect()

# Read individual values
voltage = victron.read_battery_voltage()  # Returns float (volts)
current = victron.read_battery_current()  # Returns float (amps, signed)
soc = victron.read_battery_soc()          # Returns int (0-100%)
power = victron.read_solar_power()        # Returns int (watts)

# Read all data at once
data = victron.read_all_data()  # Returns dict with all values

# Low-level access
values = victron.read_input_register(840, count=1)  # Read register directly
```

### Adding New Registers

To read additional Victron data:
1. Find register address in Victron's Modbus TCP documentation
2. Determine if it's a holding register (function 3) or input register (function 4)
3. Add method to `VictronClient` with appropriate scaling
4. Update `read_all_data()` if needed

## Important Notes

- **Modbus TCP must be enabled** on the Cerbo GX: Settings → Services → Modbus TCP
- **WiFi hotspot must be enabled** on the Cerbo GX for this setup
- **Dependencies must be installed** on the Pico W via `mip` (requires temporary internet)
- The Pico W connects directly to the Cerbo GX hotspot (no router needed)
- **Cerbo GX IP varies** - check the Gateway IP from WiFi connection output and update `config.py`
- Victron register addresses are documented in their Modbus TCP FAQ and Excel spreadsheet
- Register values often need scaling - the `VictronClient` class handles this automatically
- The Cerbo GX Modbus unit ID is typically 100 for system data (configurable in VictronClient)

## Debugging

Enable verbose logging in your code:
```python
DEBUG = True

if DEBUG:
    print(f"Connecting to {CERBO_IP}:{CERBO_PORT}")
```

Monitor via serial connection to see print() output in real-time.

## Troubleshooting

### Connection Issues

**Problem:** `[Errno 103] ECONNABORTED` when connecting to Cerbo GX

**Solutions:**
1. Check Modbus TCP is enabled on Cerbo GX (Settings → Services)
2. Verify `CERBO_IP` in config.py matches the Gateway IP shown in WiFi connection output
3. Ensure you're connected to the Cerbo GX hotspot (not another WiFi network)
4. The Pico W may be connected to a previous WiFi - `main.py` now disconnects first

**Problem:** `ImportError: can't import name ModbusTCPMaster`

**Solution:** The correct import is `from umodbus.tcp import TCP as ModbusTCPMaster`

**Problem:** Already connected to wrong WiFi network

**Solution:** The app now calls `wifi.disconnect()` before connecting to Cerbo GX hotspot
