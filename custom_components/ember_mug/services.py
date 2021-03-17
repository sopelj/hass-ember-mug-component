from .const import LED_COLOUR_UUID, TARGET_TEMP_UUID

from . import _LOGGER


async def set_led_colour(self, red: int = 255, green: int = 255, blue: int = 255, alpha: int = 255):
    colour = bytearray([red, green, blue, alpha])
    _LOGGER.debug(f'Set colour to {colour}')
    await self.client.write_gatt_char(LED_COLOUR_UUID, colour, False)

async def set_target_temp(self, temp: float): 
    _LOGGER.debug(f"Set to {temp}")
    target = bytearray(int(temp / 0.01).to_bytes(2, 'little'))
    resp = await self.client.write_gatt_char(TARGET_TEMP_UUID, target, False)
    _LOGGER.debug(resp)