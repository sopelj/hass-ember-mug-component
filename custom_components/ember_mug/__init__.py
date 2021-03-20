"""Ember Mug Custom Integration."""
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
import voluptuous as vol

from .const import ATTR_RGB_COLOR, DOMAIN, SERVICE_SET_LED_COLOUR

_LOGGER = logging.getLogger(__name__)


SET_LED_COLOUR_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): vol.All(
        vol.ExactSequence((cv.byte,) * 3), vol.Coerce(tuple)
    ),
}


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Create EntityComponent to facilitate service calls."""
    from .services import set_led_colour

    component = hass.data[DOMAIN] = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_setup(config)
    component.async_register_entity_service(
        SERVICE_SET_LED_COLOUR,
        cv.make_entity_service_schema(SET_LED_COLOUR_SCHEMA),
        set_led_colour,
    )
    return True


async def async_setup_entry(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up a config entry."""
    return await hass.data[DOMAIN].async_setup_entry(entry)
