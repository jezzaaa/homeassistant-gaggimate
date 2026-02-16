"""Update platform for GaggiMate."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
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
    """Set up GaggiMate update entity."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    async_add_entities([GaggiMateUpdateEntity(coordinator, entry)])


class GaggiMateUpdateEntity(CoordinatorEntity[GaggiMateCoordinator], UpdateEntity):
    """Update entity for GaggiMate firmware."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the update entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_firmware_update"
        self._attr_name = f"{entry.title} Firmware"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GaggiMate",
            "model": entry.data.get("model", "GaggiMate"),
            "hw_version": entry.data.get("hw_version"),
            "sw_version": coordinator.data.get("displayVersion"),
        }

    @property
    def installed_version(self) -> str | None:
        """Return the installed version."""
        # Use display version as primary, fallback to controller version
        version = self.coordinator.data.get("displayVersion") or self.coordinator.data.get("controllerVersion")
        if version and isinstance(version, str):
            # Remove "v" prefix if present for consistency
            return version.lstrip("v")
        return version

    @property
    def latest_version(self) -> str | None:
        """Return the latest available version."""
        version = self.coordinator.data.get("latestVersion")
        if version and isinstance(version, str):
            # Remove "v" prefix if present for consistency
            return version.lstrip("v")
        return version

    @property
    def update_available(self) -> bool:
        """Return if update is available."""
        display_update = self.coordinator.data.get("displayUpdateAvailable", False)
        controller_update = self.coordinator.data.get("controllerUpdateAvailable", False)
        return display_update or controller_update

    @property
    def in_progress(self) -> bool | int:
        """Return if update is in progress."""
        if self.coordinator.data.get("updating", False):
            progress = self.coordinator.data.get("progress", 0)
            return progress
        return False

    @property
    def release_summary(self) -> str | None:
        """Return the release summary."""
        if self.update_available:
            display_update = self.coordinator.data.get("displayUpdateAvailable", False)
            controller_update = self.coordinator.data.get("controllerUpdateAvailable", False)
            
            updates = []
            if display_update:
                updates.append("Display")
            if controller_update:
                updates.append("Controller")
            
            return f"Update available for: {', '.join(updates)}"
        return None

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        """Install an update."""
        _LOGGER.info("Starting firmware update to version %s", version or self.latest_version)
        await self.coordinator.start_ota_update()
