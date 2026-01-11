"""
UART Manager for Battery Data Transmission
Sends battery SOC to Waveshare RP2350B display via one-way UART
"""

from machine import UART, Pin
import config

class UARTManager:
    """Manages UART communication for sending battery data to display"""

    def __init__(self, uart_id=0, baudrate=115200, tx_pin=0, rx_pin=1):
        """
        Initialize UART interface

        Args:
            uart_id: UART peripheral ID (0 or 1)
            baudrate: Communication speed (default 115200)
            tx_pin: GPIO pin for TX
            rx_pin: GPIO pin for RX (unused but required for init)

        Raises:
            Exception: If UART initialization fails
        """
        self.uart_id = uart_id
        self.baudrate = baudrate
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin

        try:
            self.uart = UART(
                uart_id,
                baudrate=baudrate,
                tx=Pin(tx_pin),
                rx=Pin(rx_pin),
                bits=8,
                parity=None,
                stop=1
            )
            print(f"UART{uart_id} initialized: TX=GP{tx_pin}, RX=GP{rx_pin}, {baudrate} baud")

        except Exception as e:
            print(f"UART initialization failed: {e}")
            raise

        self.send_count = 0
        self.error_count = 0

    def send_battery_soc(self, soc_percentage):
        """
        Send battery SOC via UART

        Args:
            soc_percentage: Battery SOC 0-100 (int or None)

        Returns:
            True if sent successfully, False otherwise
        """
        # Validate input
        if soc_percentage is None:
            if hasattr(config, 'UART_DEBUG') and config.UART_DEBUG:
                print("UART: Skipping send (SOC is None)")
            return False

        # Clamp to valid range
        soc = max(0, min(100, int(soc_percentage)))

        # Format message
        message = f"BATTERY:{soc}\n"

        try:
            # Send via UART
            bytes_written = self.uart.write(message.encode('utf-8'))

            if bytes_written != len(message):
                print(f"UART: Incomplete write ({bytes_written}/{len(message)} bytes)")
                self.error_count += 1
                return False

            self.send_count += 1

            if hasattr(config, 'UART_DEBUG') and config.UART_DEBUG:
                print(f"UART TX: {message.strip()} ({bytes_written} bytes)")

            return True

        except Exception as e:
            print(f"UART send error: {e}")
            self.error_count += 1
            return False

    def send_battery_system(self, voltage, current, temperature):
        """
        Send battery system data via UART

        Args:
            voltage: Battery voltage in volts (float or None)
            current: Battery current in amps (float or None)
            temperature: Battery temperature in Celsius (float or None)

        Returns:
            True if sent successfully, False otherwise
        """
        # Validate inputs
        if voltage is None or current is None or temperature is None:
            if hasattr(config, 'UART_DEBUG') and config.UART_DEBUG:
                print("UART: Skipping BATSYS send (one or more values is None)")
            return False

        # Format message: BATSYS:<voltage>,<current>,<temp>\n
        message = f"BATSYS:{voltage:.1f},{current:.1f},{temperature:.1f}\n"

        try:
            # Send via UART
            bytes_written = self.uart.write(message.encode('utf-8'))

            if bytes_written != len(message):
                print(f"UART: Incomplete write ({bytes_written}/{len(message)} bytes)")
                self.error_count += 1
                return False

            self.send_count += 1

            if hasattr(config, 'UART_DEBUG') and config.UART_DEBUG:
                print(f"UART TX: {message.strip()} ({bytes_written} bytes)")

            return True

        except Exception as e:
            print(f"UART send error: {e}")
            self.error_count += 1
            return False

    def send_charging_state(self, state):
        """
        Send charging state via UART

        Args:
            state: Charging state - 0=not charging, 1=charging (int or None)

        Returns:
            True if sent successfully, False otherwise
        """
        # Validate input
        if state is None:
            if hasattr(config, 'UART_DEBUG') and config.UART_DEBUG:
                print("UART: Skipping CHARGING send (state is None)")
            return False

        # Ensure state is 0 or 1
        state_value = 1 if state else 0

        # Format message: CHARGING:<state>\n
        message = f"CHARGING:{state_value}\n"

        try:
            # Send via UART
            bytes_written = self.uart.write(message.encode('utf-8'))

            if bytes_written != len(message):
                print(f"UART: Incomplete write ({bytes_written}/{len(message)} bytes)")
                self.error_count += 1
                return False

            self.send_count += 1

            if hasattr(config, 'UART_DEBUG') and config.UART_DEBUG:
                print(f"UART TX: {message.strip()} ({bytes_written} bytes)")

            return True

        except Exception as e:
            print(f"UART send error: {e}")
            self.error_count += 1
            return False

    def get_stats(self):
        """
        Get transmission statistics

        Returns:
            Dictionary with send_count and error_count
        """
        return {
            'send_count': self.send_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(1, self.send_count)
        }

    def close(self):
        """Cleanup UART resources"""
        if self.uart:
            stats = self.get_stats()
            print(f"UART closing: {stats['send_count']} sent, {stats['error_count']} errors")
            self.uart.deinit()
            self.uart = None
