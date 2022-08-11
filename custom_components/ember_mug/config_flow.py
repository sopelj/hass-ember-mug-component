"""Add Config Flow for Ember Mug."""
from __future__ import annotations

import contextlib
from typing import Any

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak, async_discovered_service_info,
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from bleak import BleakClient, BleakError
import voluptuous as vol
from . import _LOGGER
from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for Ember Mug."""
    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug("Discovered bluetooth device: %s", discovery_info)
        await self.async_set_unique_id(discovery_info.address.replace(":", "").lower())
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {
            CONF_NAME: discovery_info.name,
            CONF_ADDRESS: discovery_info.address,
        }
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(
                address.replace(":", "").lower(), raise_on_progress=False
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        if not self._discovery_info:
            current_addresses = self._async_current_ids()
            for discovery_info in async_discovered_service_info(self.hass):
                address = discovery_info.address
                unique_id = address.replace(":", "").lower()
                if unique_id in current_addresses:
                    continue
                try:
                    with BleakClient(discovery_info.device) as client:
                        await client.connect()
                        with contextlib.suppress(BleakError):
                            client.pair()
                except BleakError:
                    self.async_abort(reason='cannot_connect')
                self._discovery_info = discovery_info
                break
            else:
                return self.async_abort(reason="no_unconfigured_devices")

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        self._discovery_info.address: f"{self._discovery_info.name} ({self._discovery_info.address})"
                    }
                ),
                vol.Required(CONF_NAME, default=self._discovery_info.name): str,
                vol.Required(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): vol.In(
                    [TEMP_CELSIUS, TEMP_FAHRENHEIT],
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

