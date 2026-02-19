# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1-beta.5] - 2026-02-20

**Pre-release for testing**

### Fixed
- Fixed frontend resource registration to use StaticPathConfig dataclass instead of dict (was causing 'dict' object has no attribute 'url_path' error)

## [0.2.1-beta.4] - 2026-02-19

**Pre-release for testing**

### Fixed
- Fixed frontend resource registration to use correct async_register_static_paths API (was causing AttributeError on integration load)

## [0.2.1-beta.3] - 2026-02-19

**Pre-release for testing**

### Added
- Custom Lovelace dashboard card (gaggimate-card.js) for unified machine control
- Visual card editor with device selection and display options
- Real-time temperature and pressure dials with target indicators
- Mode selector buttons (Standby, Brew, Steam, Water, Grind)
- Profile selector dropdown
- Current and target weight display
- Frontend resource registration for HACS distribution

### Changed
- Updated codeowners in manifest.json

## [0.2.1-beta.2] - 2026-02-19

**Pre-release for testing**

### Fixed
- Update progress sensor now correctly shows "None" when no update is in progress (removed incorrect available() override that was causing "Unavailable" state)

## [0.2.1-beta.1] - 2026-02-19

**Pre-release for testing**

### Fixed
- Update progress now correctly shows as "Not applicable" when no update is in progress (instead of "Unavailable")

## [0.2.0] - 2026-02-19

### Added
- INFO-level logging for WebSocket reconnection attempts and successes
- Timeout protection on WebSocket send operations to prevent hanging
- Enhanced profiles list logging with summary information
- Pressure sensor now displays with 2 decimal places precision

### Changed
- Improved WebSocket connection state visibility with better logging
- Version strings now strip "v" prefix for consistency across sensors and update entity
- Simplified configuration to manual setup only (removed non-functional mDNS discovery)

### Fixed
- WebSocket send operations can no longer hang indefinitely on unresponsive connections
- Pressure sensor values now consistently rounded to 2 decimal places

## [0.1.0] - Initial Release

### Added
- Initial release of GaggiMate Home Assistant integration
- Support for temperature, pressure, weight, and flow sensors
- Mode and profile selection
- Bluetooth scale scanning
- OTA firmware updates
- WebSocket-based real-time communication
