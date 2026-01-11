"""
Victron Cerbo GX Modbus TCP client
Uses micropython-modbus library to communicate with Victron devices
"""

from umodbus.tcp import TCP as ModbusTCPMaster
import config

class VictronClient:
    """
    Client for reading data from Victron Cerbo GX via Modbus TCP
    """

    # Victron Modbus Unit IDs
    UNIT_ID_SYSTEM = 100  # System/GX device
    UNIT_ID_BATTERY = 225  # Battery monitor (BMV)
    UNIT_ID_SOLAR = 226   # Solar charger (MPPT)
    UNIT_ID_INVERTER = 227  # Inverter/Charger

    def __init__(self, host=None, port=None, unit_id=None):
        """
        Initialize Victron Modbus client

        Args:
            host: Cerbo GX IP address (defaults to config.CERBO_IP)
            port: Modbus TCP port (defaults to config.CERBO_PORT)
            unit_id: Modbus unit ID (defaults to UNIT_ID_SYSTEM)
        """
        self.host = host or config.CERBO_IP
        self.port = port or config.CERBO_PORT
        self.unit_id = unit_id or self.UNIT_ID_SYSTEM
        self.client = None

    def connect(self):
        """
        Establish connection to Cerbo GX

        Returns:
            True if connected successfully
        """
        try:
            self.client = ModbusTCPMaster(
                slave_ip=self.host,
                slave_port=self.port,
                timeout=config.CONNECT_TIMEOUT
            )
            print(f"Connected to Victron Cerbo GX at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to Cerbo GX: {e}")
            return False

    def read_holding_register(self, register_addr, count=1):
        """
        Read holding register(s) - Modbus function 3

        Args:
            register_addr: Starting register address
            count: Number of registers to read

        Returns:
            List of register values or None on error
        """
        try:
            result = self.client.read_holding_registers(
                slave_addr=self.unit_id,
                starting_addr=register_addr,
                register_qty=count
            )
            return result
        except Exception as e:
            print(f"Error reading holding register {register_addr}: {e}")
            return None

    def read_input_register(self, register_addr, count=1):
        """
        Read input register(s) - Modbus function 4

        Args:
            register_addr: Starting register address
            count: Number of registers to read

        Returns:
            List of register values or None on error
        """
        try:
            result = self.client.read_input_registers(
                slave_addr=self.unit_id,
                starting_addr=register_addr,
                register_qty=count
            )
            return result
        except Exception as e:
            print(f"Error reading input register {register_addr}: {e}")
            return None

    def read_battery_voltage(self):
        """
        Read battery voltage (register 840)

        Returns:
            Voltage in volts (float) or None on error
        """
        result = self.read_input_register(840)
        if result:
            # Victron stores voltage in 0.01V units
            return result[0] * 0.1
        return None

    def read_battery_current(self):
        """
        Read battery current (register 841)

        Returns:
            Current in amps (float) or None on error
        """
        result = self.read_input_register(841)
        if result:
            # Victron stores current in 0.1A units
            # Signed value: positive = charging, negative = discharging
            value = result[0]
            if value > 32767:  # Handle negative values (two's complement)
                value -= 65536
            return value * 0.1
        return None

    def read_battery_soc(self):
        """
        Read battery state of charge (register 843)

        Returns:
            SOC as percentage (0-100) or None on error
        """
        result = self.read_input_register(843)
        if result:
            # SOC in 1% units
            return result[0]
        return None

    def read_battery_temperature(self):
        """
        Read battery temperature (register 842)

        Returns:
            Temperature in Celsius (float) or None on error
        """
        result = self.read_input_register(842)
        if result:
            # Victron stores temperature in 0.01 Kelvin units
            # Convert to Celsius: (K * 0.01) - 273.15
            kelvin = result[0] * 0.01
            celsius = kelvin - 273.15
            return round(celsius, 1)
        return None

    def get_charging_state(self, current=None):
        """
        Determine if battery is charging based on current

        Args:
            current: Battery current in amps (if None, will read from register)

        Returns:
            1 if charging (current > 0), 0 if not charging, None on error
        """
        if current is None:
            current = self.read_battery_current()

        if current is None:
            return None

        # Positive current = charging, negative/zero = not charging
        return 1 if current > 0 else 0

    def read_all_data(self):
        """
        Read all common Victron registers

        Returns:
            Dictionary with all data or None on error
        """
        battery_current = self.read_battery_current()

        data = {
            'battery_voltage': self.read_battery_voltage(),
            'battery_current': battery_current,
            'battery_temperature': self.read_battery_temperature(),
            'battery_soc': self.read_battery_soc(),
            'charging_state': self.get_charging_state(battery_current),
        }
        return data

    def close(self):
        """Close the Modbus connection"""
        if self.client:
            # Note: micropython-modbus TCP client doesn't have explicit close
            self.client = None
            print("Disconnected from Cerbo GX")
