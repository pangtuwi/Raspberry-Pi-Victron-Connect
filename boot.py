"""
Boot script for Raspberry Pi Pico
Runs once on startup before main.py
"""

import machine
import time

print("Booting Raspberry Pi Pico...")
print(f"Frequency: {machine.freq() / 1000000:.1f} MHz")

# Add any initialization code here
# e.g., WiFi setup, hardware initialization
