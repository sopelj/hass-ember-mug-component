"""Ember Mug Custom Integration."""
import logging

from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
import voluptuous as vol

from .const import ATTR_RGB_COLOR, LED_COLOUR_UUID, SERVICE_SET_LED_COLOUR

_LOGGER = logging.getLogger(__name__)


SET_LED_COLOUR_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): vol.All(
        vol.ExactSequence((cv.byte,) * 3), vol.Coerce(tuple)
    ),
}


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Register service calls."""
    return True


async def async_setup_entry(hass: HomeAssistantType, entry):
    """Set up services for Entry."""

    platform = entity_platform.current_platform.get()

    async def set_led_colour(call) -> None:
        """Set LED colour of mug."""
        params = dict(call.data["params"])
        _LOGGER.info(
            f"Called service set led colour with entity {entry} and {call} {params})"
        )
        colour = bytearray([*params[ATTR_RGB_COLOR], 255])
        _LOGGER.debug(f"Set colour to {colour}")
        await entry.mug.client.write_gatt_char(LED_COLOUR_UUID, colour, False)

    platform.async_register_entity_service(
        SERVICE_SET_LED_COLOUR, SET_LED_COLOUR_SCHEMA, set_led_colour
    )
