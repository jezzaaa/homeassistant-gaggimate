"""Constants for the GaggiMate integration."""

DOMAIN = "gaggimate"
DEFAULT_NAME = "GaggiMate"
DEFAULT_PORT = 80

# mDNS hostname
MDNS_HOSTNAME = "gaggimate.local"

# WebSocket configuration
WS_PATH = "/ws"
WS_TIMEOUT = 10
RECONNECT_INTERVAL = 30

# Update intervals
SCAN_INTERVAL = 5
OTA_REFRESH_INTERVAL = 900  # 15 minutes

# Platforms
PLATFORMS = ["sensor", "binary_sensor", "switch", "select", "button", "update"]

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

# WebSocket message types
WS_REQ_OTA_SETTINGS = "req:ota-settings"
WS_RES_OTA_SETTINGS = "res:ota-settings"
WS_REQ_OTA_START = "req:ota-start"
WS_EVT_STATUS = "evt:status"
WS_REQ_CHANGE_MODE = "req:change-mode"
WS_REQ_PROFILES_LIST = "req:profiles:list"
WS_RES_PROFILES_LIST = "res:profiles:list"
WS_REQ_PROFILES_SELECT = "req:profiles:select"
WS_RES_PROFILES_SELECT = "res:profiles:select"

# HTTP endpoints
API_SCALES_SCAN = "/api/scales/scan"

# Config entry keys
CONF_MODEL = "model"
CONF_HW_VERSION = "hw_version"
