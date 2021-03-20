from typing import Dict, Union, Callable
import asyncio
import contextlib

from homeassistant.helpers.icon import icon_for_battery_level

from bleak import BleakClient
from bleak.exc import BleakError

from . import _LOGGER
from .const import (
    TARGET_TEMP_UUID, LED_COLOUR_UUID, CURRENT_TEMP_UUID, BATTERY_UUID, ICON_DEFAULT, ICON_UNAVAILABLE, STATE_UUID, UNKNOWN_READ_UUIDS
)


class EmberMug:
    def __init__(self, mac_address: str, use_metric, update_callback: Callable) -> None:
        self.mac_address = mac_address
        self.client = BleakClient(mac_address)
        self.use_metric = use_metric
        self.state = None
        self.charging = False  # TODO from state?
        self.led_colour_rgb = [255, 255, 255]
        self.current_temp: float = None
        self.target_temp: float = None
        self.battery: float = None
        self._loop = False
        self.available = False
        self.uuid_debug = {
            uuid: None for uuid in UNKNOWN_READ_UUIDS
        }
        self.update_callback = update_callback

    @property
    def colour(self) -> str:
        r, g, b = self.led_colour_rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    @property
    def battery_icon(self) -> str:
        return icon_for_battery_level(self.battery, charging=self.charging)

    @property
    def attrs(self) -> Dict[str, Union[str, float]]:
        return {
            'led_colour': self.colour,
            'current_temp': self.current_temp,
            'target_temp': self.target_temp,
            'battery': self.battery,
            'battery_icon': self.battery_icon,
            'uuid_debug': self.uuid_debug,
            'state': self.state,
        }

    async def async_run(self):
        self._loop = True
        _LOGGER.info(f'Starting mug loop {self.mac_address}')

        while self._loop:
            if not await self.client.is_connected():
                await self.connect()

            await self.update_all()
            self.update_callback()

            # Maintain connection for 30 seconds until next update
            for _ in range(15):
                await self.client.is_connected()
                await asyncio.sleep(2)

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

    async def update_uuid_debug(self) -> None:
        for uuid in self.uuid_debug:
            try:
                value = await self.client.read_gatt_char(uuid)
                _LOGGER.debug(f'Current value of {uuid}: {self.current_temp}')
                self.uuid_debug[uuid] = str(value)
            except BleakError as e:
                _LOGGER.error(f'Failed to update {uuid}: {e}')

    async def connect(self) -> None:
        connected = False
        for i in range(1, 10 + 1):
            try:
                await self.client.connect()
                await self.client.pair()
                connected = True
                _LOGGER.info(f'Connected to {self.mac_address}')
            except BleakError as e:
                _LOGGER.error(f'Init: {e} on attempt {i}. waiting 30sec')
                asyncio.sleep(30)

        if connected is False:
            self.available = False
            self.update_callback()
            _LOGGER.warning(f'Failed to connect to {self.mac_address} after 10 tries. Will try again in 5min')
            await asyncio.sleep(5 * 60)
            await self.connect()

        try:
            _LOGGER.info(f'Try to subscribe to STATE')
            await self.client.start_notify(STATE_UUID, self.state_notify)
        except BleakError:
            _LOGGER.warning('Failed to subscribe to state attr')

    def state_notify(self, sender: int, data: bytearray):
        _LOGGER.info(f'State from {sender}: {data} ({list(data)})')
        self._state = str(list(data))

    async def update_all(self) -> bool:
        update_attrs = ['led_colour', 'current_temp', 'target_temp', 'battery']
        try:
            await self.client.connect()
            for attr in update_attrs:
                await getattr(self, f'update_{attr}')()
            success = True
        except BleakError as e:
            _LOGGER.error(str(e))
            success = False
        finally:
            await self.client.disconnect()
        return success

    async def disconnect(self) -> None:
        self._loop = False
        with contextlib.suppress(BleakError):
            await self.client.stop_notify(STATE_UUID)
        with contextlib.suppress(BleakError):
            await self.client.disconnect()
