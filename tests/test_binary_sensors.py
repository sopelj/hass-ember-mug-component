"""Test Binary Sensor entities."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

import pytest
from ember_mug.consts import LiquidState
from ember_mug.data import BatteryInfo
from homeassistant.const import EntityCategory
from homeassistant.helpers import entity_registry as er

from custom_components.ember_mug import DOMAIN

from .conftest import setup_platform

if TYPE_CHECKING:
    from unittest.mock import Mock

    from ember_mug import EmberMug
    from homeassistant.core import HomeAssistant


async def test_setup_binary_sensors(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Binary sensor entities."""
    assert len(hass.states.async_all()) == 0
    config = await setup_platform(hass, mock_mug, "binary_sensor")
    assert len(hass.states.async_all()) == 2
    entity_registry = er.async_get(hass)
    get_binary_sensor_id = partial(entity_registry.async_get_entity_id, "binary_sensor", DOMAIN)

    power_entity_id = get_binary_sensor_id(f"ember_mug_{config.unique_id}_power")
    power_sensor_state = hass.states.get(power_entity_id)

    assert power_sensor_state is not None
    assert power_sensor_state.attributes == {
        "device_class": "plug",
        "friendly_name": "Test Mug Power",
    }
    assert power_sensor_state.state == "unknown"

    power_entity = entity_registry.async_get(power_entity_id)
    assert power_entity.entity_category == EntityCategory.DIAGNOSTIC
    assert power_entity.translation_key == "power"
    assert power_entity.original_name == "Power"

    low_battery_entity_id = get_binary_sensor_id(f"ember_mug_{config.unique_id}_low_battery")
    low_battery_sensor_state = hass.states.get(low_battery_entity_id)
    assert low_battery_sensor_state is not None
    assert low_battery_sensor_state.attributes == {
        "device_class": "battery",
        "friendly_name": "Test Mug Low battery",
    }
    assert low_battery_sensor_state.state == "unknown"

    low_battery_entity = entity_registry.async_get(low_battery_entity_id)
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
    entity_registry = er.async_get(hass)

    entity_id = entity_registry.async_get_entity_id("binary_sensor", DOMAIN, f"ember_mug_{config.unique_id}_power")
    power_sensor_state = hass.states.get(entity_id)
    assert power_sensor_state.state == "on"

    entity_id = entity_registry.async_get_entity_id(
        "binary_sensor",
        DOMAIN,
        f"ember_mug_{config.unique_id}_low_battery",
    )
    low_battery_sensor_state = hass.states.get(entity_id)
    assert low_battery_sensor_state.state == "off"


@pytest.mark.parametrize(
    ("battery_level", "liquid_state", "expected_state"),
    [
        (20, LiquidState.COOLING, "off"),
        (30, LiquidState.HEATING, "off"),
        (20, LiquidState.HEATING, "on"),
    ],
)
async def test_low_battery_normal(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
    battery_level: int,
    liquid_state: LiquidState,
    expected_state: str,
) -> None:
    """Test state when mug is cooling in and battery is not low."""
    mock_mug.data.battery = BatteryInfo(battery_level, True)
    mock_mug.data.liquid_state = liquid_state

    config = await setup_platform(hass, mock_mug, "binary_sensor")
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "binary_sensor",
        DOMAIN,
        f"ember_mug_{config.unique_id}_low_battery",
    )

    low_battery_sensor_state = hass.states.get(entity_id)
    assert low_battery_sensor_state.state == expected_state
