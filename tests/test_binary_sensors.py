"""Test Binary Sensor entities."""
from __future__ import annotations

from unittest.mock import Mock

from ember_mug import EmberMug
from ember_mug.consts import LiquidState
from ember_mug.data import BatteryInfo
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform


async def test_setup_binary_sensors(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Binary sensor entities."""
    assert len(hass.states.async_all()) == 0
    config = await setup_platform(hass, mock_mug, "binary_sensor")
    assert len(hass.states.async_all()) == 2
    entity_registry = er.async_get(hass)

    sensor_base_name = f"binary_sensor.ember_mug_{config.unique_id}"

    power_sensor_state = hass.states.get(f"{sensor_base_name}_power")
    assert power_sensor_state is not None
    assert power_sensor_state.attributes == {
        "device_class": "plug",
        "friendly_name": "Test Mug Power",
    }
    assert power_sensor_state.state == "unknown"

    power_entity = entity_registry.async_get(f"{sensor_base_name}_power")
    assert power_entity.entity_category == EntityCategory.DIAGNOSTIC
    assert power_entity.translation_key == "power"
    assert power_entity.original_name == "Power"

    low_battery_sensor_state = hass.states.get(f"{sensor_base_name}_low_battery")
    assert low_battery_sensor_state is not None
    assert low_battery_sensor_state.attributes == {
        "device_class": "battery",
        "friendly_name": "Test Mug Low battery",
    }
    assert low_battery_sensor_state.state == "unknown"

    low_battery_entity = entity_registry.async_get(f"{sensor_base_name}_low_battery")
    assert low_battery_entity.entity_category == EntityCategory.DIAGNOSTIC
    assert low_battery_entity.translation_key == "low_battery"
    assert low_battery_entity.original_name == "Low battery"


async def test_plugged_in_and_charged(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test state when plugged in and charged."""
    mock_mug.data.battery = BatteryInfo(100, True)

    config = await setup_platform(hass, mock_mug, "binary_sensor")
    sensor_base_name = f"binary_sensor.ember_mug_{config.unique_id}"

    power_sensor_state = hass.states.get(f"{sensor_base_name}_power")
    assert power_sensor_state.state == "on"

    low_battery_sensor_state = hass.states.get(f"{sensor_base_name}_low_battery")
    assert low_battery_sensor_state.state == "off"


async def test_cooling_and_normal(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test state when mug is cooling in and battery is not low."""
    mock_mug.data.battery = BatteryInfo(20, True)
    mock_mug.data.liquid_state = LiquidState.COOLING

    config = await setup_platform(hass, mock_mug, "binary_sensor")
    sensor_name = f"binary_sensor.ember_mug_{config.unique_id}_low_battery"

    low_battery_sensor_state = hass.states.get(sensor_name)
    assert low_battery_sensor_state.state == "off"


async def test_heating_and_normal(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test state when mug is heating in and battery is not low."""
    mock_mug.data.battery = BatteryInfo(30, True)
    mock_mug.data.liquid_state = LiquidState.HEATING

    config = await setup_platform(hass, mock_mug, "binary_sensor")
    sensor_name = f"binary_sensor.ember_mug_{config.unique_id}_low_battery"

    low_battery_sensor_state = hass.states.get(sensor_name)
    assert low_battery_sensor_state.state == "off"


async def test_cooling_and_low(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test state when mug is heating in and battery is low."""
    mock_mug.data.battery = BatteryInfo(20, True)
    mock_mug.data.liquid_state = LiquidState.HEATING

    config = await setup_platform(hass, mock_mug, "binary_sensor")
    sensor_name = f"binary_sensor.ember_mug_{config.unique_id}_low_battery"

    low_battery_sensor_state = hass.states.get(sensor_name)
    assert low_battery_sensor_state.state == "on"
