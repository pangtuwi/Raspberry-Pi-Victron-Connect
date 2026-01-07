"""
Configuration settings for Victron Cerbo GX connection
"""

# Victron Cerbo GX connection settings
# When connected to Cerbo GX hotspot, the Cerbo IP is the gateway address
# Check WiFi connection output to see what the gateway IP is
CERBO_IP = "172.24.24.1"  # Updated from 192.168.2.1 based on your network
CERBO_PORT = 502  # Modbus TCP port (default: 502)

# WiFi settings - Cerbo GX hotspot
WIFI_SSID = "venus-HQ2449Y9R23-b05"
WIFI_PASSWORD = "7zehc2ey"

# Connection timeout (seconds)
WIFI_TIMEOUT = 30
CONNECT_TIMEOUT = 10

# Polling interval (seconds)
POLL_INTERVAL = 5

# Modbus register addresses (examples - update based on your needs)
# See Victron Modbus TCP documentation
REGISTERS = {
    "battery_voltage": 840,
    "battery_current": 841,
    "battery_soc": 843,
}

# UART settings for display communication
UART_ENABLED = True          # Master enable/disable switch
UART_ID = 0                  # UART peripheral (0 or 1)
UART_BAUDRATE = 115200       # Must match display setting
UART_TX_PIN = 0              # GP0 (Pin 1)
UART_RX_PIN = 1              # GP1 (Pin 2) - unused but required
UART_DEBUG = False           # Print UART messages to console
