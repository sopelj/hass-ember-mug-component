"""Services for updating Mug information."""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from bleak import BleakClient, discover
from homeassistant.core import ServiceCall

from . import _LOGGER
from .const import ATTR_RGB_COLOR, ATTR_TARGET_TEMP

if TYPE_CHECKING:
    from .sensor import EmberMugSensor


async def set_led_colour(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set LED colour of mug."""
    led_colour: Tuple[int, int, int] = service_call.data[ATTR_RGB_COLOR]
    _LOGGER.info(f"Called service set led colour of {entity} to {led_colour})")
    await entity.mug.set_led_colour([*led_colour, 255])


async def set_target_temp(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set target temp of mug."""
    target_temp: float = service_call.data[ATTR_TARGET_TEMP]
    _LOGGER.debug(f"Set to {target_temp}")
    await entity.mug.set_target_temp(target_temp)


async def find_mugs():
    """Find all mugs."""
    try:
        print("Searching..", end="")

        while True:
            print(".", end="")
            devices = await discover()

            for device in devices:
                if device.name == "Ember Ceramic Mug":
                    # We found the ember mug!
                    print(device.address)
                    print(device.name)
                    print(device.details)

                    async with BleakClient(device) as client:
                        x = await client.is_connected()
                        print(f"Connected: {x}")
                        y = await client.pair()
                        print(f"Paired: {y}")
    except Exception as e:
        print(f"Error: {e}")
