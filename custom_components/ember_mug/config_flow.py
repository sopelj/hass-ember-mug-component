"""Add Config Flow for Ember Mug."""
from __future__ import annotations

import re
from typing import Any, Optional

from bleak import BleakClient
from homeassistant import config_entries
from homeassistant.const import (
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
import voluptuous as vol

from . import _LOGGER
from .const import DOMAIN
from .mug import find_mugs

CONF_MUG = "mug"
DEFAULT_NAME = "Ember Mug"
MUG_NAME_MAC_REGEX = r"^(.+): (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))$"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for Ember Mug."""

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Implement flow for config started by User in the UI."""
        errors: dict[str, str] = {}
        if user_input is not None:
            name, mac_address = DEFAULT_NAME, ""
            if match := re.match(MUG_NAME_MAC_REGEX, user_input[CONF_MUG]):
                name, mac_address = match.groups()[:2]
                async with BleakClient(mac_address) as client:
                    connected = await client.is_connected()
                    _LOGGER.info(f"Connected: {connected}")
                    paired = await client.pair()
                    _LOGGER.info(f"Paired: {paired}")
                    if not connected or not paired:
                        errors["base"] = "not_connected"
            else:
                errors["base"] = "invalid_mac"
            if not errors:
                name = user_input.get(CONF_NAME) or name
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_MAC: mac_address,
                        CONF_TEMPERATURE_UNIT: user_input[CONF_TEMPERATURE_UNIT][1],
                    },
                )

        devices = await find_mugs()
        _LOGGER.info(devices)
        if not devices:
            return self.async_abort("not_found")

        schema = vol.Schema(
            {
                vol.Required(CONF_MUG, default=""): vol.In(
                    [f"{n}: {a}" for a, n in devices.items()]
                ),
                vol.Optional(CONF_NAME, default=""): str,
                vol.Required(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
                    [TEMP_CELSIUS, TEMP_FAHRENHEIT]
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input):
        """Forward from import flow."""
        return await self.async_step_user(user_input)
