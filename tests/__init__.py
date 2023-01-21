"""Tests for this Integration."""
from unittest.mock import patch

from bleak.backends.scanner import AdvertisementData, BLEDevice
from ember_mug.consts import EMBER_BLUETOOTH_NAMES
from home_assistant_bluetooth.models import BluetoothServiceInfoBleak


def patch_async_setup_entry(return_value=True):
    """Patch async setup entry to return True."""
    return patch(
        "custom_components.ember_mug.async_setup_entry",
        return_value=return_value,
    )


MUG_DEVICE_NAME = EMBER_BLUETOOTH_NAMES[0]
TEST_MAC = "AA:BB:CC:DD:EE:FF"
TEST_MUG_NAME = "Test Mug"


MUG_SERVICE_INFO = BluetoothServiceInfoBleak(
    name=MUG_DEVICE_NAME,
    manufacturer_data={89: b"\xfd`0U\x92W"},
    service_data={"": b""},
    service_uuids=["cba20d00-224d-11e6-9fb8-0002a5d5c51b"],
    address=TEST_MAC,
    rssi=-50,
    source="local",
    advertisement=AdvertisementData(
        local_name=MUG_DEVICE_NAME,
        manufacturer_data={},
        service_data={},
        service_uuids=["fc543622-236c-4c94-8fa9-944a3e5353fa"],
        rssi=-127,
        platform_data=((),),
        tx_power=-127,
    ),
    device=BLEDevice(TEST_MAC, MUG_DEVICE_NAME),
    time=0,
    connectable=True,
)
