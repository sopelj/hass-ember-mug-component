import asyncio
import socket
from typing import Any, Optional

from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_MAC, CONF_PORT, CONF_TEMPERATURE_UNIT, TEMP_CELSIUS, TEMP_FAHRENHEIT, CONF_NAME
import voluptuous as vol

from . import _LOGGER
from .const import DOMAIN
from .mug import EmberMug, find_mugs

MUG_SCHEMA = vol.Schema({
    vol.Required(CONF_MAC, default=""): str,
    vol.Optional(CONF_NAME, default=""): str,
    vol.Required(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
        [TEMP_CELSIUS, TEMP_FAHRENHEIT]
    ),
})


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        errors: dict[str, str] = {}
        devices = await find_mugs()
        _LOGGER.info(devices)
        if not devices:
            return self.async_abort('not_found')
        if user_input is not None:
            pass
        schema = vol.Schema({
            vol.Required(CONF_MAC, default=""): vol.In(list(devices)),
            vol.Optional(CONF_NAME, default=""): str,
            vol.Required(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
                [TEMP_CELSIUS, TEMP_FAHRENHEIT]
            ),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input):
        return await self.async_step_user(user_input)
