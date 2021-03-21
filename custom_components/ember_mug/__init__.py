"""Ember Mug Custom Integration."""
from __future__ import annotations

import logging
from typing import Dict, Optional, Union

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
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import (  # noqa: F401
    PLATFORM_SCHEMA,
    PLATFORM_SCHEMA_BASE,
)
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
import voluptuous as vol

from .const import ATTR_RGB_COLOR, DOMAIN, ICON_DEFAULT, SERVICE_SET_LED_COLOUR
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

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Create EntityComponent to facilitate service calls."""
    from .services import set_led_colour

    component = hass.data[DOMAIN] = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_setup(config)

    _LOGGER.info(config[DOMAIN])
    await component.async_add_entities(
        [EmberMugSensor(hass, c) for c in config[DOMAIN]]
    )

    component.async_register_entity_service(
        SERVICE_SET_LED_COLOUR,
        cv.make_entity_service_schema(SET_LED_COLOUR_SCHEMA),
        set_led_colour,
    )
    return True


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
            "state": self.mug.state,
            "second_state": self.mug.second_state,
            "serial_number": self.mug.serial_number,
            "uuid_debug": self.mug.uuid_debug,
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
