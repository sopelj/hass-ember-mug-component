"""Ember Mug Custom Integration."""
import logging

import homeassistant.helpers.config_validation as cv
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
    """Register service calls."""
    from .services import set_led_colour

    hass.services.async_register(
        DOMAIN, SERVICE_SET_LED_COLOUR, set_led_colour, SET_LED_COLOUR_SCHEMA
    )
    return True
