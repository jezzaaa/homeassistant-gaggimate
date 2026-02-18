# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-beta.1] - 2026-02-18

**Pre-release for testing**

### Added
- GaggiMate-specific mDNS service type (`_gaggimate._tcp.local.`) to prevent false matches with non-GaggiMate devices
- TXT record validation during mDNS discovery to verify device type is "espresso_machine"
- Firmware version logging during device discovery
- New abort reason "not_gaggimate" for rejected non-GaggiMate devices during discovery
- New abort reason "unknown" for unexpected errors during device discovery
- INFO-level logging for WebSocket reconnection attempts and successes
- Timeout protection on WebSocket send operations
- Enhanced profiles list logging with summary information

### Changed
- Improved WebSocket connection state visibility with better logging
- Updated translation files (strings.json, translations/en.json) with new abort reasons

### Fixed
- WebSocket send operations can no longer hang indefinitely on unresponsive connections

## [0.1.0] - Initial Release

### Added
- Initial release of GaggiMate Home Assistant integration
- Support for temperature, pressure, weight, and flow sensors
- Mode and profile selection
- Bluetooth scale scanning
- OTA firmware updates
- WebSocket-based real-time communication
