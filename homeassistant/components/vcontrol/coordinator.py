"""Data Coordinator for vcontrol API."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import now

from .viessmannApi import VControlAPI

_LOGGER = logging.getLogger(__name__)
SENSOR_REGISTRY_FILE = "vcontrol_sensors.json"
STORAGE_VERSION = 1


class HeatPumpDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching heat pump data from a single endpoint."""

    def __init__(self, hass: HomeAssistant, api: VControlAPI) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Heat Pump Data Coordinator",
            update_interval=timedelta(minutes=1),
        )
        self.api = api
        self.hass = hass
        self.stored_sensors: dict[str, Any] = {}
        self.store: Store = Store(hass, STORAGE_VERSION, SENSOR_REGISTRY_FILE)
        self._async_init = False

    async def async_setup(self):
        """Load stored sensor configurations and register listeners."""
        self.stored_sensors = await self.store.async_load() or {}
        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_START, self._handle_ha_start
        )
        self._async_init = True

    def _detect_api_changes(self, current_data: dict[str, Any]) -> dict[str, Any]:
        """Detect changes in API schema."""
        changes: dict[str, Any] = {"new": [], "removed": [], "modified": []}

        current_sensors = set(current_data.keys())
        stored_sensors = set(self.stored_sensors.keys())

        changes["new"] = list(current_sensors - stored_sensors)
        changes["removed"] = list(stored_sensors - current_sensors)

        return changes

    async def _handle_api_changes(self, changes: dict[str, Any]):
        """Handle detected API changes."""
        if any(changes.values()):
            # Notify users about changes
            self.hass.components.persistent_notification.create(
                f"VControl API Changes Detected:\n"
                f"New sensors: {', '.join(changes['new'])}\n"
                f"Removed sensors: {', '.join(changes['removed'])}",
                title="VControl API Changes",
            )

            # Register new sensors
            for sensor in changes["new"]:
                self.stored_sensors[sensor] = {
                    "name": sensor,
                    "first_seen": now().isoformat(),
                }

            # Store updated sensor registry
            await self.store.async_save(self.stored_sensors)

    async def _async_update_data(self):
        """Fetch data from the heat pump API."""
        _LOGGER.debug("Trying to update sensors from vcontrol API")
        try:
            data = await self.hass.async_add_executor_job(self.api.get_data)
            records = {}

            # Detect and handle API changes if initialization is complete
            if self._async_init:
                changes = self._detect_api_changes(data)
                await self._handle_api_changes(changes)

            # Process all available sensors (including new ones)
            for key, value in data.items():
                records[key] = value["raw"]

        except Exception as err:
            raise UpdateFailed(f"Error fetching data from vcontrol API: {err}") from err
        else:
            return records

    async def _handle_ha_start(self, _):
        """Handle Home Assistant start event."""
        # Force an immediate update to detect any API changes
        await self.async_refresh()
