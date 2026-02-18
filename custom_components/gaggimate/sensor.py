"""Sensor platform for GaggiMate."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfMass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MODE_MAP
from .coordinator import GaggiMateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GaggiMate sensors."""
    coordinator: GaggiMateCoordinator = entry.runtime_data
    
    entities = [
        GaggiMateTemperatureSensor(coordinator, entry, "current_temperature", "Current Temperature", "ct"),
        GaggiMateTemperatureSensor(coordinator, entry, "target_temperature", "Target Temperature", "tt"),
        GaggiMatePressureSensor(coordinator, entry, "current_pressure", "Current Pressure", "pr"),
        GaggiMatePressureSensor(coordinator, entry, "target_pressure", "Target Pressure", "pt"),
        GaggiMateWeightSensor(coordinator, entry, "current_weight", "Current Weight", "cw"),
        GaggiMateWeightSensor(coordinator, entry, "target_weight", "Target Weight", "tw"),
        GaggiMateFlowSensor(coordinator, entry),
        GaggiMateModeSensor(coordinator, entry),
        GaggiMateProfileSensor(coordinator, entry),
        GaggiMateVersionSensor(coordinator, entry, "display_version", "Display Version", "displayVersion"),
        GaggiMateVersionSensor(coordinator, entry, "controller_version", "Controller Version", "controllerVersion"),
        GaggiMateVersionSensor(coordinator, entry, "latest_version", "Latest Version", "latestVersion"),
        GaggiMateFilesystemSensor(coordinator, entry, "filesystem_total", "Filesystem Total", "spiffsTotal"),
        GaggiMateFilesystemSensor(coordinator, entry, "filesystem_used", "Filesystem Used", "spiffsUsed"),
        GaggiMateFilesystemSensor(coordinator, entry, "filesystem_free", "Filesystem Free", "spiffsFree"),
        GaggiMateFilesystemPercentSensor(coordinator, entry),
        GaggiMateUpdateProgressSensor(coordinator, entry),
    ]
    
    async_add_entities(entities)


class GaggiMateSensorBase(CoordinatorEntity[GaggiMateCoordinator], SensorEntity):
    """Base class for GaggiMate sensors."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
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


class GaggiMateTemperatureSensor(GaggiMateSensorBase):
    """Temperature sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, entry, sensor_id, name)
        self._data_key = data_key
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._data_key)


class GaggiMatePressureSensor(GaggiMateSensorBase):
    """Pressure sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the pressure sensor."""
        super().__init__(coordinator, entry, sensor_id, name)
        self._data_key = data_key
        self._attr_icon = "mdi:gauge"
        self._attr_native_unit_of_measurement = "bar"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 2

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._data_key)
        if value is not None:
            return round(value, 2)
        return None


class GaggiMateWeightSensor(GaggiMateSensorBase):
    """Weight sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the weight sensor."""
        super().__init__(coordinator, entry, sensor_id, name)
        self._data_key = data_key
        self._attr_icon = "mdi:weight-gram"
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._data_key)


class GaggiMateFlowSensor(GaggiMateSensorBase):
    """Flow rate sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the flow sensor."""
        super().__init__(coordinator, entry, "flow_rate", "Flow Rate")
        self._attr_icon = "mdi:water"
        self._attr_native_unit_of_measurement = "ml/s"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("fl")


class GaggiMateModeSensor(GaggiMateSensorBase):
    """Mode sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the mode sensor."""
        super().__init__(coordinator, entry, "mode", "Mode")
        self._attr_icon = "mdi:state-machine"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        mode_num = self.coordinator.data.get("m")
        if mode_num is not None:
            return MODE_MAP.get(mode_num, "Unknown")
        return None


class GaggiMateProfileSensor(GaggiMateSensorBase):
    """Profile sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the profile sensor."""
        super().__init__(coordinator, entry, "profile", "Profile")
        self._attr_icon = "mdi:coffee"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("p")


class GaggiMateVersionSensor(GaggiMateSensorBase):
    """Version sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the version sensor."""
        super().__init__(coordinator, entry, sensor_id, name)
        self._data_key = data_key
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._data_key)
        if value and isinstance(value, str):
            # Remove "v" prefix if present for consistency
            return value.lstrip("v")
        return value


class GaggiMateFilesystemSensor(GaggiMateSensorBase):
    """Filesystem sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        name: str,
        data_key: str,
    ) -> None:
        """Initialize the filesystem sensor."""
        super().__init__(coordinator, entry, sensor_id, name)
        self._data_key = data_key
        self._attr_icon = "mdi:harddisk"
        self._attr_native_unit_of_measurement = "MB"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        bytes_value = self.coordinator.data.get(self._data_key)
        if bytes_value is not None:
            return round(bytes_value / (1024 * 1024), 2)
        return None


class GaggiMateFilesystemPercentSensor(GaggiMateSensorBase):
    """Filesystem percentage sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the filesystem percent sensor."""
        super().__init__(coordinator, entry, "filesystem_used_percent", "Filesystem Used")
        self._attr_icon = "mdi:harddisk"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get("spiffsUsedPct")


class GaggiMateUpdateProgressSensor(GaggiMateSensorBase):
    """Update progress sensor for GaggiMate."""

    def __init__(
        self,
        coordinator: GaggiMateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the update progress sensor."""
        super().__init__(coordinator, entry, "update_progress", "Update Progress")
        self._attr_icon = "mdi:progress-download"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data.get("updating"):
            return self.coordinator.data.get("progress", 0)
        return None
