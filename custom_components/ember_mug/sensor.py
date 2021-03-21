"""Sensor Entity for Ember Mug."""
from __future__ import annotations

from typing import Callable, Dict, Optional, Union

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import voluptuous as vol

from . import _LOGGER
from .const import (
    ATTR_RGB_COLOR,
    ATTR_TARGET_TEMP,
    ICON_DEFAULT,
    SERVICE_SET_LED_COLOUR,
    SERVICE_SET_TARGET_TEMP,
)
from .mug import EmberMug

# Schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.matches_regex(
            r"^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$"
        ),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)

SET_LED_COLOUR_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): vol.All(
        vol.ExactSequence((cv.byte,) * 3), vol.Coerce(tuple)
    ),
}

SET_TARGET_TEMP_SCHEMA = {
    vol.Required(ATTR_TARGET_TEMP): cv.positive_float,
}


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Add Mug Sensor Entity to HASS."""
    from .services import set_led_colour, set_target_temp

    _LOGGER.debug("Setup platform")

    async_add_entities([EmberMugSensor(hass, config)])

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_SET_LED_COLOUR, SET_LED_COLOUR_SCHEMA, set_led_colour
    )
    platform.async_register_entity_service(
        SERVICE_SET_TARGET_TEMP, SET_TARGET_TEMP_SCHEMA, set_target_temp
    )


async def async_setup_entry(hass: HomeAssistantType, config: ConfigType):
    """Set up services for Entry."""
    _LOGGER.debug(f"Setup entry {config}")


class EmberMugSensor(Entity):
    """Config for an Ember Mug."""

    def __init__(self, hass: HomeAssistantType, config: ConfigType):
        """Set config and initial values. Also add EmberMug class which tracks changes."""
        super().__init__()
        self.mac_address = config[CONF_MAC]
        self._icon = ICON_DEFAULT
        self._unique_id = f"ember_mug_{format_mac(self.mac_address)}"
        self._name = config.get(CONF_NAME, f"Ember Mug {self.mac_address}")
        self._unit_of_measurement = config.get(CONF_TEMPERATURE_UNIT, TEMP_CELSIUS)

        self.mug = EmberMug(
            self.mac_address,
            self._unit_of_measurement != TEMP_FAHRENHEIT,
            self.async_update_callback,
            hass,
        )
        _LOGGER.info(f"Ember Mug {self._name} Setup")

    @property
    def name(self) -> str:
        """Human readable name."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return unique ID for HASS."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return if this entity is available. This is only sort of reliable since we don't want to set it too often because Bluetooth is unreliable..."""
        return self.mug.available

    @property
    def state(self) -> Optional[float]:
        """Use the current temperature for the state of the mug."""
        return self.mug.current_temp

    @property
    def state_attributes(self) -> Dict[str, Union[str, float]]:
        """Return a list of attributes."""
        return {
            ATTR_BATTERY_LEVEL: self.mug.battery,
            "led_colour": self.mug.colour,
            "current_temp": self.mug.current_temp,
            "target_temp": self.mug.target_temp,
            "latest_push": self.mug.latest_push,
            "serial_number": self.mug.serial_number,
            "on_charging_base": self.mug.on_charging_base,
            "liquid_level": self.mug.liquid_level,
            "liquid_state": self.mug.liquid_state_label,
            "udsk": self.mug.udsk,
            "dsk": self.mug.dsk,
            "name": self.mug.name,
        }

    @property
    def unit_of_measurement(self) -> str:
        """Return unit of measurement. By default this is Celsius, but can be customized in config."""
        return self._unit_of_measurement

    @property
    def device_class(self) -> str:
        """Use temperature device class, since warming is its primary function."""
        return DEVICE_CLASS_TEMPERATURE

    @property
    def icon(self) -> str:
        """Icon representation for this mug."""
        return self._icon

    @property
    def should_poll(self) -> bool:
        """Don't use polling. We'll request updates."""
        return False

    @callback
    def async_update_callback(self) -> None:
        """Is called in Mug `async_run` to signal change to hass."""
        _LOGGER.debug("Update in HASS requested")
        self.async_schedule_update_ha_state()

    async def async_added_to_hass(self) -> None:
        """Stop polling on remove."""
        _LOGGER.info(f"Start running {self._name}")
        # Start loop
        self.hass.async_create_task(self.mug.async_run())

    async def async_will_remove_from_hass(self) -> None:
        """Stop polling on remove."""
        _LOGGER.info(f"Stop running {self._name}")
        await self.mug.disconnect()
