"""The GaggiMate integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS
from .coordinator import GaggiMateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_RAISE_TEMPERATURE = "raise_temperature"
SERVICE_LOWER_TEMPERATURE = "lower_temperature"

SERVICE_SCHEMA = vol.Schema({
    vol.Required("device_id"): cv.string,
})

type GaggiMateConfigEntry = ConfigEntry[GaggiMateCoordinator]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

CARD_URL = f"/hacsfiles/{DOMAIN}/gaggimate-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the GaggiMate component."""
    # Register the static path for the Lovelace card
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url_path=CARD_URL,
                path=hass.config.path(f"custom_components/{DOMAIN}/www/gaggimate-card.js"),
                cache_headers=False,
            )
        ]
    )

    # Register the card as a Lovelace resource in storage so it loads via
    # Nabu Casa, the Android app, and any other remote access method.
    # add_extra_js_url() only works for direct local HA access.
    hass.async_create_task(_async_register_lovelace_resource(hass))

    return True


async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
    """Add the dashboard card to Lovelace resources if not already present."""
    try:
        lovelace = hass.data.get("lovelace")
        if lovelace is None:
            _LOGGER.warning("Lovelace not available, cannot register GaggiMate card resource")
            return

        resources = lovelace.resources

        # Ensure resources are loaded from storage
        if not resources.loaded:
            await resources.async_load()

        # Check if our resource is already registered
        existing_urls = {item.get("url") for item in resources.async_items()}
        if CARD_URL in existing_urls:
            _LOGGER.debug("GaggiMate card resource already registered")
            return

        # Add the resource
        await resources.async_create_item({"res_type": "module", "url": CARD_URL})
        _LOGGER.info("Registered GaggiMate dashboard card as Lovelace resource: %s", CARD_URL)

    except Exception as err:  # noqa: BLE001
        _LOGGER.error("Failed to register GaggiMate card as Lovelace resource: %s", err)


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
    
    # Register services
    async def async_raise_temperature(call: ServiceCall) -> None:
        """Handle raise temperature service call."""
        device_id = call.data["device_id"]
        # Find the coordinator for this device
        for config_entry in hass.config_entries.async_entries(DOMAIN):
            if config_entry.entry_id in device_id or device_id in config_entry.title.lower().replace(" ", "_"):
                coordinator = config_entry.runtime_data
                await coordinator.raise_temperature()
                _LOGGER.debug("Raised temperature for device %s", device_id)
                return
        _LOGGER.error("Device %s not found", device_id)
    
    async def async_lower_temperature(call: ServiceCall) -> None:
        """Handle lower temperature service call."""
        device_id = call.data["device_id"]
        # Find the coordinator for this device
        for config_entry in hass.config_entries.async_entries(DOMAIN):
            if config_entry.entry_id in device_id or device_id in config_entry.title.lower().replace(" ", "_"):
                coordinator = config_entry.runtime_data
                await coordinator.lower_temperature()
                _LOGGER.debug("Lowered temperature for device %s", device_id)
                return
        _LOGGER.error("Device %s not found", device_id)
    
    # Register services only once (check if not already registered)
    if not hass.services.has_service(DOMAIN, SERVICE_RAISE_TEMPERATURE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RAISE_TEMPERATURE,
            async_raise_temperature,
            schema=SERVICE_SCHEMA,
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_LOWER_TEMPERATURE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LOWER_TEMPERATURE,
            async_lower_temperature,
            schema=SERVICE_SCHEMA,
        )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GaggiMateConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        coordinator = entry.runtime_data
        await coordinator.async_shutdown()
        
        # Unregister services if this is the last entry
        if len(hass.config_entries.async_entries(DOMAIN)) == 1:
            hass.services.async_remove(DOMAIN, SERVICE_RAISE_TEMPERATURE)
            hass.services.async_remove(DOMAIN, SERVICE_LOWER_TEMPERATURE)
    
    return unload_ok
