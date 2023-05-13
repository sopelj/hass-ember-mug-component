"""Test Text entities."""
from __future__ import annotations

from unittest.mock import Mock, patch

from ember_mug import EmberMug
from homeassistant.components.number import NumberMode
from homeassistant.const import ATTR_ENTITY_ID, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform


async def test_setup_number_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both number entities."""
    assert len(hass.states.async_all()) == 0
    config = await setup_platform(hass, mock_mug, "number")
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    entity_id = f"number.ember_mug_{config.unique_id}_target_temp"

    target_temp_state = hass.states.get(entity_id)
    assert target_temp_state is not None
    assert target_temp_state.attributes == {
        "friendly_name": "Test Mug Target temperature",
        "device_class": "temperature",
        "max": 100,
        "min": 0,
        "mode": NumberMode.BOX,
        "step": 1,
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
    mock_mug.is_cup = False
    mock_mug.is_travel_mug = True
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
    entity_id = f"number.ember_mug_{config.unique_id}_target_temp"
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
