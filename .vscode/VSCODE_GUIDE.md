# VS Code Quick Reference for Pico W Development

## Initial Setup

1. **Install Extension**:
   - Open Extensions (Cmd+Shift+X)
   - Search for "MicroPico" or "Pico-W-Go"
   - Install

2. **First Time Connection**:
   - Connect Pico W via USB
   - Cmd+Shift+P → "MicroPico: Connect"
   - Select your Pico W device

## Common Commands

### File Operations
- **Upload current file**: Right-click file → "Upload current file to Pico"
- **Upload all files**: Right-click folder → "Upload project to Pico"
- **Download from Pico**: Right-click → "Download file from Pico"

### Running Code
- **Run current file**: Cmd+Shift+P → "MicroPico: Run current file"
- **Stop execution**: Click "Stop" in terminal or disconnect/reconnect

### Device Management
- **Connect to Pico**: Cmd+Shift+P → "MicroPico: Connect"
- **Disconnect**: Cmd+Shift+P → "MicroPico: Disconnect"
- **Hard Reset Pico**: Cmd+Shift+P → "MicroPico: Reset"
- **Soft Reset**: Ctrl+D in REPL terminal

### REPL Terminal
- **Open REPL**: Automatically opens when connected
- **Close REPL**: Click trash icon in terminal
- **Switch to REPL mode**: Ctrl+C (stops current program)

## Workflow Tips

### Typical Development Cycle
1. Edit code in VS Code
2. Save file (Cmd+S)
3. Right-click → "Upload current file to Pico"
4. Watch output in terminal
5. Soft reset (Ctrl+D) to restart

### Testing WiFi Connection
```python
# In REPL
from wifi_manager import WiFiManager
wifi = WiFiManager()
wifi.connect()  # Should connect to Cerbo GX
wifi.scan()     # See available networks
```

### Testing Modbus Connection
```python
# In REPL
from victron_client import VictronClient
victron = VictronClient()
victron.connect()
data = victron.read_all_data()
print(data)
```

### Installing Libraries on Pico
```python
# In REPL (requires internet connection)
import mip
mip.install('github:brainelectronics/micropython-modbus')
```

## Troubleshooting

### Can't connect to Pico
- Check USB cable is connected
- Try unplugging and replugging
- Reset Pico (hold BOOTSEL, press reset)
- Disconnect other serial programs (Thonny, mpremote)

### Upload fails
- Make sure you're connected (check status bar)
- Try disconnecting and reconnecting
- Check file paths are correct (no spaces in filenames)

### Code doesn't run on boot
- Make sure main.py is uploaded
- Check for syntax errors in boot.py
- Use REPL to see error messages

### REPL not responding
- Ctrl+C to interrupt current program
- Ctrl+D to soft reset
- Disconnect and reconnect if frozen

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Command Palette | Cmd+Shift+P |
| Upload file | (Right-click menu) |
| Save file | Cmd+S |
| Open terminal | Ctrl+` |
| Stop program | Ctrl+C (in REPL) |
| Soft reset | Ctrl+D (in REPL) |

## Project-Specific Notes

- **config.py**: Contains WiFi credentials - be careful not to commit sensitive versions
- **main.py**: Runs automatically on boot
- **boot.py**: Runs before main.py, currently just prints boot info
- **Always test in REPL first** before making main.py auto-run on boot
