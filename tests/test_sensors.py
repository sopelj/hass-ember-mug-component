"""Test Sensor entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ember_mug.consts import DeviceModel, LiquidState
from ember_mug.data import ModelInfo
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.helpers import entity_registry as er

from custom_components.ember_mug.const import ICON_DEFAULT, LIQUID_STATE_OPTIONS

from .conftest import setup_platform

if TYPE_CHECKING:
    from unittest.mock import Mock

    from ember_mug import EmberMug
    from homeassistant.core import HomeAssistant


async def test_setup_sensors(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test sensors."""
    assert len(hass.states.async_all()) == 0
    mock_mug.data.model_info = ModelInfo(DeviceModel.MUG_2_10_OZ)
    mock_mug.data.liquid_state = LiquidState.STANDBY
    config = await setup_platform(hass, mock_mug, "sensor")
    assert len(hass.states.async_all()) == 4
    entity_registry = er.async_get(hass)

    sensor_base_name = f"sensor.ember_mug_{config.unique_id}"

    # Liquid state sensor
    liquid_state_state = hass.states.get(f"{sensor_base_name}_state")
    assert liquid_state_state is not None
    assert liquid_state_state.attributes == {
        "device_class": "enum",
        "firmware_info": None,
        "friendly_name": "Test Mug State",
        "colour": "unknown",
        "icon": ICON_DEFAULT,
        "options": LIQUID_STATE_OPTIONS,
        "raw_state": 0,
    }
    assert liquid_state_state.state == "standby"
    liquid_state_sensor = entity_registry.async_get(f"{sensor_base_name}_state")
    assert liquid_state_sensor.translation_key == "state"
    assert liquid_state_sensor.original_name == "State"

    # Liquid level sensor
    liquid_level_state = hass.states.get(f"{sensor_base_name}_liquid_level")
    assert liquid_level_state is not None
    assert liquid_level_state.attributes == {
        "capacity": 295,
        "friendly_name": "Test Mug Liquid level",
        "icon": "mdi:cup-water",
        "raw_liquid_level": 0,
        "unit_of_measurement": PERCENTAGE,
    }
    assert liquid_level_state.state == "0"

    liquid_level_sensor = entity_registry.async_get(f"{sensor_base_name}_liquid_level")
    assert liquid_level_sensor.translation_key == "liquid_level"
    assert liquid_level_sensor.original_name == "Liquid level"

    # Temperature sensor
    current_temp_state = hass.states.get(f"{sensor_base_name}_current_temp")
    assert current_temp_state is not None
    assert current_temp_state.attributes == {
        "device_class": "temperature",
        "friendly_name": "Test Mug Current temperature",
        "icon": "mdi:thermometer-off",
        "native_value": 0.0,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
    }
    assert current_temp_state.state == "0.0"

    current_temp_sensor = entity_registry.async_get(f"{sensor_base_name}_current_temp")
    assert current_temp_sensor.translation_key == "current_temp"
    assert current_temp_sensor.original_name == "Current temperature"

    # Battery percent sensor
    battery_percent_state = hass.states.get(f"{sensor_base_name}_battery_percent")
    assert battery_percent_state is not None
    assert battery_percent_state.attributes == {
        "battery_charging": None,
        "device_class": "battery",
        "friendly_name": "Test Mug Battery",
        "unit_of_measurement": "%",
        "state_class": SensorStateClass.MEASUREMENT,
    }
    assert battery_percent_state.state == "unknown"

    battery_percent_sensor = entity_registry.async_get(
        f"{sensor_base_name}_battery_percent",
    )
    assert battery_percent_sensor.translation_key == "battery_percent"
    assert battery_percent_sensor.original_name == "Battery"
