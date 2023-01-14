"""Services for updating Mug information."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.core import ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import ATTR_RGB_COLOR

if TYPE_CHECKING:
    from .sensor import EmberMugSensor


_LOGGER = logging.getLogger(__name__)

SET_LED_COLOUR_SCHEMA = {
    vol.Required(ATTR_RGB_COLOR): vol.All(
        vol.ExactSequence((cv.byte,) * 3),
        vol.Coerce(tuple),
    ),
}


async def set_led_colour(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set LED colour of mug."""
    led_colour: tuple[int, int, int] = service_call.data[ATTR_RGB_COLOR]
    _LOGGER.info(f"Called service set led colour of {entity} to {led_colour})")
    await entity.coordinator.connection.set_led_colour((*led_colour, 255))
