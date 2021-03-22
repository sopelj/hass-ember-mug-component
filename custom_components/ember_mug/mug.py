"""Reusable class for Ember Mug connection and data."""

import asyncio
from base64 import b64encode
import contextlib
from typing import Callable, Tuple, Union

from bleak import BleakClient
from bleak.exc import BleakError
from homeassistant.helpers.typing import HomeAssistantType

from . import _LOGGER
from .const import (  # UUID_TEMPERATURE_UNIT,
    LIQUID_STATES,
    UUID_BATTERY,
    UUID_DRINK_TEMPERATURE,
    UUID_DSK,
    UUID_LED,
    UUID_LIQUID_LEVEL,
    UUID_LIQUID_STATE,
    UUID_MUG_ID,
    UUID_MUG_NAME,
    UUID_PUSH_EVENT,
    UUID_TARGET_TEMPERATURE,
    UUID_UDSK,
)


def decode_byte_string(data: Union[bytes, bytearray]) -> str:
    """Convert bytes to text as Ember expects."""
    return b64encode(data).decode("utf8")


class EmberMug:
    """Class to connect and communicate with the mug via Bluetooth."""

    def __init__(
        self,
        mac_address: str,
        use_metric: bool,
        async_update_callback: Callable,
        hass: HomeAssistantType,
    ) -> None:
        """Set default values in for mug attributes."""
        self._loop = False
        self._first_run = True
        self.hass = hass
        self.async_update_callback = async_update_callback
        self.mac_address = mac_address
        self.client = BleakClient(mac_address)
        self.use_metric = use_metric
        self.available = True
        self.updates_queued = set()

        self.latest_event_id: int = None
        self.liquid_level: int = None
        self.serial_number = None
        self.led_colour_rgba = [255, 255, 255, 255]
        self.current_temp: float = None
        self.target_temp: float = None
        self.battery: float = None
        self.on_charging_base: bool = None
        self.liquid_state = None
        self.mug_name = None
        self.mug_id: str = None
        self.udsk = None
        self.dsk = None

    @property
    def colour(self) -> str:
        """Return colour as hex value."""
        r, g, b, a = self.led_colour_rgba
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"

    @property
    def liquid_state_label(self) -> str:
        """Return human readable liquid state."""
        return LIQUID_STATES.get(self.liquid_state, str(self.liquid_state))

    async def async_run(self) -> None:
        """Start a the task loop."""
        try:
            self._loop = True
            _LOGGER.info(f"Starting mug loop {self.mac_address}")
            await self.connect()

            while self._loop:
                if not await self.client.is_connected():
                    await self.connect()

                await self.update_all()
                self.updates_queued.clear()
                self.async_update_callback()

                # Maintain connection for 5min seconds until next update
                # We will be notified of most changes during this time
                for _ in range(150):
                    await self.client.is_connected()
                    await self.update_queued_attributes()
                    await asyncio.sleep(2)

        except Exception as e:
            _LOGGER.error(f"An unexpected error occurred during loop {e}. Restarting.")
            self.hass.async_create_task(self.async_run())

    async def _temp_from_bytes(self, temp_bytes: bytearray) -> float:
        """Get temperature from bytearray and convert to fahrenheit if needed."""
        temp = (
            float(int.from_bytes(temp_bytes, byteorder="little", signed=False)) * 0.01
        )
        if self.use_metric is False:
            # Convert to fahrenheit
            temp = (temp * 9 / 5) + 32
        return round(temp, 2)

    async def update_battery(self) -> None:
        """Get Battery percent from mug gatt."""
        battery = await self.client.read_gatt_char(UUID_BATTERY)
        battery_percent = float(battery[0])
        _LOGGER.debug(f"Battery is at {battery_percent}. On base: {battery[1] == 1}")
        self.battery = round(battery_percent, 2)
        self.on_charging_base = battery[1] == 1

    async def update_led_colour(self) -> None:
        """Get RGBA colours from mug gatt."""
        self.led_colour_rgba = list(await self.client.read_gatt_char(UUID_LED))

    async def set_led_colour(self, colour: Tuple[int, int, int, int]) -> None:
        """Set new target temp for mug."""
        _LOGGER.debug(f"Set led colour to {colour}")
        colour = bytearray(colour)  # To RGBA bytearray
        await self.client.is_connected()
        await self.client.write_gatt_char(UUID_LED, colour, False)

    async def update_target_temp(self) -> None:
        """Get target temp form mug gatt."""
        temp_bytes = await self.client.read_gatt_char(UUID_TARGET_TEMPERATURE)
        target_temp = await self._temp_from_bytes(temp_bytes)
        if self.target_temp != target_temp:
            _LOGGER.debug(f"Target temp {self.target_temp}")
            self.target_temp = target_temp

    async def set_target_temp(self, target_temp: float) -> None:
        """Set new target temp for mug."""
        _LOGGER.debug(f"Set target temp to {target_temp}")
        target = bytearray(int(target_temp / 0.01).to_bytes(2, "little"))
        await self.client.is_connected()
        await self.client.write_gatt_char(UUID_TARGET_TEMPERATURE, target, False)

    async def update_current_temp(self) -> None:
        """Get current temp from mug gatt."""
        temp_bytes = await self.client.read_gatt_char(UUID_DRINK_TEMPERATURE)
        current_temp = await self._temp_from_bytes(temp_bytes)
        if self.current_temp != current_temp:
            _LOGGER.debug(f"Current temp {self.current_temp}")
            self.current_temp = current_temp

    async def update_liquid_level(self) -> None:
        """Get liquid level from mug gatt."""
        liquid_level_bytes = await self.client.read_gatt_char(UUID_LIQUID_LEVEL)
        liquid_level = int(liquid_level_bytes[0])
        if self.liquid_level != liquid_level:
            _LOGGER.debug(f"Liquid level now: {self.liquid_level}")
            self.liquid_level = liquid_level

    async def update_liquid_state(self) -> None:
        """Get liquid state from mug gatt."""
        liquid_state_bytes = await self.client.read_gatt_char(UUID_LIQUID_STATE)
        self.liquid_state = int(liquid_state_bytes[0])

    async def update_mug_name(self) -> None:
        """Get mug name from gatt."""
        name_bytes: bytearray = await self.client.read_gatt_char(UUID_MUG_NAME)
        self.mug_name = bytes(name_bytes).decode("utf8")

    async def set_mug_name(self, name: str) -> None:
        """Assign new name to mug."""
        await self.client.is_connected()
        await self.client.write_gatt_char(UUID_MUG_NAME, name.encode("utf8"), False)

    async def update_udsk(self) -> None:
        """Get mug udsk from gatt."""
        self.udsk = str(list(await self.client.read_gatt_char(UUID_UDSK)))

    async def update_dsk(self) -> None:
        """Get mug dsk from gatt."""
        self.dsk = str(list(await self.client.read_gatt_char(UUID_DSK)))

    async def connect(self) -> None:
        """Try 10 times to connect and if we fail wait five minutes and try again. If connected also subscribe to state notifications."""
        connected = False
        for i in range(1, 10 + 1):
            try:
                await self.client.connect()
                await self.client.pair()
                connected = True
                _LOGGER.info(f"Connected to {self.mac_address}")
                break
            except BleakError as e:
                _LOGGER.error(f"Init: {e} on attempt {i}. waiting 30sec")
                asyncio.sleep(30)

        if connected is False:
            self.available = False
            self.async_update_callback()
            _LOGGER.warning(
                f"Failed to connect to {self.mac_address} after 10 tries. Will try again in 2min"
            )
            await asyncio.sleep(2 * 60)
            return await self.connect()

        self.available = True

        if self.serial_number is None:
            try:
                full_mug_id = await self.client.read_gatt_char(UUID_MUG_ID)
                self.mug_id = decode_byte_string(full_mug_id[:6])
                self.serial_number = full_mug_id[7:].decode("utf8")
            except Exception as e:
                _LOGGER.warning(f"Failed to get mug ID {e}")

        try:
            _LOGGER.info("Try to subscribe to Push Events")
            await self.client.start_notify(UUID_PUSH_EVENT, self.push_notify)
        except Exception as e:
            _LOGGER.warning(f"Failed to subscribe to state attr {e}")

    async def update_queued_attributes(self) -> None:
        """Update all attributes in queue."""
        if not self.updates_queued:
            return
        _LOGGER.debug(f"Queued updates {self.updates_queued}")
        queued_attributes = set(self.updates_queued)
        self.updates_queued.clear()
        for attr in queued_attributes:
            await getattr(self, f"update_{attr}")()
        self.async_update_callback()

    def push_notify(self, sender: int, data: bytearray):
        """Push events from the mug to indicate changes."""
        event_id = data[0]
        if self.latest_event_id == event_id:
            return  # Skip to avoid unnecessary calls
        _LOGGER.info(f"Push event received from Mug ({event_id})")
        self.latest_event_id = event_id

        # Check known IDs
        if event_id in [1, 2, 3]:
            # 1, 2 and 3 : Battery Change
            if event_id in [2, 3]:
                # 2 -> Placed on charger, 3 -> Removed from charger
                self.on_charging_base = event_id == 2
            # All indicate changes in battery
            self.updates_queued.add("battery")
        elif event_id == 4:
            # 4 : Check target temp?
            self.updates_queued.add("target_temp")
        elif event_id == 5:
            # 5 : Check current temp
            self.updates_queued.add("current_temp")
        elif event_id == 7:
            # 7 : Check level
            self.updates_queued.add("liquid_level")
        elif event_id == 8:
            # 8 : Check liquid state
            self.updates_queued.add("liquid_state")
        else:
            _LOGGER.warning(f"Unknown event_id pushed: {event_id}")

    async def update_all(self) -> bool:
        """Update all attributes."""
        update_attrs = [
            "led_colour",
            "current_temp",
            "target_temp",
            "battery",
            "liquid_level",
            "liquid_state",
            "mug_name",
            "udsk",
            "dsk",
        ]
        try:
            if not await self.client.is_connected():
                await self.connect()
            for attr in update_attrs:
                await getattr(self, f"update_{attr}")()
            success = True
        except BleakError as e:
            _LOGGER.error(str(e))
            success = False
        return success

    async def disconnect(self) -> None:
        """Stop Loop and disconnect."""
        with contextlib.suppress(BleakError):
            await self.client.stop_notify(UUID_PUSH_EVENT)

        self._loop = False
        with contextlib.suppress(BleakError):
            if self.client and await self.client.is_connected():
                await self.client.disconnect()
