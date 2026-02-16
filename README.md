# GaggiMate Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/jpl/homeassistant-gaggimate.svg)](https://github.com/jpl/homeassistant-gaggimate/releases)
[![License](https://img.shields.io/github/license/jpl/homeassistant-gaggimate.svg)](LICENSE)

A custom Home Assistant integration for GaggiMate espresso machines with full WebSocket support, real-time monitoring, and comprehensive control capabilities.

## Features

### 🔍 Automatic Discovery
- Discovers GaggiMate devices on the local network via mDNS (hostname: `gaggimate.local`)
- Automatic device information retrieval (model, hardware version, firmware versions)
- User-friendly setup flow with device confirmation

### 📊 Comprehensive Monitoring (17 Sensors)
- **Temperature**: Current and target temperature (°C)
- **Pressure**: Current and target pressure (bar)
- **Weight**: Current and target weight (grams)
- **Flow Rate**: Real-time flow measurement (ml/s)
- **Mode**: Current operating mode (Standby/Brew/Steam/Water/Grind)
- **Profile**: Active brewing profile
- **Firmware**: Display, controller, and latest available versions
- **Filesystem**: Total, used, free space and usage percentage
- **Update Progress**: Real-time OTA update progress

### 🎛️ Full Device Control
- **Power Switch**: Turn device on (brew mode) or off (standby)
- **Mode Selector**: Switch between Standby, Brew, Steam, Water, and Grind modes
- **Profile Selector**: Choose from available brewing profiles
- **Scale Scan Button**: Trigger Bluetooth scale scanning
- **Update Button**: Start firmware updates when available

### 🔄 Real-time Updates
- WebSocket-based push updates for instant sensor changes
- Automatic reconnection on connection loss
- Periodic OTA settings refresh (every 15 minutes)

### 🔧 Firmware Management
- Update entity showing installed vs. latest firmware versions
- One-click firmware updates with progress tracking
- Separate tracking for display and controller updates

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the **three dots** in the top right corner
4. Select **Custom repositories**
5. Add this repository URL: `https://github.com/jpl/homeassistant-gaggimate`
6. Select **Integration** as the category
7. Click **Install**
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/jpl/homeassistant-gaggimate/releases)
2. Extract the `custom_components/gaggimate` directory to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"GaggiMate"**
4. Follow the setup wizard:
   - The integration will attempt to discover your device automatically
   - If not found, enter the hostname or IP address manually (default: `gaggimate.local`)
   - Confirm the device information (model, hardware version, firmware)
   - Optionally edit the device name

## Entities Created

### Sensors
- `sensor.gaggimate_current_temperature`
- `sensor.gaggimate_target_temperature`
- `sensor.gaggimate_current_pressure`
- `sensor.gaggimate_target_pressure`
- `sensor.gaggimate_current_weight`
- `sensor.gaggimate_target_weight`
- `sensor.gaggimate_flow_rate`
- `sensor.gaggimate_mode`
- `sensor.gaggimate_profile`
- `sensor.gaggimate_display_version`
- `sensor.gaggimate_controller_version`
- `sensor.gaggimate_latest_version`
- `sensor.gaggimate_filesystem_total`
- `sensor.gaggimate_filesystem_used`
- `sensor.gaggimate_filesystem_free`
- `sensor.gaggimate_filesystem_used_percent`
- `sensor.gaggimate_update_progress` (only visible during updates)

### Binary Sensors
- `binary_sensor.gaggimate_display_update_available`
- `binary_sensor.gaggimate_controller_update_available`
- `binary_sensor.gaggimate_is_updating`

### Controls
- `switch.gaggimate_power` - Power on/off
- `select.gaggimate_mode` - Mode selection
- `select.gaggimate_profile` - Profile selection
- `button.gaggimate_scan_for_scales` - Trigger Bluetooth scale scan
- `button.gaggimate_start_update` - Start firmware update
- `update.gaggimate_firmware` - Firmware update entity

## Usage Examples

### Automation: Start Brewing at 7 AM
```yaml
automation:
  - alias: "Morning Coffee"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.gaggimate_power
```

### Automation: Notify When Update Available
```yaml
automation:
  - alias: "GaggiMate Update Available"
    trigger:
      - platform: state
        entity_id: binary_sensor.gaggimate_display_update_available
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "GaggiMate firmware update available!"
```

### Script: Switch to Steam Mode
```yaml
script:
  gaggimate_steam:
    sequence:
      - service: select.select_option
        target:
          entity_id: select.gaggimate_mode
        data:
          option: "Steam"
```

## Technical Details

### WebSocket API
The integration communicates with the GaggiMate device via WebSocket at `ws://<device_ip>/ws`:
- **Status Updates**: Real-time push updates for all sensor values
- **OTA Settings**: Device information and firmware status
- **Profile Management**: List and select brewing profiles
- **Mode Control**: Change operating modes
- **Firmware Updates**: Trigger and monitor OTA updates

### Architecture
- **DataUpdateCoordinator**: Efficient data management with automatic updates
- **Config Flow**: User-friendly setup with mDNS discovery
- **WebSocket**: Real-time bidirectional communication
- **Auto-reconnection**: Robust connection handling with automatic recovery

## Troubleshooting

### Device Not Discovered
- Ensure your GaggiMate device is on the same network as Home Assistant
- Try entering the IP address manually instead of using `gaggimate.local`
- Check that mDNS/Bonjour is working on your network

### Connection Issues
- Verify the device is powered on and connected to WiFi
- Check Home Assistant logs for detailed error messages
- Ensure no firewall is blocking WebSocket connections

### Entities Not Updating
- Check the WebSocket connection status in the logs
- Restart the integration from the Integrations page
- Verify the device firmware is up to date

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/jpl/homeassistant-gaggimate/issues) page
2. Create a new issue with detailed information about your problem
3. Include relevant logs from Home Assistant

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Based on the [GaggiMate project](https://github.com/jniebuhr/gaggimate) by jniebuhr
- Integration developed for the Home Assistant community

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by GaggiMate.
