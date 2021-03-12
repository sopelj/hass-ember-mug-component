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


async def get_services(client):
    for service in client.services:
        print("[Service] {0}: {1}".format(service.uuid, service.description))
        for char in service.characteristics:
            value_type = None
            if "read" in char.properties:
                try:
                    data = await client.read_gatt_char(char.uuid)
                    value_type = type(data)
                    value = bytes(data)
                except Exception as e:
                    value = str(e).encode()
            else:
                value = None
            print(
                f"\t[Characteristic] {char.uuid}: ({','.join(char.properties)}) | Name: {char.description}, Value: {value}, Type: {value_type}"
            )
            for descriptor in char.descriptors:
                value = await client.read_gatt_descriptor(descriptor.handle)
                print(
                    f"\t\t[Descriptor] {descriptor.uuid}: (Handle: {descriptor.handle}) | Value: {bytes(value)} | Type: {type(value)}"
                )


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
    # https://github.com/pledi/EmberControl/blob/d19b7867ae5572a7da0e2ca9e68866fd28c613ed/main.py#L95
    search = True
    client = None
    keep_alive = True
    uuid_handle_mapping: Dict[str, int]

    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self.uuid_handle_mapping = {}

    async def setup(self):
        try:
            # try to connect to the mug
            async with BleakClient(self.mac_address) as client:
                self.client = client
                connected_mac = await client.is_connected()
                print(f"Connected: {connected_mac}")

                self.uuid_handle_mapping = {
                    uuid: self.client.services.get_characteristic(uuid).handle
                    for uuid in ALL_UUIDS
                }
                
                #await get_services(client)
                print(self.client.services.get_characteristic(LED_COLOUR_UUID).handle)
                # await self.set_led_colour(204, 2, 170)
                await self.set_target_temp(55.5)
                await self.fetch_led_colour()
                await self.fetch_battery()
                await self.fetch_target_temp()

                # https://github.com/hbldh/bleak/blob/develop/examples/enable_notifications.py
                await client.start_notify(UNKNOWN_NOTIFY_UUID, notification_handler)
                await asyncio.sleep(5.0)

                # we are connected, get the settings we need.
                while self.keep_alive:
                    # We stay in here to keep the client alive
                    # once keepConnectionAlive is set to false
                    # the client will also disconnect automatically
                    print(".")
                    await asyncio.sleep(2)
                    self.keep_alive = await self.client.is_connected()

        except Exception as e:
            # await self.client.stop_notify(STATE_UUID)
            print('Error: {}'.format(e))

    async def fetch_led_colour(self):
        if await self.client.is_connected():
            c = await self.client.read_gatt_char(LED_COLOUR_UUID)
            colour = c[0], c[1], c[2], c[3]
            print(f"Current colour is {colour}")
        else:
            print('Not connected')

    async def set_led_colour(self, red: int = 255, green: int = 255, blue: int = 255, alpha: int = 255):
        if await self.client.is_connected():
            colour = bytearray([red, green, blue, alpha])
            print('Set colour to', colour)
            await self.client.write_gatt_char(self.uuid_handle_mapping[LED_COLOUR_UUID], colour, True)
        else:
            print('Not connected')


    async def fetch_battery(self):
        if await self.client.is_connected():
            current_battery = await self.client.read_gatt_char(BATTERY_UUID)
            print('Battery is', float(current_battery[0]))
        else:
            print('Not connected')

    async def fetch_target_temp(self):
        if await self.client.is_connected():
            current_temp = await self.client.read_gatt_char(TARGET_TEMP_UUID)
            print(current_temp)
            current = float(int.from_bytes(current_temp, byteorder='little', signed=False)) * 0.01
            print('Current temp', current)
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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Mug('C9:0F:59:D6:33:F9').setup())
    except (KeyboardInterrupt, SystemExit) as e:
        logging.info(f"{e.__class__.__name__} received")