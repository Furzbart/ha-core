"""API handler for vcontrol API."""

import logging

import requests

from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class VControlAPI:
    """Handles connection and updates from/to vcontrol API."""

    def __init__(self, host, port="5000", base_url="/api/vcontrol"):
        """Useless docstring."""
        self._base_url = base_url
        self._host = host
        self._port = port

    def get_data(self):
        """Pull data from vcontrol API."""
        try:
            res = requests.get(
                f"{self._host}:{self._port}{self._base_url}/status", timeout=15
            )
            res.raise_for_status()
            res = requests.get(
                f"{self._host}:{self._port}{self._base_url}/commands/all", timeout=15
            )
            res.raise_for_status()
            return res.json()
        except requests.HTTPError:
            _LOGGER.log(
                level=20,
                msg="Couldn't fetch API update! Check connectivity to vcontrol API.",
            )
            return None
        except requests.exceptions.Timeout:
            _LOGGER.log(level=20, msg="Connection to vcontrol API timed out!")
            return None

    async def async_get_available_sensors(self, hass):
        """Get all available sensors from vcontrol API."""

        session = async_get_clientsession(hass)
        async with session.get(
            f"{self._host}:{self._port}{self._base_url}/commands"
        ) as res:
            data = await res.json()
            _LOGGER.log(
                level=20, msg="Got response from vcontrol. Available sensors fetched."
            )
            return {f"vcontrol_{item['name']}": item for item in data}
