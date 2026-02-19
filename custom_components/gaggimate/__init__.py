"""The GaggiMate integration."""
from __future__ import annotations

import logging

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS
from .coordinator import GaggiMateCoordinator

_LOGGER = logging.getLogger(__name__)

type GaggiMateConfigEntry = ConfigEntry[GaggiMateCoordinator]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the GaggiMate component."""
    # Register the Lovelace card
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url_path=f"/hacsfiles/{DOMAIN}/gaggimate-card.js",
                path=hass.config.path(f"custom_components/{DOMAIN}/www/gaggimate-card.js"),
                cache_headers=True,
            )
        ]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: GaggiMateConfigEntry) -> bool:
    """Set up GaggiMate from a config entry."""
    host = entry.data[CONF_HOST]
    
    coordinator = GaggiMateCoordinator(hass, host)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Error connecting to GaggiMate at %s: %s", host, err)
        raise ConfigEntryNotReady from err
    
    entry.runtime_data = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GaggiMateConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinator = entry.runtime_data
        await coordinator.async_shutdown()
    
    return unload_ok
