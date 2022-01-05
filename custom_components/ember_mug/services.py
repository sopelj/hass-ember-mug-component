"""Services for updating Mug information."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import ServiceCall

from . import _LOGGER
from .const import ATTR_MUG_NAME, ATTR_RGB_COLOR, ATTR_TARGET_TEMP

if TYPE_CHECKING:
    from .sensor import EmberMugSensor


async def set_led_colour(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set LED colour of mug."""
    led_colour: tuple[int, int, int] = service_call.data[ATTR_RGB_COLOR]
    _LOGGER.info(f"Called service set led colour of {entity} to {led_colour})")
    await entity.mug.set_led_colour([*led_colour, 255])


async def set_target_temp(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set target temp of mug."""
    target_temp: float = service_call.data[ATTR_TARGET_TEMP]
    _LOGGER.debug(f"Service called to set temp to {target_temp}")
    await entity.mug.set_target_temp(target_temp)


async def set_mug_name(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set target temp of mug."""
    name: str = service_call.data[ATTR_MUG_NAME]
    _LOGGER.debug(f"Service called to set name to '{name}'")
    await entity.mug.set_mug_name(name)
