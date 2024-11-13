"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, UNIQUE_ID
from .coordinator import HeatPumpDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VControl sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    sensor_collection = hass.data[DOMAIN]["sensors"]

    sensors = [
        VControlSensor(
            coordinator=coordinator,
            key=sensor_key,
            name=sensor_collection[sensor_key]["name"],
            type=sensor_collection[sensor_key].get("measurement", None),
            unit=sensor_collection[sensor_key].get("unit", None),
        )
        for sensor_key in sensor_collection
    ]
    await async_add_entities(sensors, update_before_add=True)  # type:ignore[func-returns-value]


class VControlSensor(CoordinatorEntity, SensorEntity):
    """vcontrol Sensor representation."""

    def __init__(
        self,
        coordinator: HeatPumpDataCoordinator,
        key,
        type,
        name,
        unit,
    ) -> None:
        """Stfu about docstring pls."""
        super().__init__(coordinator)
        self._sensor_key = key
        self._name = name
        self._type = type
        self._unit = unit
        self._device_id = UNIQUE_ID
        self._unique_id = f"{UNIQUE_ID}_{key}"

    @property
    def name(self) -> str:
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

    @property
    def device_info(self) -> DeviceInfo:
        """Device info."""
        return {
            "identifiers": {(DOMAIN, UNIQUE_ID)},
            "name": "V200-A",
            "model": "Vitocal 200-A",
            "manufacturer": "Viessmann",
        }

    @property
    def unique_id(self) -> str:
        """Unique id."""
        return self._unique_id

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
