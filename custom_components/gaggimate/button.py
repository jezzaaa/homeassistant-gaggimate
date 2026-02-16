"""Button platform for GaggiMate."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GaggiMateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GaggiMate buttons."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    entities = [
        GaggiMateScaleScanButton(coordinator, entry),
        GaggiMateStartUpdateButton(coordinator, entry),
    ]
    
    async_add_entities(entities)


class GaggiMateButtonBase(CoordinatorEntity[GaggiMateCoordinator], ButtonEntity):
    """Base class for GaggiMate buttons."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        button_id: str,
        name: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{button_id}"
        self._attr_name = f"{entry.title} {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GaggiMate",
            "model": entry.data.get("model", "GaggiMate"),
            "hw_version": entry.data.get("hw_version"),
            "sw_version": coordinator.data.get("displayVersion"),
        }


class GaggiMateScaleScanButton(GaggiMateButtonBase):
    """Button to trigger Bluetooth scale scan."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the scale scan button."""
        super().__init__(coordinator, entry, "scale_scan", "Scan for Scales")
        self._attr_icon = "mdi:bluetooth-connect"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Triggering Bluetooth scale scan")
        success = await self.coordinator.scan_scales()
        if success:
            _LOGGER.info("Scale scan triggered successfully")
        else:
            _LOGGER.warning("Scale scan failed")


class GaggiMateStartUpdateButton(GaggiMateButtonBase):
    """Button to start OTA update."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the start update button."""
        super().__init__(coordinator, entry, "start_update", "Start Update")
        self._attr_icon = "mdi:update"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug("Starting OTA update")
        await self.coordinator.start_ota_update()
        _LOGGER.info("OTA update started")

    @property
    def available(self) -> bool:
        """Return if button is available."""
        # Only available if update is available and not currently updating
        update_available = (
            self.coordinator.data.get("displayUpdateAvailable", False)
            or self.coordinator.data.get("controllerUpdateAvailable", False)
        )
        is_updating = self.coordinator.data.get("updating", False)
        return super().available and update_available and not is_updating
