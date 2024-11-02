"""Tests for this Integration."""

from unittest.mock import patch

from bleak.backends.scanner import AdvertisementData, BLEDevice
from ember_mug.consts import (
    DEFAULT_NAME,
    EMBER_BLE_SIG,
    MugCharacteristic,
    TemperatureUnit,
)
from home_assistant_bluetooth import SOURCE_LOCAL, BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS, CONF_MAC, CONF_NAME, CONF_TEMPERATURE_UNIT

from custom_components.ember_mug import CONF_DEBUG


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
}
CONFIG_DATA_V1 = {
    CONF_MAC: TEST_MAC,
    CONF_NAME: TEST_MUG_NAME,
    CONF_TEMPERATURE_UNIT: "°C",
}
CONFIG_DATA_V2 = {
    CONF_ADDRESS: TEST_MAC,
    CONF_NAME: TEST_MUG_NAME,
    CONF_TEMPERATURE_UNIT: TemperatureUnit.CELSIUS,
    CONF_DEBUG: True,
}

MUG_SERVICE_UUID = str(MugCharacteristic.STANDARD_SERVICE)
DEFAULT_MUG_ADVERTISEMENT_DATA = AdvertisementData(
    local_name=MUG_DEVICE_NAME,
    manufacturer_data={EMBER_BLE_SIG: b"\x81"},
    service_data={},
    service_uuids=[MUG_SERVICE_UUID],
    rssi=-127,
    platform_data=((),),
    tx_power=-127,
)
MUG_SERVICE_INFO = BluetoothServiceInfoBleak(
    name=MUG_DEVICE_NAME,
    manufacturer_data={EMBER_BLE_SIG: b"\xfd`0U\x92W"},
    service_data={"": b""},
    service_uuids=[MUG_SERVICE_UUID],
    address=TEST_MAC,
    rssi=-50,
    source=SOURCE_LOCAL,
    advertisement=DEFAULT_MUG_ADVERTISEMENT_DATA,
    tx_power=-127,
    device=TEST_BLE_DEVICE,
    time=0,
    connectable=True,
)
