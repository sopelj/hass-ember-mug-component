"""Test Sensor entities."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

import pytest
from ember_mug.consts import DeviceModel, LiquidState, TemperatureUnit
from ember_mug.data import ModelInfo
from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.helpers import entity_registry as er
from homeassistant.util.unit_system import (
    METRIC_SYSTEM,
    US_CUSTOMARY_SYSTEM,
    UnitSystem,
)

from custom_components.ember_mug.const import DOMAIN, ICON_DEFAULT, LIQUID_STATE_OPTIONS

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
    mock_mug.data.temperature_unit = TemperatureUnit.CELSIUS
    mock_mug.data.current_temp = 55.1
    config = await setup_platform(hass, mock_mug, "sensor")
    assert len(hass.states.async_all()) == 4
    entity_registry = er.async_get(hass)

    get_sensor_id = partial(entity_registry.async_get_entity_id, "sensor", DOMAIN)

    # Liquid state sensor
    state_entity_id = get_sensor_id(f"ember_mug_{config.unique_id}_state")
    liquid_state_state = hass.states.get(state_entity_id)
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
    liquid_state_sensor = entity_registry.async_get(state_entity_id)
    assert liquid_state_sensor.translation_key == "state"
    assert liquid_state_sensor.original_name == "State"

    # Liquid level sensor
    level_entity_id = get_sensor_id(f"ember_mug_{config.unique_id}_liquid_level")
    liquid_level_state = hass.states.get(level_entity_id)
    assert liquid_level_state is not None
    assert liquid_level_state.attributes == {
        "capacity": 295,
        "friendly_name": "Test Mug Liquid level",
        "icon": "mdi:cup-water",
        "raw_liquid_level": 0,
        "unit_of_measurement": PERCENTAGE,
    }
    assert liquid_level_state.state == "0"

    liquid_level_sensor = entity_registry.async_get(level_entity_id)
    assert liquid_level_sensor.translation_key == "liquid_level"
    assert liquid_level_sensor.original_name == "Liquid level"

    # Temperature sensor
    current_temp_entity_id = get_sensor_id(f"ember_mug_{config.unique_id}_current_temp")
    current_temp_state = hass.states.get(current_temp_entity_id)
    assert current_temp_state is not None
    assert current_temp_state.attributes == {
        "device_class": "temperature",
        "friendly_name": "Test Mug Current temperature",
        "icon": "mdi:thermometer-off",
        "native_value": 55.1,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
    }
    assert current_temp_state.state == "55.1"

    current_temp_sensor = entity_registry.async_get(current_temp_entity_id)
    assert current_temp_sensor.translation_key == "current_temp"
    assert current_temp_sensor.original_name == "Current temperature"

    # Battery percent sensor
    battery_entity_id = get_sensor_id(f"ember_mug_{config.unique_id}_battery_percent")
    battery_percent_state = hass.states.get(battery_entity_id)
    assert battery_percent_state is not None
    assert battery_percent_state.attributes == {
        "battery_charging": None,
        "device_class": "battery",
        "friendly_name": "Test Mug Battery",
        "unit_of_measurement": "%",
        "state_class": SensorStateClass.MEASUREMENT,
    }
    assert battery_percent_state.state == "unknown"

    battery_percent_sensor = entity_registry.async_get(battery_entity_id)
    assert battery_percent_sensor.translation_key == "battery_percent"
    assert battery_percent_sensor.original_name == "Battery"


@pytest.mark.xfail
@pytest.mark.parametrize(
    ("system", "mug_unit", "temp", "expected_state"),
    [
        (METRIC_SYSTEM, TemperatureUnit.CELSIUS, 55.145, 55.145),
        (METRIC_SYSTEM, TemperatureUnit.FAHRENHEIT, 55.145, 131.261),
        (US_CUSTOMARY_SYSTEM, TemperatureUnit.FAHRENHEIT, 100.145, 100.145),
        (US_CUSTOMARY_SYSTEM, TemperatureUnit.CELSIUS, 100.145, 37.85833),
    ],
)
async def test_sensor_unit_conversion(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
    system: UnitSystem,
    mug_unit: TemperatureUnit,
    temp: float,
    expected_state: float,
) -> None:
    """Initialize and test sensors."""
    hass.config.units = system
    assert len(hass.states.async_all()) == 0
    mock_mug.data.model_info = ModelInfo(DeviceModel.MUG_2_10_OZ)
    mock_mug.data.temperature_unit = mug_unit
    mock_mug.data.current_temp = temp
    config = await setup_platform(hass, mock_mug, "sensor")
    assert len(hass.states.async_all()) == 4

    entity_registry = er.async_get(hass)
    sensor_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"ember_mug_{config.unique_id}_current_temp")
    assert sensor_id is not None
    current_temp_state = hass.states.get(sensor_id)

    assert current_temp_state is not None
    # Temperature sensor
    assert current_temp_state.attributes == {
        "device_class": "temperature",
        "friendly_name": "Test Mug Current temperature",
        "icon": "mdi:thermometer-off",
        "native_value": temp,
        "state_class": SensorStateClass.MEASUREMENT,
        "unit_of_measurement": (
            UnitOfTemperature.FAHRENHEIT if system == US_CUSTOMARY_SYSTEM else UnitOfTemperature.CELSIUS
        ),
    }
    assert current_temp_state.state == str(expected_state)
