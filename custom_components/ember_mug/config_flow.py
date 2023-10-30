"""Add Config Flow for Ember Mug."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from bleak import BleakClient, BleakError
from ember_mug.consts import (
    EMBER_BLUETOOTH_NAMES,
    EMBER_TRAVEL_MUG,
    EMBER_TRAVEL_MUG_SHORT,
)
from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    UnitOfTemperature,
)
from homeassistant.helpers import config_validation as cv

from . import _LOGGER
from .const import CONF_DEBUG, CONF_INCLUDE_EXTRA, DOMAIN

if TYPE_CHECKING:
    from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
    from homeassistant.data_entry_flow import FlowResult


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for Ember Mug."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(
        self,
        discovery_info: BluetoothServiceInfoBleak,
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
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """First step for users."""
        errors: dict[str, str] = {}
        if user_input:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(
                address.replace(":", "").lower(),
                raise_on_progress=False,
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
                if discovery_info.name not in EMBER_BLUETOOTH_NAMES:
                    continue
                try:
                    async with BleakClient(discovery_info.device) as client:
                        await client.connect()
                        with contextlib.suppress(BleakError, EOFError):
                            # An error will be raised if already paired
                            await client.pair()
                except BleakError:
                    self.async_abort(reason="cannot_connect")
                self._discovery_info = discovery_info
                break
            else:
                return self.async_abort(reason="no_new_devices")

        name = self._discovery_info.name
        if name == EMBER_TRAVEL_MUG_SHORT:
            name = EMBER_TRAVEL_MUG
        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        self._discovery_info.address: f"{name} ({self._discovery_info.address})",
                    },
                ),
                vol.Required(CONF_NAME, default=name): str,
                vol.Required(
                    CONF_TEMPERATURE_UNIT,
                    default=UnitOfTemperature.CELSIUS,
                ): vol.In(
                    [UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT],
                ),
                vol.Optional(CONF_INCLUDE_EXTRA, default=False): cv.boolean,
                vol.Optional(CONF_DEBUG, default=False): cv.boolean,
            },
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
