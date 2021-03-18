import voluptuous as vol
import logging
import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, Optional

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_MAC, CONF_NAME, CONF_FRIENDLY_NAME, CONF_TEMPERATURE_UNIT, 
    TEMP_CELSIUS, TEMP_FAHRENHEIT, DEVICE_CLASS_TEMPERATURE,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.core import callback
from homeassistant.helpers.device_registry import format_mac
import homeassistant.helpers.config_validation as cv

from . import _LOGGER
from .mug import EmberMug
from .const import ICON_DEFAULT, ICON_UNAVAILABLE


# Schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.matches_regex(r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)


CONNECT_TIMEOUT = 30
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    _LOGGER.debug("Starting Ember Mug Setup")
    ember_mug = EmberMug(config[CONF_MAC], config.get(CONF_TEMPERATURE_UNIT) != TEMP_FAHRENHEIT)
    async_add_entities([EmberMugSensor(ember_mug, config)])


class EmberMugSensor(Entity):
    """
    Config for an Ember Mug
    """

    def __init__(self, mug: EmberMug, config: ConfigType):
        super().__init__()
        self.mug = mug
        self.mac_address = config[CONF_MAC]
        self._unique_id = f'ember_mug_{format_mac(self.mac_address)}'
        self._name = config.get(CONF_NAME, f'Ember Mug {self.mac_address}')
        self._unit_of_measurement = config.get(CONF_TEMPERATURE_UNIT, TEMP_CELSIUS)

        self._icon = ICON_DEFAULT
        self._state = None
        self._available = True
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
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self.mug.current_temp

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.mug.attrs

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

    async def async_added_to_hass(self) -> None:
        _LOGGER.info(f'Starting Init for {self._name}')
        await self.mug.init()

        self._loop = True
        _LOGGER.info(f'Starting loop {self._name}')

        while self._loop:
            _LOGGER.debug(f"Mug Update")
            await self.mug.update_all()
            self.async_schedule_update_ha_state()
            await asyncio.sleep(60)

    async def async_will_remove_from_hass(self) -> None:
        self._loop = False
        await self.mug.disconnect()

    async def async_update(self) -> None:
        _LOGGER.warning(f'Async update called for {self._name}')

        if await self.mug.update_all() is True:
            self._state = self.mug.current_temp
            self._available = True
        else:
            self._available = False
            self._state = None
