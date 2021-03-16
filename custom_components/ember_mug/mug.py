import asyncio

from bleak import BleakClient
from bleak.exc import BleakError

from . import _LOGGER
from .const import (
    TARGET_TEMP_UUID, LED_COLOUR_UUID, CURRENT_TEMP_UUID, BATTERY_UUID, ICON_DEFAULT, ICON_UNAVAILABLE
)


class EmberMug:
    def __init__(self, mac_address: str, use_metric = True):
        self.client = BleakClient(mac_address)
        self.use_metric = use_metric
        self.colour = [255, 255, 255]
        self.current_temp = None
        self.target_temp = None
        self.battery = None

    @property
    def colour_hex(self) -> str:
        r, g, b = self.colour
        return f'#{r:02x}{g:02x}{b:02x}'

    async def _temp_from_bytes(self, temp_bytes: bytearray) -> float:
        temp = float(int.from_bytes(temp_bytes, byteorder='little', signed=False)) * 0.01
        if self.use_metric is False:
            # Convert to fahrenheit
            temp = (temp * 9/5) + 32
        return round(temp, 2)

    async def update_battery(self) -> None:
        current_battery = await self.client.read_gatt_char(BATTERY_UUID)
        battery_percent = float(current_battery[0])
        _LOGGER.debug(f'Battery is at {battery_percent}')
        self.current_temp = round(battery_percent, 2)

    async def update_led_colour(self) -> None:
        r, g, b, _ = await self.client.read_gatt_char(LED_COLOUR_UUID)
        self.colour = [r, g, b]
 
    async def update_target_temp(self) -> None:
        temp_bytes = await self.client.read_gatt_char(TARGET_TEMP_UUID)
        self.target_temp = await self._temp_from_bytes(temp_bytes)
        _LOGGER.debug(f'Target temp {self.target_temp}')

    async def update_current_temp(self) -> None:
        temp_bytes = await self.client.read_gatt_char(CURRENT_TEMP_UUID)
        self.current_temp = await self._temp_from_bytes(temp_bytes)
        _LOGGER.debug(f'Current temp {self.current_temp}')

    async def set_led_colour(self, red: int = 255, green: int = 255, blue: int = 255, alpha: int = 255):
        colour = bytearray([red, green, blue, alpha])
        _LOGGER.debug(f'Set colour to {colour}')
        await self.client.write_gatt_char(LED_COLOUR_UUID, colour, False)

    async def set_target_temp(self, temp: float): 
        _LOGGER.debug(f"Set to {temp}")
        target = bytearray(int(temp / 0.01).to_bytes(2, 'little'))
        resp = await self.client.write_gatt_char(TARGET_TEMP_UUID, target, False)
        _LOGGER.debug(resp)

    async def update_all(self) -> bool:
        try:
            if not await self.client.is_connected():
                await self.client.connect()
            await self.update_battery()
            await self.update_current_temp()
            await self.update_target_temp()
            await self.update_led_colour()
            return True
        except BleakError as e:
            _LOGGER.error(str(e))
            return False

    def __del__(self) -> None:
        asyncio.ensure_future(self.client.disconnect())