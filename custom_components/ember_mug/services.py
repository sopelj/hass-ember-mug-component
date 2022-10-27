"""Services for updating Mug information."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import ATTR_MUG_NAME, ATTR_RGB_COLOR, ATTR_TARGET_TEMP, MUG_NAME_REGEX

if TYPE_CHECKING:
    from .sensor import EmberMugSensor


_LOGGER = logging.getLogger(__name__)

SET_LED_COLOUR_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): vol.All(
        vol.ExactSequence((cv.byte,) * 3),
        vol.Coerce(tuple),
    ),
}

SET_TARGET_TEMP_SCHEMA = {
    vol.Required(ATTR_TARGET_TEMP): cv.positive_float,
}

SET_MUG_NAME_SCHEMA = {
    vol.Required(ATTR_MUG_NAME): cv.matches_regex(MUG_NAME_REGEX),
}


async def set_led_colour(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set LED colour of mug."""
    led_colour: tuple[int, int, int] = service_call.data[ATTR_RGB_COLOR]
    _LOGGER.info(f"Called service set led colour of {entity} to {led_colour})")
    await entity.coordinator.connection.set_led_colour((*led_colour, 255))


async def set_target_temp(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set target temp of mug."""
    target_temp: float = service_call.data[ATTR_TARGET_TEMP]
    _LOGGER.debug(f"Service called to set temp to {target_temp}")
    await entity.coordinator.connection.set_target_temp(target_temp)


async def set_mug_name(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set target temp of mug."""
    name: str = service_call.data[ATTR_MUG_NAME]
    _LOGGER.debug(f"Service called to set name to '{name}'")
    await entity.coordinator.connection.set_name(name)
