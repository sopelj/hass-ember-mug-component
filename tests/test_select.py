"""Test Select entities."""
from __future__ import annotations

from unittest.mock import Mock

from ember_mug import EmberMug
from ember_mug.consts import VolumeLevel
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform

TEMP_OPTIONS = [UnitOfTemperature.CELSIUS.value, UnitOfTemperature.FAHRENHEIT.value]


async def test_setup_select_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Select entities."""
    assert len(hass.states.async_all()) == 0
    mock_mug.is_travel_mug = False
    config = await setup_platform(hass, mock_mug, "select")
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    entity_name = f"select.ember_mug_{config.unique_id}_temperature_unit"

    temperature_unit_state = hass.states.get(entity_name)
    assert temperature_unit_state is not None
    assert temperature_unit_state.attributes == {
        "friendly_name": "Test Mug Temperature unit",
        "icon": "mdi:temperature-celsius",
        "options": TEMP_OPTIONS,
    }
    assert temperature_unit_state.state == UnitOfTemperature.CELSIUS

    name_entity = entity_registry.async_get(entity_name)
    assert name_entity.translation_key == "temperature_unit"
    assert name_entity.original_name == "Temperature unit"


async def test_setup_select_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Select entities for Travel Mug."""
    assert len(hass.states.async_all()) == 0
    mock_mug.is_travel_mug = True
    config = await setup_platform(hass, mock_mug, "select")
    assert len(hass.states.async_all()) == 2
    entity_registry = er.async_get(hass)

    base_entity_name = f"select.ember_mug_{config.unique_id}"

    temperature_unit_state = hass.states.get(f"{base_entity_name}_temperature_unit")
    assert temperature_unit_state is not None
    assert temperature_unit_state.attributes == {
        "friendly_name": "Test Mug Temperature unit",
        "icon": "mdi:temperature-celsius",
        "options": TEMP_OPTIONS,
    }
    assert temperature_unit_state.state == UnitOfTemperature.CELSIUS

    name_entity = entity_registry.async_get(f"{base_entity_name}_temperature_unit")
    assert name_entity.translation_key == "temperature_unit"
    assert name_entity.original_name == "Temperature unit"

    volume_level_state = hass.states.get(f"{base_entity_name}_volume_level")
    assert volume_level_state is not None
    assert volume_level_state.attributes == {
        "friendly_name": "Test Mug Volume Level",
        "icon": "mdi:volume-off",
        "options": [v.value for v in VolumeLevel],
    }
    assert volume_level_state.state == "unknown"

    volume_level_entity = entity_registry.async_get(f"{base_entity_name}_volume_level")
    assert volume_level_entity.translation_key == "volume_level"
    assert volume_level_entity.original_name == "Volume Level"


async def test_setup_select_cup(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test cup also only has one Select entity."""
    mock_mug.is_cup = True
    assert len(hass.states.async_all()) == 0
    await setup_platform(hass, mock_mug, "select")
    assert len(hass.states.async_all()) == 1
