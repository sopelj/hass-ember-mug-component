from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any, Callable, Dict, Optional, Union

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONF_FRIENDLY_NAME,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from . import _LOGGER
from .const import ICON_DEFAULT, ICON_UNAVAILABLE
from .mug import EmberMug

# Schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.matches_regex(r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    _LOGGER.debug("Starting Ember Mug Setup")
    async_add_entities([EmberMugSensor(hass, config)])


class EmberMugSensor(Entity):
    """
    Config for an Ember Mug
    """

    def __init__(self, hass: HomeAssistantType, config: ConfigType):
        super().__init__()
        self.hass = hass
        self.mac_address = config[CONF_MAC]
        self._unique_id = f'ember_mug_{format_mac(self.mac_address)}'
        self._name = config.get(CONF_NAME, f'Ember Mug {self.mac_address}')
        self._unit_of_measurement = config.get(CONF_TEMPERATURE_UNIT, TEMP_CELSIUS)

        self.mug = EmberMug(
            self.mac_address, 
            self._unit_of_measurement != TEMP_FAHRENHEIT,
            self,
        )

        self._icon = ICON_DEFAULT
        self._loop = False

        _LOGGER.info(f"Ember Mug {self._name} Setup")

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def available(self) -> bool:
        return self.mug.available

    @property
    def state(self) -> Optional[float]:
        return self.mug.current_temp

    @property
    def state_attributes(self) -> Dict[str, Union[str, float]]:
        return {
            ATTR_BATTERY_LEVEL: self.mug.battery,
            'led_colour': self.mug.colour,
            'current_temp': self.mug.current_temp,
            'target_temp': self.mug.target_temp,
            'uuid_debug': self.mug.uuid_debug,
            'state': self.mug.state,
        }

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    @property
    def device_class(self) -> str:
        return DEVICE_CLASS_TEMPERATURE

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def should_poll(self) -> bool:
        return False

    @callback
    def async_update_callback(self) -> None:
        """
        Called in Mug `async_run` to signal change to hass
        """
        _LOGGER.debug('Update in HASS requested')
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        _LOGGER.info(f'Starting run for {self._name}')
        self.hass.async_create_task(self.mug.async_run())

    async def async_will_remove_from_hass(self) -> None:
        _LOGGER.info(f'Stop running {self._name}')
        await self.mug.disconnect()
