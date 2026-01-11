# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Raspberry Pi Pico - Victron Cerbo GX Interface**: MicroPython application that connects to a Victron Cerbo GX energy management system to read battery data.

**Hardware Target**: Raspberry Pi Pico W (WiFi required)

**Network Setup**: Connects to Cerbo GX WiFi hotspot (venus-HQ2449Y9R23-b05)

**Communication Protocols**:
- Modbus TCP (WiFi) for reading Cerbo GX data
- UART (serial) for sending data to external display

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
mpremote fs cp uart_manager.py :uart_manager.py

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
├── uart_manager.py       # UART communication for display output
├── battery_monitor.py    # Display module (for Waveshare RP2350B)
├── DISPLAY_INTEGRATION.md  # Display integration instructions
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
- Battery Voltage: Register 840 (0.1V units) → converted to volts
- Battery Current: Register 841 (0.1A units, signed) → converted to amps
- Battery Temperature: Register 842 (0.01K units) → converted to Celsius
- Battery SOC: Register 843 (1% units) → percentage 0-100

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
- **Unit IDs**: Victron devices use different Modbus unit IDs (100=System, 225=Battery, 227=Inverter)

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

**UART Configuration:**
- `UART_ENABLED`: Enable/disable UART transmission (default: True)
- `UART_ID`: UART peripheral 0 or 1 (default: 0)
- `UART_BAUDRATE`: Communication speed (default: 115200)
- `UART_TX_PIN`: GPIO pin for TX (default: 0 = GP0)
- `UART_RX_PIN`: GPIO pin for RX (default: 1 = GP1, unused)
- `UART_DEBUG`: Print UART messages to console (default: False)

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
voltage = victron.read_battery_voltage()      # Returns float (volts)
current = victron.read_battery_current()      # Returns float (amps, signed)
temperature = victron.read_battery_temperature()  # Returns float (Celsius)
soc = victron.read_battery_soc()              # Returns int (0-100%)
charging = victron.get_charging_state()       # Returns 1 (charging) or 0 (not charging)

# Read all data at once
data = victron.read_all_data()  # Returns dict with all values:
# {
#   'battery_voltage': float,
#   'battery_current': float,
#   'battery_temperature': float,
#   'battery_soc': int,
#   'charging_state': int (0 or 1)
# }

# Low-level access
values = victron.read_input_register(840, count=1)  # Read register directly
```

### Adding New Registers

To read additional Victron data:
1. Find register address in Victron's Modbus TCP documentation
2. Determine if it's a holding register (function 3) or input register (function 4)
3. Add method to `VictronClient` with appropriate scaling
4. Update `read_all_data()` if needed

## UART Communication

The project includes UART support for sending battery data to an external display (e.g., Waveshare RP2350B). Three types of messages are transmitted: battery SOC, battery system data (voltage/current/temperature), and charging state.

### UART Manager API

The `UARTManager` class in `uart_manager.py` provides one-way UART transmission:

```python
from uart_manager import UARTManager

# Initialize UART
uart_mgr = UARTManager(
    uart_id=0,        # UART peripheral (0 or 1)
    baudrate=115200,  # Communication speed
    tx_pin=0,         # GP0 for TX
    rx_pin=1          # GP1 for RX (unused but required)
)

# Send battery SOC (0-100)
success = uart_mgr.send_battery_soc(85)  # Returns True/False

# Send battery system data (voltage, current, temperature)
success = uart_mgr.send_battery_system(48.5, 12.3, 25.5)  # Returns True/False

# Send charging state (0=not charging, 1=charging)
success = uart_mgr.send_charging_state(1)  # Returns True/False

# Send WiFi status (0=disconnected, 1=connected, 2=skipped)
success = uart_mgr.send_wifi_status(1)  # Returns True/False

# Send demo mode status (0=normal, 1=demo)
success = uart_mgr.send_demo_mode(0)  # Returns True/False

# Get transmission statistics
stats = uart_mgr.get_stats()
# Returns: {'send_count': N, 'error_count': N, 'error_rate': 0.0}

