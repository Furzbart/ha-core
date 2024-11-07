"""Config flow for Viessmann vcontrol integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PATH, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_HOST, description={"suggested_value": "http://127.0.0.1"}
        ): str,
        vol.Optional(CONF_PORT, default="5000"): str,
        vol.Required(CONF_PATH, default="/api/vcontrol"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    _host = data.get(CONF_HOST)
    _port = data.get(CONF_PORT)
    baseUrl = "/api/vcontrol"
    requestUrl = f"{_host}:{_port}{baseUrl}/status"
    success = await getStatus(requestUrl)

    if not success:
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": "Viessmann vcontrol"}


async def getStatus(requestUrl: str):
    """Call vcontrol API and query connection status.

    This will validate both connection parameters (IP/URL) as well as vcontrol connectivity to the heater.
    """
    async with aiohttp.ClientSession() as sess, sess.get(requestUrl) as res:
        if res.status == 200:
            logging.debug(
                msg="Connection to Viessmann heater successfully established."
            )
            return True
    return False


class VControlConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Viessmann vcontrol."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
