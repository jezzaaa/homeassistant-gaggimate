"""Number platform for GaggiMate."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfPressure, UnitOfMass
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
    """Set up GaggiMate number entities."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    entities = [
        GaggiMateTargetTemperatureNumber(coordinator, entry),
        GaggiMateTargetPressureNumber(coordinator, entry),
        GaggiMateTargetWeightNumber(coordinator, entry),
    ]
    
    async_add_entities(entities)


class GaggiMateNumberBase(CoordinatorEntity[GaggiMateCoordinator], NumberEntity):
    """Base class for GaggiMate number entities."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        number_id: str,
        name: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{number_id}"
        self._attr_name = f"{entry.title} {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "GaggiMate",
            "model": entry.data.get("model", "GaggiMate"),
            "hw_version": entry.data.get("hw_version"),
            "sw_version": coordinator.data.get("displayVersion"),
        }
        self._attr_mode = NumberMode.BOX


class GaggiMateTargetTemperatureNumber(GaggiMateNumberBase):
    """Number entity for target temperature."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the target temperature number."""
        super().__init__(coordinator, entry, "target_temperature", "Target Temperature")
        self._attr_icon = "mdi:thermometer"
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 160.0
        self._attr_native_step = 0.5

    @property
    def native_value(self) -> float | None:
        """Return the current target temperature."""
        return self.coordinator.data.get("tt")

    async def async_set_native_value(self, value: float) -> None:
        """Set the target temperature."""
        await self.coordinator.set_target_temperature(value)


class GaggiMateTargetPressureNumber(GaggiMateNumberBase):
    """Number entity for target pressure."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the target pressure number."""
        super().__init__(coordinator, entry, "target_pressure", "Target Pressure")
        self._attr_icon = "mdi:gauge"
        self._attr_native_unit_of_measurement = UnitOfPressure.BAR
        self._attr_native_min_value = 0.0
        self._attr_native_max_value = 15.0
        self._attr_native_step = 0.1

    @property
    def native_value(self) -> float | None:
        """Return the current target pressure."""
        return self.coordinator.data.get("pt")

    async def async_set_native_value(self, value: float) -> None:
        """Set the target pressure."""
        await self.coordinator.set_target_pressure(value)


class GaggiMateTargetWeightNumber(GaggiMateNumberBase):
    """Number entity for target weight."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the target weight number."""
        super().__init__(coordinator, entry, "target_weight", "Target Weight")
        self._attr_icon = "mdi:weight-gram"
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_native_min_value = 5.0
        self._attr_native_max_value = 250.0
        self._attr_native_step = 0.5

    @property
    def native_value(self) -> float | None:
        """Return the current target weight."""
        return self.coordinator.data.get("tw")

    async def async_set_native_value(self, value: float) -> None:
        """Set the target weight."""
        await self.coordinator.set_target_weight(value)
