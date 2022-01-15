"""Add Config Flow for Ember Mug."""
from __future__ import annotations

import contextlib
import re
from typing import Any, Optional

from bleak import BleakClient, BleakError
from homeassistant import config_entries
from homeassistant.const import (
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.helpers.device_registry import format_mac
import voluptuous as vol

from . import _LOGGER
from .const import DOMAIN
from .mug import find_mug

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
                try:
                    async with BleakClient(mac_address) as client:
                        connected = True
                        if not client.is_connected:
                            connected = await client.connect()
                            _LOGGER.info(f"Connected: {connected}")
                        with contextlib.suppress(BleakError):
                            paired = await client.pair()
                            _LOGGER.info(f"Paired: {paired}")
                        if not connected:
                            errors["base"] = "not_connected"
                except BleakError as e:
                    _LOGGER.error(f"Bleak Error whilst connecting: {e}")
                    errors["base"] = "connection_failed"
            else:
                errors["base"] = "invalid_mac"
            if not errors:
                name = user_input.get(CONF_NAME) or name
                await self.async_set_unique_id(
                    format_mac(mac_address), raise_on_progress=False
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_MAC: mac_address,
                        CONF_TEMPERATURE_UNIT: user_input[CONF_TEMPERATURE_UNIT],
                    },
                )

        devices = await find_mug()
        _LOGGER.info(devices)
        if not devices:
            return self.async_abort(reason="not_found")
        device_mac, name = next(iter(devices.items()))
        schema = vol.Schema(
            {
                vol.Required(CONF_MUG, default=device_mac): vol.In([device_mac]),
                vol.Optional(CONF_NAME, default=name): str,
                vol.Required(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
                    [TEMP_CELSIUS, TEMP_FAHRENHEIT]
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input: dict[str, str]):
        """Forward from import flow."""
        return await self.async_step_user(user_input)
