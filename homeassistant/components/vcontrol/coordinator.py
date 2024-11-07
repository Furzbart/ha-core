"""Data Coordinator for vcontrol API."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .viessmannApi import VControlAPI  # Import the API client

_LOGGER = logging.getLogger(__name__)


class HeatPumpDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching heat pump data from a single endpoint."""

    def __init__(self, hass: HomeAssistant, api: VControlAPI) -> None:
        """Initialize the coordinator with the Home Assistant instance and API client."""
        super().__init__(
            hass,
            _LOGGER,
            name="Heat Pump Data Coordinator",
            update_interval=timedelta(minutes=1),  # Fetch data every 5 minutes
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from the heat pump API."""
        _LOGGER.log(level=20, msg="Trying to update sensors...")
        try:
            # Fetch data from the API using the `HeatPumpAPI` client
            data = await self.hass.async_add_executor_job(self.api.get_data)
            records = {}

            for key, value in self.hass.data[DOMAIN]["sensors"].items():
                records[key] = data[value["name"]]["raw"]

        except Exception as err:
            raise UpdateFailed(f"Error fetching data from vcontrol API: {err}") from err

        return records
