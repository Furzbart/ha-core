"""The Viessmann vcontrol integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, UNIQUE_ID
from .coordinator import HeatPumpDataCoordinator
from .viessmannApi import VControlAPI

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Viessmann vcontrol from a config entry."""

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, UNIQUE_ID)},
        manufacturer="Viessmann",
        model="Vitocal 200-A",
        name="V200-A",
    )

    vcontrol = VControlAPI(
        host=entry.data["host"],
        port=entry.data["port"],
        base_url=entry.data["path"],
    )

    coordinator = HeatPumpDataCoordinator(hass, vcontrol)

    sensors = await coordinator.api.async_get_available_sensors(hass)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    hass.data[DOMAIN]["sensors"] = sensors
    hass.data[DOMAIN]["unique_id"] = UNIQUE_ID

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
