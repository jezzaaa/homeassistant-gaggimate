"""Binary sensor platform for GaggiMate."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up GaggiMate binary sensors."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    entities = [
        GaggiMateUpdateAvailableSensor(coordinator, entry, "display_update_available", "Display Update Available", "displayUpdateAvailable"),
        GaggiMateUpdateAvailableSensor(coordinator, entry, "controller_update_available", "Controller Update Available", "controllerUpdateAvailable"),
        GaggiMateUpdatingSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class GaggiMateBinarySensorBase(CoordinatorEntity[GaggiMateCoordinator], BinarySensorEntity):
    """Base class for GaggiMate binary sensors."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{sensor_id}"
        self._attr_name = f"{entry.title} {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GaggiMate",
            "model": entry.data.get("model", "GaggiMate"),
            "hw_version": entry.data.get("hw_version"),
            "sw_version": coordinator.data.get("displayVersion"),
        }


class GaggiMateUpdateAvailableSensor(GaggiMateBinarySensorBase):
    """Update available binary sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the update available sensor."""
        super().__init__(coordinator, entry, sensor_id, name)
        self._data_key = data_key
        self._attr_device_class = BinarySensorDeviceClass.UPDATE

    @property
    def is_on(self) -> bool:
        """Return true if update is available."""
        return self.coordinator.data.get(self._data_key, False)


class GaggiMateUpdatingSensor(GaggiMateBinarySensorBase):
    """Updating binary sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the updating sensor."""
        super().__init__(coordinator, entry, "is_updating", "Is Updating")
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_icon = "mdi:update"

    @property
    def is_on(self) -> bool:
        """Return true if device is updating."""
        return self.coordinator.data.get("updating", False)
