"""Constants for the GaggiMate integration."""

DOMAIN = "gaggimate"
DEFAULT_NAME = "GaggiMate"

# mDNS hostname
MDNS_HOSTNAME = "gaggimate.local"

# WebSocket configuration
WS_PATH = "/ws"
WS_TIMEOUT = 10
RECONNECT_INTERVAL = 30

# Update intervals
OTA_REFRESH_INTERVAL = 900  # 15 minutes

# API paths
API_SETTINGS_PATH = "/api/settings"

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "switch", "select", "button", "number", "update"]

# Mode constants
MODE_STANDBY = 0
MODE_BREW = 1
MODE_STEAM = 2
MODE_WATER = 3
MODE_GRIND = 4

MODE_MAP = {
    0: "Standby",
    1: "Brew",
    2: "Steam",
    3: "Water",
    4: "Grind"
}

MODE_REVERSE_MAP = {v: k for k, v in MODE_MAP.items()}

# Config entry keys
CONF_MODEL = "model"
CONF_HW_VERSION = "hw_version"
