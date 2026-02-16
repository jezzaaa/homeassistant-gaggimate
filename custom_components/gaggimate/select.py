"""Select platform for GaggiMate."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_MAP, MODE_REVERSE_MAP
from .coordinator import GaggiMateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GaggiMate select entities."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    # Request profiles list on setup
    await coordinator.request_profiles_list()
    
    entities = [
        GaggiMateModeSelect(coordinator, entry),
        GaggiMateProfileSelect(coordinator, entry),
    ]
    
    async_add_entities(entities)


class GaggiMateSelectBase(CoordinatorEntity[GaggiMateCoordinator], SelectEntity):
    """Base class for GaggiMate select entities."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        select_id: str,
        name: str,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{select_id}"
        self._attr_name = f"{entry.title} {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GaggiMate",
            "model": entry.data.get("model", "GaggiMate"),
            "hw_version": entry.data.get("hw_version"),
            "sw_version": coordinator.data.get("displayVersion"),
        }


class GaggiMateModeSelect(GaggiMateSelectBase):
    """Mode selector for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the mode selector."""
        super().__init__(coordinator, entry, "mode_select", "Mode")
        self._attr_icon = "mdi:state-machine"
        self._attr_options = list(MODE_MAP.values())

    @property
    def current_option(self) -> str | None:
        """Return the current mode."""
        mode_num = self.coordinator.data.get("m")
        if mode_num is not None:
            return MODE_MAP.get(mode_num)
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the mode."""
        mode_num = MODE_REVERSE_MAP.get(option)
        if mode_num is not None:
            _LOGGER.debug("Changing mode to %s (%d)", option, mode_num)
            await self.coordinator.change_mode(mode_num)
        else:
            _LOGGER.error("Invalid mode option: %s", option)


class GaggiMateProfileSelect(GaggiMateSelectBase):
    """Profile selector for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the profile selector."""
        super().__init__(coordinator, entry, "profile_select", "Profile")
        self._attr_icon = "mdi:coffee"

    @property
    def options(self) -> list[str]:
        """Return available profile options."""
        # Filter out utility profiles and return labels
        profiles = [
            p.get("label", p.get("id", "Unknown"))
            for p in self.coordinator.profiles
            if not p.get("utility", False)
        ]
        return profiles if profiles else ["No profiles available"]

    @property
    def current_option(self) -> str | None:
        """Return the current profile."""
        return self.coordinator.data.get("p")

    async def async_select_option(self, option: str) -> None:
        """Select a profile."""
        # Find profile by label
        profile = None
        for p in self.coordinator.profiles:
            if p.get("label") == option or p.get("id") == option:
                profile = p
                break
        
        if profile:
            profile_id = profile.get("id")
            _LOGGER.debug("Selecting profile %s (ID: %s)", option, profile_id)
            await self.coordinator.select_profile(profile_id)
        else:
            _LOGGER.error("Profile not found: %s", option)
            # Refresh profiles list
            await self.coordinator.request_profiles_list()
