from typing import Dict

import asyncio
from struct import *
from bleak import BleakScanner
from bleak import BleakClient
from bleak import discover

from .const import ALL_UUIDS, TARGET_TEMP_UUID, CURRENT_TEMP_UUID, BATTERY_UUID, LED_COLOUR_UUID, UNKNOWN_NOTIFY_UUID, STATE_UUID


def notification_handler(sender, data):
    """
    Simple notification handler which prints the data received.
    """
    print(f"\n{sender}: {data}")


async def find_mugs():
    try:
        print("Searching..", end='')

        while True:
            print('.', end='')
            devices = await discover()

            for device in devices:
                if device.name == "Ember Ceramic Mug":
                    # We found the ember mug!
                    print(device.address)
                    print(device.name)
                    print(device.details)

                    async with BleakClient(device) as client:
                        self.client = client
                        x = await client.is_connected()
                        print(f"Connected: {x}")
                        y = await client.pair()
                        print(f"Paired: {y}")
    except Exception as e:
        print(f'Error: {e}')


class Mug:
    async def set_led_colour(self, red: int = 255, green: int = 255, blue: int = 255, alpha: int = 255):
        if await self.client.is_connected():
            colour = bytearray([red, green, blue, alpha])
            print('Set colour to', colour)
            await self.client.write_gatt_char(self.uuid_handle_mapping[LED_COLOUR_UUID], colour, True)
        else:
            print('Not connected')

    async def set_target_temp(self, temp: float):     
        if await self.client.is_connected():   
            print("Set to", temp)
            target = bytearray(int(temp / 0.01).to_bytes(2, 'little'))
            print(target)
            resp = await self.client.write_gatt_char(self.uuid_handle_mapping[TARGET_TEMP_UUID], target, True)
            print(resp)
        else:
            print('Not connected')