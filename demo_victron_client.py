"""
Demo Victron Client - Simulates Victron Cerbo GX data
Generates realistic changing battery/solar data for testing without hardware
"""

import time
import math

class DemoVictronClient:
    """
    Demo client that simulates VictronClient interface
    Generates realistic changing data using mathematical functions
    """

    def __init__(self, host=None, port=None, unit_id=None):
        """
        Initialize demo client (parameters ignored for compatibility)

        Args:
            host: Ignored (for interface compatibility)
            port: Ignored (for interface compatibility)
            unit_id: Ignored (for interface compatibility)
        """
        self.connected = False
        self.start_time = time.ticks_ms()

    def connect(self):
        """
        Simulate connection (always succeeds)

        Returns:
            True (always succeeds)
        """
        print("DEMO MODE: Simulated connection to Victron Cerbo GX")
        self.connected = True
        return True

    def _get_elapsed_seconds(self):
        """
        Get elapsed time since initialization

        Returns:
            Elapsed seconds as float
        """
        return time.ticks_diff(time.ticks_ms(), self.start_time) / 1000.0

    def read_battery_voltage(self):
        """
        Simulate battery voltage: 48-52V oscillating

        Returns:
            Voltage in volts (float) or None if not connected
        """
        if not self.connected:
            return None

        elapsed = self._get_elapsed_seconds()
        # 60-second cycle, oscillates between 48-52V
        voltage = 50.0 + 2.0 * math.sin(elapsed * 2 * math.pi / 60.0)
        return round(voltage, 1)

    def read_battery_current(self):
        """
        Simulate battery current: alternating charge/discharge

        Returns:
            Current in amps (float) or None if not connected
            Positive = charging, Negative = discharging
        """
        if not self.connected:
            return None

        elapsed = self._get_elapsed_seconds()
        # 120-second cycle: 60s charge, 60s discharge
        cycle_pos = (elapsed % 120) / 120.0

        if cycle_pos < 0.5:  # Charging phase (first 60 seconds)
            # Current ranges from +10A to +25A
            current = 15.0 + 10.0 * math.sin(cycle_pos * 4 * math.pi)
        else:  # Discharging phase (second 60 seconds)
            # Current ranges from -5A to -15A
            current = -10.0 - 5.0 * math.sin((cycle_pos - 0.5) * 4 * math.pi)

        return round(current, 1)

    def read_battery_temperature(self):
        """
        Simulate battery temperature: 25-30°C

        Returns:
            Temperature in Celsius (float) or None if not connected
        """
        if not self.connected:
            return None

        elapsed = self._get_elapsed_seconds()
        # 180-second cycle, varies between 25-30°C
        temp = 27.5 + 2.5 * math.sin(elapsed * 2 * math.pi / 180.0)
        return round(temp, 1)

    def read_battery_soc(self):
        """
        Simulate battery SOC: slow drift 20-95%

        Returns:
            SOC as percentage (0-100) or None if not connected
        """
        if not self.connected:
            return None

        elapsed = self._get_elapsed_seconds()
        # 300-second cycle, drifts between 20-95%
        soc_base = 57.5 + 37.5 * math.sin(elapsed * 2 * math.pi / 300.0)
        soc = int(max(20, min(95, soc_base)))
        return soc

    def get_charging_state(self, current=None):
        """
        Determine charging state from current

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
        Read all demo data - mirrors VictronClient.read_all_data()

        Returns:
            Dictionary with all data values
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
        """Simulate disconnect"""
        if self.connected:
            self.connected = False
            print("DEMO MODE: Disconnected")

    # Compatibility methods (unused in demo but present for interface compatibility)
    def read_holding_register(self, register_addr, count=1):
        """
        Not implemented in demo mode

        Returns:
            None
        """
        return None

    def read_input_register(self, register_addr, count=1):
        """
        Not implemented in demo mode

        Returns:
            None
        """
        return None
