"""Tests for this Integration."""
from unittest.mock import patch

from bleak.backends.scanner import AdvertisementData, BLEDevice
from ember_mug.consts import DEFAULT_NAME
from home_assistant_bluetooth.models import BluetoothServiceInfoBleak
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    UnitOfTemperature,
)

from custom_components.ember_mug import CONF_INCLUDE_EXTRA


def patch_async_setup_entry(return_value=True):
    """Patch async setup entry to return True."""
    return patch(
        "custom_components.ember_mug.async_setup_entry",
        return_value=return_value,
    )


MUG_DEVICE_NAME = DEFAULT_NAME
TEST_MAC = "AA:BB:CC:DD:EE:FF"
TEST_MAC_UNIQUE_ID = TEST_MAC.replace(":", "").lower()
TEST_MUG_NAME = "Test Mug"
TEST_BLE_DEVICE = BLEDevice(TEST_MAC, MUG_DEVICE_NAME, {}, 1)
DEFAULT_CONFIG_DATA = {
    CONF_ADDRESS: TEST_MAC,
    CONF_NAME: TEST_MUG_NAME,
    CONF_TEMPERATURE_UNIT: UnitOfTemperature.CELSIUS,
    CONF_INCLUDE_EXTRA: False,
}
V1_CONFIG_DATA = {
    CONF_MAC: TEST_MAC,
    CONF_NAME: TEST_MUG_NAME,
    CONF_TEMPERATURE_UNIT: "°C",
}

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
        manufacturer_data={0x03C1: b"\x81"},
        service_data={},
        service_uuids=["fc543622-236c-4c94-8fa9-944a3e5353fa"],
        rssi=-127,
        platform_data=((),),
        tx_power=-127,
    ),
    device=TEST_BLE_DEVICE,
    time=0,
    connectable=True,
)
