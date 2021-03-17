from typing import Dict, Union
import asyncio

from bleak import BleakClient
from bleak.exc import BleakError

from . import _LOGGER
from .const import (
    TARGET_TEMP_UUID, LED_COLOUR_UUID, CURRENT_TEMP_UUID, BATTERY_UUID, ICON_DEFAULT, ICON_UNAVAILABLE, STATE_UUID, UNKNOWN_READ_UUIDS
)


class EmberMug:
    def __init__(self, mac_address: str, use_metric = True):
        self.client = BleakClient(mac_address)
        self.use_metric = use_metric
        self.state = None
        self.led_colour_rgb = [255, 255, 255]
        self.current_temp: float = None
        self.target_temp: float = None
        self.battery: float = None
        self.uuid_debug = {
            uuid: None for uuid in UNKNOWN_READ_UUIDS
        }

    @property
    def colour(self) -> str:
        r, g, b = self.led_colour_rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    @property
    def attrs(self) -> Dict[str, Union[str, float]]:
        return {
            'led_colour': self.colour,
            'current_temp': self.current_temp,
            'target_temp': self.target_temp,
            'battery': self.battery,
            'uuid_debug': self.uuid_debug,
            'state': self.state,
        }

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
        self.battery = round(battery_percent, 2)

    async def update_led_colour(self) -> None:
        r, g, b, _ = await self.client.read_gatt_char(LED_COLOUR_UUID)
        self.led_colour_rgb = [r, g, b]
 
    async def update_target_temp(self) -> None:
        temp_bytes = await self.client.read_gatt_char(TARGET_TEMP_UUID)
        self.target_temp = await self._temp_from_bytes(temp_bytes)
        _LOGGER.debug(f'Target temp {self.target_temp}')

    async def update_current_temp(self) -> None:
        temp_bytes = await self.client.read_gatt_char(CURRENT_TEMP_UUID)
        self.current_temp = await self._temp_from_bytes(temp_bytes)
        _LOGGER.debug(f'Current temp {self.current_temp}')

    async def update_state(self) -> None:
        self.state = str(await self.client.read_gatt_char(STATE_UUID))

    async def update_uuid_debug(self):
        for uuid in self.uuid_debug:
            value = await self.client.read_gatt_char(uuid)
            _LOGGER.debug(f'Current value of {uuid}: {self.current_temp}')
            self.uuid_debug[uuid] = str(value)

    async def update_all(self) -> bool:
        try:
            if not await self.client.is_connected():
                await self.client.connect()
                await self.client.pair()

            for attr in self.attrs:
                await getattr(self, f'update_{attr}')()
    
            success = True
        except BleakError as e:
            _LOGGER.error(str(e))
            success = False
        finally:
            await self.client.disconnect()
        return success

    def __del__(self) -> None:
        asyncio.ensure_future(self.client.disconnect())