# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.3-beta.3] - 2026-02-21

**Pre-release for testing**

### Fixed
- Dashboard card now loads Lit from Home Assistant's bundled frontend instead of external CDN (unpkg.com)
- Fixes card not rendering on Nabu Casa (remote access) and mobile devices due to Content Security Policy restrictions

## [0.2.3-beta.2] - 2026-02-21

**Pre-release for testing**

### Added
- **Number Entities** for automation-friendly control
  - Target Temperature number entity (0-160°C) - set exact temperature via automations
  - Target Pressure number entity (0-15 bar) - set exact pressure via automations
  - Target Weight number entity (5-250g) - set exact weight via automations
  - Uses HTTP REST API for direct value setting
  - Ranges match firmware limits exactly
- **Temperature Control Buttons** on dashboard card
  - Plus (+) and minus (-) buttons on temperature dial
  - Buttons enabled only in Brew mode (as per firmware requirements)
  - Visual feedback with hover effects and disabled states
- **Custom Services** for temperature adjustment
  - `gaggimate.raise_temperature` - increase temperature by 1°C
  - `gaggimate.lower_temperature` - decrease temperature by 1°C
  - Services documented in services.yaml for automation UI

### Changed
- Coordinator now supports both WebSocket (for +/- buttons) and HTTP REST API (for number entities)
- Dashboard card temperature dial now includes interactive control buttons

## [0.2.3-beta.1] - 2026-02-21

**Pre-release for testing**

### Changed
- Improved code quality by removing unused constants and replacing rarely-used constants with string literals for better readability
- Removed 7 unused constants from const.py (WS_REQ_OTA_START, WS_REQ_CHANGE_MODE, WS_REQ_PROFILES_LIST, WS_REQ_PROFILES_SELECT, WS_RES_PROFILES_SELECT, DEFAULT_PORT, SCAN_INTERVAL)
- Replaced WebSocket message type constants with inline strings in coordinator.py for improved code clarity (constants used only 1-2 times each)
- Kept MODE constants (MODE_STANDBY through MODE_GRIND) as they provide meaningful documentation for numeric mode values

## [0.2.2] - 2026-02-20

### Added
- **Custom Lovelace Dashboard Card** - Beautiful unified card for complete machine control
  - Visual configuration editor with device selection and display options
  - Real-time temperature and pressure dials with target indicators
  - Quick-access mode selector buttons (Standby, Brew, Steam, Water, Grind)
  - Profile selector dropdown
  - Current and target weight display
  - Responsive design that adapts to Home Assistant themes
  - Automatically registered as a Lovelace resource
- Frontend resource registration for HACS distribution
- Dashboard card screenshot in README

### Changed
- Updated codeowners from @jpl to @jezzaaa in manifest.json
- Improved README with prominent dashboard card section and screenshot

### Fixed
- Frontend resource registration now uses correct StaticPathConfig dataclass
- Lovelace resource properly registered with add_extra_js_url
- Dashboard card now imports Lit from CDN for reliable loading across HA versions

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
