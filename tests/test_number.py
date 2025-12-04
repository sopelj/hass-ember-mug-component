"""Test Text entities."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from ember_mug.consts import DeviceModel
from ember_mug.data import ModelInfo
from homeassistant.components.number import NumberMode
from homeassistant.const import ATTR_ENTITY_ID, UnitOfTemperature
from homeassistant.helpers import entity_registry as er

from custom_components.ember_mug import DOMAIN

from .conftest import setup_platform

if TYPE_CHECKING:
    from ember_mug import EmberMug
    from homeassistant.core import HomeAssistant


async def test_setup_number_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both number entities."""
    assert len(hass.states.async_all()) == 0
    config = await setup_platform(hass, mock_mug, "number")
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    unique_id = f"ember_mug_{config.unique_id}_target_temp"
    entity_id = entity_registry.async_get_entity_id("number", DOMAIN, unique_id)

    target_temp_state = hass.states.get(entity_id)
    assert target_temp_state is not None
    assert target_temp_state.attributes == {
        "friendly_name": "Test Mug Target temperature",
        "device_class": "temperature",
        "max": 63,
        "min": 48.8,
        "mode": NumberMode.BOX,
        "step": 0.1,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
    }
    assert target_temp_state.state == "0.0"

    target_temp_entity = entity_registry.async_get(entity_id)
    assert target_temp_entity.translation_key == "target_temp"
    assert target_temp_entity.original_name == "Target temperature"


async def test_setup_number_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test travel mug also works."""
    mock_mug.data.model_info = ModelInfo(DeviceModel.TRAVEL_MUG_12_OZ)
    assert len(hass.states.async_all()) == 0
    await setup_platform(hass, mock_mug, "number")
    assert len(hass.states.async_all()) == 1


async def test_setup_update_number(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test updating target temp."""
    config = await setup_platform(hass, mock_mug, "number")

    entity_registry = er.async_get(hass)
    unique_id = f"ember_mug_{config.unique_id}_target_temp"
    entity_id = entity_registry.async_get_entity_id("number", DOMAIN, unique_id)
    entity = entity_registry.async_get(entity_id)
    assert entity
    assert not entity.disabled
    target_temp_state = hass.states.get(entity_id)
    assert target_temp_state.state == "0.0"

    with patch.object(mock_mug, "set_target_temp") as mock_set:
        await hass.services.async_call(
            "number",
            "set_value",
            {ATTR_ENTITY_ID: entity_id, "value": 50.0},
            blocking=True,
        )
        mock_set.assert_called_once_with(50.0)
