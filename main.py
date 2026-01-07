"""
Main entry point for Raspberry Pi Pico - Victron Cerbo GX interface
Reads data from Victron Cerbo GX and processes it
"""

import time
import sys
import config
from wifi_manager import WiFiManager
from victron_client import VictronClient

def main():
    """Main application loop"""
    print("=" * 50)
    print("Victron Cerbo GX Reader")
    print("=" * 50)

    # Initialize WiFi
    wifi = WiFiManager()

    # Disconnect from any existing WiFi connection first
    wifi.disconnect()

    # Connect to Cerbo GX hotspot
    print("\n[1/2] Connecting to Cerbo GX WiFi hotspot...")
    if not wifi.connect(timeout=config.WIFI_TIMEOUT):
        print("ERROR: Failed to connect to WiFi")
        print("Please check:")
        print(f"  - SSID: {config.WIFI_SSID}")
        print("  - Password is correct")
        print("  - Cerbo GX hotspot is enabled")
        return

    # Initialize Modbus connection to Cerbo GX
    print(f"\n[2/2] Connecting to Cerbo GX at {config.CERBO_IP}:{config.CERBO_PORT}")
    victron = VictronClient()
    if not victron.connect():
        print("ERROR: Failed to connect to Cerbo GX via Modbus TCP")
        print("Please check:")
        print("  - Modbus TCP is enabled on Cerbo GX")
        print("  - Cerbo GX is accessible at", config.CERBO_IP)
        wifi.disconnect()
        return

    # Main polling loop
    print(f"\nStarting data polling (interval: {config.POLL_INTERVAL}s)")
    print("Press Ctrl+C to stop\n")
    print("-" * 60)

    while True:
        try:
            # Check WiFi connection
            if not wifi.is_connected():
                print("WiFi disconnected! Reconnecting...")
                if not wifi.connect(timeout=config.WIFI_TIMEOUT):
                    print("Failed to reconnect. Retrying in 10s...")
                    time.sleep(10)
                    continue
                # Reconnect to Modbus after WiFi reconnection
                if not victron.connect():
                    print("Failed to reconnect to Cerbo GX. Retrying in 10s...")
                    time.sleep(10)
                    continue

            # Read all Victron data
            data = victron.read_all_data()

            # Display results
            print(f"\n[{time.localtime()[3]:02d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d}] Victron Data:")
            if data['battery_voltage'] is not None:
                print(f"  Battery Voltage: {data['battery_voltage']:.2f} V")
            if data['battery_current'] is not None:
                current = data['battery_current']
                direction = "Charging" if current > 0 else "Discharging"
                print(f"  Battery Current: {abs(current):.1f} A ({direction})")
            if data['battery_soc'] is not None:
                print(f"  Battery SOC:     {data['battery_soc']}%")
            if data['solar_power'] is not None:
                print(f"  Solar Power:     {data['solar_power']} W")

            time.sleep(config.POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n\nShutting down...")
            victron.close()
            wifi.disconnect()
            break
        except Exception as e:
            print(f"Error: {e}")
            import sys
            sys.print_exception(e)
            time.sleep(5)

if __name__ == "__main__":
    main()
