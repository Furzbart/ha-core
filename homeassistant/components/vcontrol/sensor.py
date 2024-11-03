"""Platform for sensor integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, SENSORS


def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up VControl sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [VControlSensor(coordinator, sensor_key) for sensor_key in SENSORS]

    async_add_entities(sensors, update_before_add=True)


class VControlSensor(CoordinatorEntity, SensorEntity):
    """vcontrol Sensor representation."""

    def __init__(
        self, coordinator: DataUpdateCoordinator[dict[str, Any]], sensor_key
    ) -> None:
        """Stfu about docstring pls."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._type = SENSORS[sensor_key]["type"]
        self._name = SENSORS[sensor_key]["name"]
        self._unit = SENSORS[sensor_key]["unit"]

    @property
    def name(self):
        """The friggin name."""
        return self._name

    @property
    def state(self):
        """Sensor State."""
        return self.coordinator.data.get(self._sensor_key)

    @property
    def unit_of_measurement(self):
        """Unit."""
        return self._unit

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
