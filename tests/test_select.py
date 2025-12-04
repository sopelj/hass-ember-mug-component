"""Test Select entities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from ember_mug.consts import DeviceModel, VolumeLevel
from ember_mug.data import ModelInfo
from homeassistant.const import ATTR_ENTITY_ID, UnitOfTemperature
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er

from custom_components.ember_mug import DOMAIN

from .conftest import setup_platform

if TYPE_CHECKING:
    from ember_mug import EmberMug
    from homeassistant.core import HomeAssistant


TEMP_OPTIONS = [UnitOfTemperature.CELSIUS.value, UnitOfTemperature.FAHRENHEIT.value]


async def test_setup_select_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Select entities."""
    assert len(hass.states.async_all()) == 0
    mock_mug.data.model_info = ModelInfo(DeviceModel.MUG_2_10_OZ)
    config = await setup_platform(hass, mock_mug, "select")
    assert len(hass.states.async_all()) == 2
    entity_registry = er.async_get(hass)

    entity_id = entity_registry.async_get_entity_id("select", DOMAIN, f"ember_mug_{config.unique_id}_temperature_unit")

    temperature_unit_state = hass.states.get(entity_id)
    assert temperature_unit_state is not None
    assert temperature_unit_state.attributes == {
        "friendly_name": "Test Mug Temperature unit",
        "icon": "mdi:temperature-celsius",
        "options": TEMP_OPTIONS,
    }
    assert temperature_unit_state.state == UnitOfTemperature.CELSIUS

    name_entity = entity_registry.async_get(entity_id)
    assert name_entity.translation_key == "temperature_unit"
    assert name_entity.original_name == "Temperature unit"


async def test_setup_select_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Select entities for Travel Mug."""
    assert len(hass.states.async_all()) == 0
    mock_mug.data.model_info = ModelInfo(DeviceModel.TRAVEL_MUG_12_OZ)
    config = await setup_platform(hass, mock_mug, "select")
    assert len(hass.states.async_all()) == 3
    entity_registry = er.async_get(hass)

    entity_id = entity_registry.async_get_entity_id(
        "select",
        DOMAIN,
        f"ember_travel_mug_{config.unique_id}_temperature_unit",
    )

    temperature_unit_state = hass.states.get(entity_id)
    assert temperature_unit_state is not None
    assert temperature_unit_state.attributes == {
        "friendly_name": "Test Mug Temperature unit",
        "icon": "mdi:temperature-celsius",
        "options": TEMP_OPTIONS,
    }
    assert temperature_unit_state.state == UnitOfTemperature.CELSIUS

    name_entity = entity_registry.async_get(entity_id)
    assert name_entity.translation_key == "temperature_unit"
    assert name_entity.original_name == "Temperature unit"

    entity_id = entity_registry.async_get_entity_id(
        "select",
        DOMAIN,
        f"ember_travel_mug_{config.unique_id}_volume_level",
    )
    volume_level_state = hass.states.get(entity_id)
    assert volume_level_state is not None
    assert volume_level_state.attributes == {
        "friendly_name": "Test Mug Volume Level",
        "icon": "mdi:volume-off",
        "options": [v.value for v in VolumeLevel],
    }
    assert volume_level_state.state == "unknown"

    volume_level_entity = entity_registry.async_get(entity_id)
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
    assert len(hass.states.async_all()) == 2


async def test_setup_update_temp_unit(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test updating temperature unit."""
    config = await setup_platform(hass, mock_mug, "select")

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("select", DOMAIN, f"ember_mug_{config.unique_id}_temperature_unit")
    entity = entity_registry.async_get(entity_id)
    assert entity
    temp_unit_state = hass.states.get(entity_id)
    assert temp_unit_state.state == UnitOfTemperature.CELSIUS

    with patch.object(mock_mug, "set_temperature_unit") as mock_set:
        await hass.services.async_call(
            "select",
            "select_option",
            {ATTR_ENTITY_ID: entity_id, "option": UnitOfTemperature.FAHRENHEIT.value},
            blocking=True,
        )
        mock_set.assert_called_once_with(UnitOfTemperature.FAHRENHEIT)


async def test_setup_update_temp_preset(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test updating temperature preset."""
    mock_mug.data.target_temp = 55
    config = await setup_platform(hass, mock_mug, "select")

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "select",
        DOMAIN,
        f"ember_mug_{config.unique_id}_temperature_preset",
    )
    entity = entity_registry.async_get(entity_id)
    assert entity
    temp_unit_state = hass.states.get(entity_id)
    assert temp_unit_state.state == "latte"

    with patch.object(mock_mug, "set_target_temp") as mock_set:
        await hass.services.async_call(
            "select",
            "select_option",
            {ATTR_ENTITY_ID: entity_id, "option": "cappuccino"},
            blocking=True,
        )
        mock_set.assert_called_once_with(56)

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "select",
            "select_option",
            {ATTR_ENTITY_ID: entity_id, "option": "Invalid"},
            blocking=True,
        )


async def test_update_volume_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test updating volume level."""
    mock_mug.data.model_info = ModelInfo(DeviceModel.TRAVEL_MUG_12_OZ)
    mock_mug.data.volume_level = VolumeLevel.LOW
    config = await setup_platform(hass, mock_mug, "select")

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id(
        "select",
        DOMAIN,
        f"ember_travel_mug_{config.unique_id}_volume_level",
    )
    entity = entity_registry.async_get(entity_id)
    assert entity
    assert not entity.disabled
    volume_level_state = hass.states.get(entity_id)
    assert volume_level_state.state == "low"

    with patch.object(mock_mug, "set_volume_level") as mock_set:
        await hass.services.async_call(
            "select",
            "select_option",
            {ATTR_ENTITY_ID: entity_id, "option": "high"},
            blocking=True,
        )
        mock_set.assert_called_once_with(VolumeLevel.HIGH)
