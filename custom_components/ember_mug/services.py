"""Services for updating Mug information."""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from bleak import BleakClient, discover
from homeassistant.core import ServiceCall

from . import _LOGGER
from .const import ATTR_RGB_COLOR, ATTR_TARGET_TEMP, LED_COLOUR_UUID, TARGET_TEMP_UUID

if TYPE_CHECKING:
    from .sensor import EmberMugSensor


async def set_led_colour(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set LED colour of mug."""
    led_colour: Tuple[int, int, int] = service_call.data[ATTR_RGB_COLOR]
    _LOGGER.info(f"Called service set led colour of {entity} to {led_colour})")
    colour = bytearray([*led_colour, 255])  # To RGBA bytearray
    resp = await entity.mug.client.write_gatt_char(LED_COLOUR_UUID, colour, False)
    _LOGGER.debug(resp)


async def set_target_temp(entity: EmberMugSensor, service_call: ServiceCall) -> None:
    """Set target temp of mug."""
    target_temp = service_call.data[ATTR_TARGET_TEMP]
    _LOGGER.debug(f"Set to {target_temp}")
    target = bytearray(int(target_temp / 0.01).to_bytes(2, "little"))
    resp = await entity.client.write_gatt_char(TARGET_TEMP_UUID, target, False)
    _LOGGER.debug(resp)


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
