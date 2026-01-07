"""
WiFi connection manager for Raspberry Pi Pico W
Handles connection to Cerbo GX hotspot
"""

import network
import time
import config

class WiFiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(self, ssid=None, password=None, timeout=30):
        """
        Connect to WiFi network

        Args:
            ssid: WiFi network name (defaults to config.WIFI_SSID)
            password: WiFi password (defaults to config.WIFI_PASSWORD)
            timeout: Connection timeout in seconds

        Returns:
            True if connected, False otherwise
        """
        ssid = ssid or config.WIFI_SSID
        password = password or config.WIFI_PASSWORD

        if self.wlan.isconnected():
            print("Already connected to WiFi")
            self._print_connection_info()
            return True

        print(f"Connecting to WiFi: {ssid}")
        self.wlan.connect(ssid, password)

        # Wait for connection
        start_time = time.time()
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                print(f"WiFi connection timeout after {timeout}s")
                return False
            print(".", end="")
            time.sleep(1)

        print("\nWiFi connected!")
        self._print_connection_info()
        return True

    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
            print("WiFi disconnected")

    def is_connected(self):
        """Check if connected to WiFi"""
        return self.wlan.isconnected()

    def get_ip(self):
        """Get current IP address"""
        if self.wlan.isconnected():
            return self.wlan.ifconfig()[0]
        return None

    def _print_connection_info(self):
        """Print connection details"""
        if self.wlan.isconnected():
            ifconfig = self.wlan.ifconfig()
            print(f"  IP Address:  {ifconfig[0]}")
            print(f"  Subnet Mask: {ifconfig[1]}")
            print(f"  Gateway:     {ifconfig[2]}")
            print(f"  DNS Server:  {ifconfig[3]}")

    def scan(self):
        """Scan for available WiFi networks"""
        print("Scanning for WiFi networks...")
        networks = self.wlan.scan()

        print(f"Found {len(networks)} networks:")
        for net in networks:
            ssid = net[0].decode('utf-8')
            bssid = ':'.join('%02x' % b for b in net[1])
            channel = net[2]
            rssi = net[3]
            security = net[4]
            print(f"  {ssid:32} Channel: {channel:2d} RSSI: {rssi:3d} dBm")

        return networks
