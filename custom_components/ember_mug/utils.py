from typing import Dict

from bleak import BleakScanner
from bleak import BleakClient
from bleak import discover

from .const import ALL_UUIDS, TARGET_TEMP_UUID, CURRENT_TEMP_UUID, BATTERY_UUID, LED_COLOUR_UUID, UNKNOWN_NOTIFY_UUID, STATE_UUID


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
