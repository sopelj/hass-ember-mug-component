"""Add Config Flow for Ember Mug."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from bleak import BleakClient, BleakError
from ember_mug.consts import DEVICE_SERVICE_UUIDS
from homeassistant import config_entries
from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.const import CONF_ADDRESS, CONF_NAME, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.util.unit_conversion import TemperatureConverter

from . import _LOGGER
from .const import (
    CONF_DEBUG,
    CONF_PRESETS,
    CONF_PRESETS_UNIT,
    CONFIG_VERSION,
    DEFAULT_PRESETS,
    DOMAIN,
    MAX_TEMP_CELSIUS,
    MIN_TEMP_CELSIUS,
)

if TYPE_CHECKING:
    from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
    from homeassistant.data_entry_flow import FlowResult


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for Ember Mug."""

    VERSION = CONFIG_VERSION

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
            for service_info in async_discovered_service_info(self.hass):
                address = service_info.address
                unique_id = address.replace(":", "").lower()
                if unique_id in current_addresses:
                    _LOGGER.debug("Skipping device %s which is already setup", service_info.address)
                    continue
                if not set(service_info.service_uuids).intersection(DEVICE_SERVICE_UUIDS) and (
                    not service_info.name or not service_info.name.startswith("Ember")
                ):
                    _LOGGER.debug(
                        "Skipping unrelated device %s with services: %s",
                        service_info.name,
                        service_info.service_uuids,
                    )
                    continue
                try:
                    async with BleakClient(service_info.device) as client:
                        await client.connect()
                        with contextlib.suppress(BleakError, EOFError):
                            # An error will be raised if already paired
                            await client.pair()
                except BleakError:
                    self.async_abort(reason="cannot_connect")
                self._discovery_info = service_info
                break
            else:
                return self.async_abort(reason="no_new_devices")

        name = self._discovery_info.name
        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): vol.In(
                    {
                        self._discovery_info.address: f"{name} ({self._discovery_info.address})",
                    },
                ),
                vol.Required(CONF_NAME, default=name): str,
            },
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Allows users to configure integration after setup."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        presets_default = self.config_entry.options.get(CONF_PRESETS, DEFAULT_PRESETS)

        if user_input is not None:
            min_temp, max_temp = MIN_TEMP_CELSIUS, MAX_TEMP_CELSIUS
            if user_input[CONF_PRESETS_UNIT] == UnitOfTemperature.FAHRENHEIT:
                min_temp, max_temp = (
                    TemperatureConverter.convert(t, UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT)
                    for t in [MIN_TEMP_CELSIUS, MAX_TEMP_CELSIUS]
                )
            if presets := user_input[CONF_PRESETS]:
                schema = vol.Schema(
                    {
                        str: vol.All(
                            vol.Union(float, int),
                            vol.Any(vol.Literal(0), vol.Range(min=min_temp, max=max_temp)),
                        ),
                    },
                )
                try:
                    schema(presets)
                except (vol.Invalid, vol.MultipleInvalid) as e:
                    errors[CONF_PRESETS] = str(e)
                    # Use as default to avoid clearing the field on the user they can cancel if confused
                    presets_default = presets
                else:
                    _LOGGER.debug("Got updated options: %s", user_input)
                    return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_PRESETS_UNIT,
                        default=self.config_entry.options.get(CONF_PRESETS_UNIT, UnitOfTemperature.CELSIUS),
                    ): vol.In(
                        [UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT],
                    ),
                    vol.Required(
                        CONF_PRESETS,
                        default=presets_default,
                    ): selector.ObjectSelector(),
                    vol.Optional(CONF_DEBUG, default=self.config_entry.options.get(CONF_DEBUG, False)): cv.boolean,
                },
            ),
            errors=errors,
        )
