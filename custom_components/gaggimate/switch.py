"""Switch platform for GaggiMate."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_STANDBY, MODE_BREW
from .coordinator import GaggiMateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GaggiMate switch."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    async_add_entities([GaggiMatePowerSwitch(coordinator, entry)])


class GaggiMatePowerSwitch(CoordinatorEntity[GaggiMateCoordinator], SwitchEntity):
    """Power switch for GaggiMate.
    
    CRITICAL BEHAVIOR:
    - Switch ON → Device enters brew mode (mode 1)
    - Switch OFF → Device enters standby (mode 0)
    - Mode Standby (0) → Switch shows OFF
    - Mode anything else (1-4) → Switch shows ON
    """

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_name = f"{entry.title} Power"
        self._attr_icon = "mdi:power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GaggiMate",
            "model": entry.data.get("model", "GaggiMate"),
            "hw_version": entry.data.get("hw_version"),
            "sw_version": coordinator.data.get("displayVersion"),
        }

    @property
    def is_on(self) -> bool:
        """Return true if device is on (not in standby mode)."""
        mode = self.coordinator.data.get("m", MODE_STANDBY)
        return mode != MODE_STANDBY

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on by setting it to brew mode."""
        _LOGGER.debug("Turning on GaggiMate (setting to brew mode)")
        await self.coordinator.change_mode(MODE_BREW)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off by setting it to standby mode."""
        _LOGGER.debug("Turning off GaggiMate (setting to standby mode)")
        await self.coordinator.change_mode(MODE_STANDBY)
