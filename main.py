"""
Main entry point for Raspberry Pi Pico - Victron Cerbo GX interface
Reads data from Victron Cerbo GX and processes it
"""

import time
import sys
import config
from machine import Pin
from wifi_manager import WiFiManager
from uart_manager import UARTManager

def detect_demo_mode():
    """
    Detect demo mode by checking if GP2 is grounded

    Returns:
        True if demo mode enabled, False otherwise
    """
    # Configure GP2 as input with pull-up
    demo_pin = Pin(config.DEMO_PIN, Pin.IN, Pin.PULL_UP)

    # Read pin state (0 = grounded/demo mode, 1 = normal mode)
    is_demo = demo_pin.value() == 0

    if is_demo:
        print("=" * 60)
        print("                    *** DEMO MODE ***")
        print("     GP2 pin detected grounded - using simulated data")
        print("     WiFi disabled | All data is generated locally")
        print("=" * 60)

    return is_demo

def main():
    """Main application loop"""
    # Detect demo mode first
    demo_mode = detect_demo_mode()

    if not demo_mode:
        print("=" * 50)
        print("Victron Cerbo GX Reader")
        print("=" * 50)
    else:
        print("")  # Extra spacing after demo banner

    # Initialize WiFi (skip in demo mode)
    wifi = None
    if not demo_mode:
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
    else:
        print("[WiFi] Skipped - demo mode enabled\n")

    # Initialize Victron client (real or demo)
    if demo_mode:
        from demo_victron_client import DemoVictronClient
        step_label = "[1/2]"
        print(f"{step_label} Initializing demo Victron client...")
        victron = DemoVictronClient()
    else:
        from victron_client import VictronClient
        step_label = "[2/2]"
        print(f"\n{step_label} Connecting to Cerbo GX at {config.CERBO_IP}:{config.CERBO_PORT}")
        victron = VictronClient()

    if not victron.connect():
        print("ERROR: Failed to connect to Cerbo GX via Modbus TCP")
        print("Please check:")
        print("  - Modbus TCP is enabled on Cerbo GX")
        print("  - Cerbo GX is accessible at", config.CERBO_IP)
        if wifi:
            wifi.disconnect()
        return

    # Initialize UART for display communication
    uart_mgr = None
    if config.UART_ENABLED:
        step_label = "[2/2]" if demo_mode else "[3/3]"
        print(f"\n{step_label} Initializing UART on GP{config.UART_TX_PIN} (TX)")
        try:
            uart_mgr = UARTManager(
                uart_id=config.UART_ID,
                baudrate=config.UART_BAUDRATE,
                tx_pin=config.UART_TX_PIN,
                rx_pin=config.UART_RX_PIN
            )
            print("UART initialized successfully")
        except Exception as e:
            print(f"WARNING: UART initialization failed: {e}")
            print("Continuing without UART output...")
            uart_mgr = None

    # Main polling loop
    mode_text = "DEMO MODE" if demo_mode else f"interval: {config.POLL_INTERVAL}s"
    print(f"\nStarting data polling ({mode_text})")
    print("UART: Cycling through 5 messages, 1 message per second")
    print("Press Ctrl+C to stop\n")
    print("-" * 60)

    # UART message cycle counter (0-4 for 5 messages)
    uart_message_cycle = 0

    while True:
        try:
            # Check WiFi connection (skip in demo mode)
            if not demo_mode:
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
            mode_indicator = "[DEMO] " if demo_mode else ""
            print(f"\n{mode_indicator}[{time.localtime()[3]:02d}:{time.localtime()[4]:02d}:{time.localtime()[5]:02d}] Victron Data:")
            if data['battery_voltage'] is not None:
                print(f"  Battery Voltage: {data['battery_voltage']:.1f} V")
            if data['battery_current'] is not None:
                current = data['battery_current']
                direction = "Charging" if current > 0 else "Discharging"
                print(f"  Battery Current: {abs(current):.1f} A ({direction})")
            if data['battery_temperature'] is not None:
                print(f"  Battery Temp:    {data['battery_temperature']:.1f} °C")
            if data['battery_soc'] is not None:
                print(f"  Battery SOC:     {data['battery_soc']}%")
            if data['charging_state'] is not None:
                state_text = "Charging" if data['charging_state'] == 1 else "Not Charging"
                print(f"  Charging State:  {state_text}")
            if data['solar_power'] is not None:
                print(f"  Solar Power:     {data['solar_power']} W")

            # Send one UART message per cycle (cycling through 5 messages)
            if uart_mgr:
                if uart_message_cycle == 0:
                    # Message 1: Battery SOC
                    if data['battery_soc'] is not None:
                        if not uart_mgr.send_battery_soc(data['battery_soc']):
                            print("  WARNING: Failed to send SOC via UART")

                elif uart_message_cycle == 1:
                    # Message 2: Battery system data
                    if (data['battery_voltage'] is not None and
                        data['battery_current'] is not None and
                        data['battery_temperature'] is not None):
                        if not uart_mgr.send_battery_system(
                            data['battery_voltage'],
                            data['battery_current'],
                            data['battery_temperature']
                        ):
                            print("  WARNING: Failed to send BATSYS via UART")

                elif uart_message_cycle == 2:
                    # Message 3: Charging state
                    if data['charging_state'] is not None:
                        if not uart_mgr.send_charging_state(data['charging_state']):
                            print("  WARNING: Failed to send CHARGING via UART")

                elif uart_message_cycle == 3:
                    # Message 4: WiFi status
                    if demo_mode:
                        wifi_status = 2  # Skipped (demo mode)
                    elif wifi and wifi.is_connected():
                        wifi_status = 1  # Connected
                    else:
                        wifi_status = 0  # Disconnected

                    if not uart_mgr.send_wifi_status(wifi_status):
                        print("  WARNING: Failed to send WIFI status via UART")

                elif uart_message_cycle == 4:
                    # Message 5: Demo mode status
                    if not uart_mgr.send_demo_mode(demo_mode):
                        print("  WARNING: Failed to send DEMO mode via UART")

                # Increment cycle counter (wrap at 5)
                uart_message_cycle = (uart_message_cycle + 1) % 5

            time.sleep(1)  # 1 second between messages

        except KeyboardInterrupt:
            print("\n\nShutting down...")
            victron.close()
            if uart_mgr:
                uart_mgr.close()
            if wifi:
                wifi.disconnect()
            break
        except Exception as e:
            print(f"Error: {e}")
            import sys
            sys.print_exception(e)
            time.sleep(5)

if __name__ == "__main__":
    main()
