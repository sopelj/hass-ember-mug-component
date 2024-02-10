"""Tests for diagnostics."""
from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

from bleak import BleakError
from ember_mug.consts import (
    DeviceColour,
    DeviceModel,
    DeviceType,
    LiquidState,
    TemperatureUnit,
)
from ember_mug.data import (
    BatteryInfo,
    Colour,
    ModelInfo,
    MugData,
    MugFirmwareInfo,
    MugMeta,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ember_mug import DOMAIN, HassMugData
from custom_components.ember_mug.coordinator import MugDataUpdateCoordinator
from custom_components.ember_mug.diagnostics import async_get_config_entry_diagnostics

from . import DEFAULT_CONFIG_DATA, TEST_BLE_DEVICE, TEST_MAC, TEST_MUG_NAME

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def test_config_entry_diagnostics(hass: HomeAssistant) -> None:
    """Test diagnostics correctly dumps data."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title=TEST_MUG_NAME,
        data=DEFAULT_CONFIG_DATA,
        options=None,
    )
    pink = Colour(244, 0, 161)
    mock_mug = Mock()
    mock_mug.data = MugData(
        model_info=ModelInfo(DeviceModel.MUG_2_10_OZ, DeviceColour.BLACK),
        name=TEST_MUG_NAME,
        meta=MugMeta("test-id", "test-serial"),
        battery=BatteryInfo(33, False),
        firmware=MugFirmwareInfo(15, 200, 10),
        led_colour=pink,
        liquid_state=LiquidState.TARGET_TEMPERATURE,
        liquid_level=20,
        target_temp=45,
        current_temp=53,
    )
    expected_services = {
        "uuid": {
            "characteristics": {
                "uuid": {
                    "value": "test-char",
                    "descriptors": [
                        {"value": "test-descriptor"},
                    ],
                },
            },
        },
    }
    mock_mug.discover_services = AsyncMock(return_value=expected_services)
    mock_mug.debug = True
    mock_mug.device = TEST_BLE_DEVICE
    hass_data = HassMugData(
        coordinator=MugDataUpdateCoordinator(
            hass,
            Mock(),
            mock_mug,
            "unique-id",
            "device-name",
        ),
        mug=mock_mug,
    )
    hass.data[DOMAIN] = {config_entry.entry_id: hass_data, "debug": True}
    dump = await async_get_config_entry_diagnostics(hass, config_entry)
    mock_mug.discover_services.assert_called_once()
    assert dump == {
        "info": {
            "meta_display": "Serial Number: test-serial",
            "model_info": {
                "capacity": 295,
                "colour": DeviceColour.BLACK,
                "device_type": DeviceType.MUG,
                "model": DeviceModel.MUG_2_10_OZ,
                "name": "Ember Mug 2 (10oz)",
            },
            "use_metric": True,
            "name": TEST_MUG_NAME,
            "meta": {"mug_id": "test-id", "serial_number": "test-serial"},
            "debug": False,
            "battery": {"on_charging_base": False, "percent": 33},
            "firmware": {"bootloader": 10, "hardware": 200, "version": 15},
            "led_colour": pink,
            "liquid_state": LiquidState.TARGET_TEMPERATURE,
            "liquid_level": 20,
            "temperature_unit": TemperatureUnit.CELSIUS,
            "current_temp": 53,
            "target_temp": 45,
            "dsk": "",
            "udsk": "",
            "date_time_zone": None,
            "battery_voltage": None,
            "led_colour_display": "#f400a1",
            "liquid_state_display": "Perfect",
            "liquid_level_display": "66.67%",
            "current_temp_display": "53.00°C",
            "target_temp_display": "45.00°C",
            "volume_level": None,
        },
        "services": expected_services,
        "state": "Perfect",
        "address": TEST_MAC,
    }

    # Error
    mock_mug.discover_services.side_effect = BleakError()
    mock_mug.discover_services.reset_mock()
    dump = await async_get_config_entry_diagnostics(hass, config_entry)
    assert "services" not in dump
    mock_mug.discover_services.assert_called_once()

    # Non debug mode.
    mock_mug.debug = False
    mock_mug.discover_services.reset_mock()
    dump = await async_get_config_entry_diagnostics(hass, config_entry)
    assert "services" not in dump
    mock_mug.discover_services.assert_not_called()
