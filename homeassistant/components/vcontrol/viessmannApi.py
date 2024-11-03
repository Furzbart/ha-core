"""API handler for vcontrol API."""

import logging

import requests

_LOGGER = logging.getLogger(__name__)


class VControlAPI:
    """Handles connection and updates from/to vcontrol API."""

    def __init__(self, base_url):
        """Useless docstring."""
        self._base_url = base_url

    def get_data(self):
        """Pull data from vcontrol API."""
        try:
            res = requests.get(f"{self._base_url}/api/vcontrol/status", timeout=15)
            res.raise_for_status()
            res = requests.get(
                f"{self._base_url}/api/vcontrol/commands/all", timeout=15
            )
            res.raise_for_status()
            return res.json()
        except requests.HTTPError:
            _LOGGER.log(
                msg="Couldn't fetch API update! Check connectivity to vcontrol API."
            )
            return None
        except requests.exceptions.Timeout:
            _LOGGER.log(msg="Connection to vcontrol API timed out!")
            return None