# Cleanup
uart_mgr.close()
```

### UART Protocol

The system transmits five types of messages via UART:

**1. Battery State of Charge**
- Format: `BATTERY:<soc>\n`
- `soc`: State of Charge (0-100)
- Example: `BATTERY:75\n`

**2. Battery System Data**
- Format: `BATSYS:<voltage>,<current>,<temp>\n`
- `voltage`: Battery voltage in volts (e.g., 48.5)
- `current`: Current in amps (positive=charging, negative=discharging)
- `temp`: Battery temperature in °C
- Example: `BATSYS:48.5,12.3,25.5\n`

**3. Charging State**
- Format: `CHARGING:<state>\n`
- `state`: 0=not charging, 1=charging
- Example: `CHARGING:1\n`

**4. WiFi Status**
- Format: `WIFI:<status>\n`
- `status`: 0=disconnected, 1=connected, 2=skipped (demo mode)
- Example: `WIFI:1\n`

**5. Demo Mode Status**
- Format: `DEMO:<state>\n`
- `state`: 0=normal mode, 1=demo mode
- Example: `DEMO:0\n`

**Specifications**:
- Baud Rate: 115200
- Data Format: 8N1 (8 data bits, no parity, 1 stop bit)
- Encoding: UTF-8
- Line Terminator: `\n` (line feed)
- Direction: One-way (Pico W TX → Display RX)

**Transmission Pattern**:
- Messages sent in a 5-second cycle, one message per second
- Cycle order: BATTERY → BATSYS → CHARGING → WIFI → DEMO (repeat)
- Each message transmitted once every 5 seconds
- 1 second interval between messages
- Example timing:
  - Second 0: `BATTERY:75\n`
  - Second 1: `BATSYS:48.5,12.3,25.5\n`
  - Second 2: `CHARGING:1\n`
  - Second 3: `WIFI:1\n`
  - Second 4: `DEMO:0\n`
  - Second 5: `BATTERY:76\n` (cycle repeats)

### Hardware Connection

| Pico W | Pin | GPIO | Signal | → | Display | GPIO | Pin |
|--------|-----|------|--------|---|---------|------|-----|
| Pin 1  | GP0 | TX   | UART0  | → | GP17    | RX   | Pin 22 |
| Pin 3  | GND | -    | Ground | → | GND     | -    | Pin 23 |

**Critical**:
- Connect TX to RX (not TX to TX)
- Common ground is essential for UART communication
- Both devices use 3.3V logic levels (compatible)

### Display Integration

For display-side implementation:

1. **Copy Files**: Transfer `battery_monitor.py` to your Waveshare display project
2. **Integration Guide**: See `DISPLAY_INTEGRATION.md` for detailed instructions
3. **Display Module**: Based on `jtj.py` template from HA-Waveshare-Display repository

The display module provides:
- Circular gauge visualization (0-100%)
- Image background support
- Staleness detection (15-second timeout)
- Automatic rendering on data update

### Error Handling

**UART Initialization Failure**:
- System continues operation without UART
- Error message printed to console
- Non-fatal (Modbus data collection unaffected)

**UART Send Failure**:
- Warning message printed
- Transmission statistics updated
- Retries on next poll cycle
- No impact on main functionality

**Data Validation**:
- `None` values are skipped (not transmitted)
- SOC clamped to 0-100 range
- Invalid values rejected with error log

## Demo Mode

The project includes a hardware-triggered demo mode for testing without Victron hardware.

### Activating Demo Mode

**Hardware Setup:**
1. Connect GPIO2 (GP2, Pin 4) to GND (Pin 3 or Pin 8) using a jumper wire
2. Power cycle the Pico W (demo mode only checked at startup)
3. Remove jumper and restart to return to normal mode

**Pin Locations:**
- GP2: Pin 4 (GPIO 2)
- GND: Pin 3 or Pin 8 (Ground)

### Demo Mode Behavior

When demo mode is active:
- **WiFi completely skipped** - faster startup, no network required
- **Simulated Victron data** - realistic changing values
- **UART works normally** - can test display integration
- **Clear visual indication** - "DEMO MODE" banner in console output

### Demo Data Characteristics

All values use mathematical functions for realistic cycling:

- **Battery Voltage**: 48-52V oscillating (60-second sine wave cycle)
- **Battery Current**: Alternates charging (+10 to +25A) / discharging (-5 to -15A) every 60 seconds (120-second total cycle)
- **Battery SOC**: Slowly drifts 20-95% (300-second cycle)
- **Battery Temperature**: Varies 25-30°C (180-second cycle)
- **Charging State**: Derived from current (matches charge/discharge cycle)

### Demo Mode Implementation

The `DemoVictronClient` class (`demo_victron_client.py`) provides:
- Identical interface to `VictronClient` - drop-in replacement
- Zero memory overhead - uses time-based calculations only
- All methods return realistic simulated data
- Compatible with all existing UART and display code

**Detection Logic:**
```python
# GP2 configured with pull-up resistor
# Low (0) when grounded = demo mode
# High (1) when floating = normal mode
demo_pin = Pin(2, Pin.IN, Pin.PULL_UP)
is_demo = demo_pin.value() == 0
```

### Testing Demo Mode

```bash
# 1. Add jumper: GP2 (Pin 4) to GND (Pin 3 or Pin 8)
# 2. Reset Pico W
# 3. Expected output:
```

```
==============================================================
                    *** DEMO MODE ***
     GP2 pin detected grounded - using simulated data
     WiFi disabled | All data is generated locally
==============================================================

[WiFi] Skipped - demo mode enabled

[1/2] Initializing demo Victron client...
DEMO MODE: Simulated connection to Victron Cerbo GX

[2/2] Initializing UART on GP0 (TX)
UART0 initialized: TX=GP0, RX=GP1, 115200 baud

Starting data polling (DEMO MODE)
Press Ctrl+C to stop

------------------------------------------------------------

[DEMO] [14:23:45] Victron Data:
  Battery Voltage: 51.2 V
  Battery Current: 18.5 A (Charging)
  Battery Temp:    28.3 °C
  Battery SOC:     67%
  Charging State:  Charging
```

### Configuration

Edit `config.py` to customize demo mode:
- `DEMO_PIN`: GPIO pin number for demo detection (default: 2)
- `DEMO_PIN_PULL`: Pull resistor direction (default: 1 = pull-up)

### Use Cases

- **Display development**: Test display code without Victron hardware
- **UART protocol testing**: Verify UART communication and parsing
- **Algorithm development**: Test data processing logic
- **Demonstrations**: Show system behavior without full setup
- **Travel development**: Work on code without Cerbo GX access

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
