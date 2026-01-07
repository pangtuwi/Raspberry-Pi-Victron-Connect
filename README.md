# Victron Cerbo GX Reader - Raspberry Pi Pico

MicroPython application for Raspberry Pi Pico to interface with Victron Cerbo GX energy management system.

## Hardware Requirements

- **Raspberry Pi Pico W** (WiFi required)
- Victron Cerbo GX with WiFi hotspot enabled
- USB cable for programming the Pico

## Setup

### 1. Install MicroPython Firmware

Download and install the latest MicroPython firmware for Pico W from [micropython.org](https://micropython.org/download/RPI_PICO_W/)

### 2. Install Dependencies

Connect your Pico W to WiFi (can use any network temporarily), then in the REPL:

```python
import mip
mip.install('github:brainelectronics/micropython-modbus')
```

### 3. Deploy Code

**Option A: Using VS Code** (Recommended)
1. Install MicroPico or Pico-W-Go extension
2. Connect Pico W via USB
3. Cmd+Shift+P → "MicroPico: Connect"
4. Right-click project folder → "Upload project to Pico"

**Option B: Using command line**
```bash
./deploy.sh
```

Files to deploy:
- `main.py`
- `boot.py`
- `config.py`
- `wifi_manager.py`
- `victron_client.py`
- `uart_manager.py`

### 4. Configure

The `config.py` is already set up with:
- Cerbo GX WiFi hotspot credentials
- Cerbo GX IP (192.168.2.1)
- Modbus TCP port (502)
- Polling interval (5 seconds)

You can adjust these settings if needed.

## Victron Cerbo GX Communication

The Cerbo GX supports multiple protocols:
- **Modbus TCP** (recommended): Port 502, requires enabling in Cerbo GX settings
- **MQTT**: Can be enabled in Cerbo GX for publish/subscribe model
- **VE.Direct**: Serial protocol (requires UART connection)

This project is set up for Modbus TCP by default.

## Enabling Services on Cerbo GX

### Enable WiFi Hotspot
1. Access Cerbo GX via VRM portal or local display
2. Navigate to Settings → WiFi
3. Enable "Create access point"
4. Note the SSID and password

### Enable Modbus TCP
1. Navigate to Settings → Services
2. Enable Modbus TCP
3. Default port is 502

## Usage

Once deployed and configured, the Pico W will:
1. Connect to the Cerbo GX WiFi hotspot
2. Establish Modbus TCP connection
3. Poll data every 5 seconds (configurable)
4. Display: Battery voltage, current, SOC, and solar power
5. Send Battery SOC via UART to external display (if enabled)

Monitor output via serial connection (115200 baud).

### UART Display Output

The Pico W can send battery SOC data to an external display via UART:

**Hardware Connection:**
- Pico W GP0 (Pin 1) → Display RX
- Pico W GND (Pin 3) → Display GND

**Protocol:**
- Format: `BATTERY:<soc>\n` (e.g., `BATTERY:85\n`)
- Baud Rate: 115200
- Update Frequency: Every 5 seconds

**Configuration:**
- Enable/disable in `config.py`: `UART_ENABLED = True`
- Pin configuration: `UART_TX_PIN = 0` (GP0)
- Debug mode: `UART_DEBUG = True` (prints UART messages to console)

See `battery_monitor.py` and `DISPLAY_INTEGRATION.md` for display-side implementation details.

## Data Retrieved

The application reads the following Victron registers:
- **Battery Voltage** (V): Current battery voltage
- **Battery Current** (A): Charging (+) or discharging (-) current
- **Battery SOC** (%): State of charge (0-100%)
- **Solar Power** (W): Current solar panel production

## Development

See `CLAUDE.md` for detailed development instructions, architecture, and API reference.
