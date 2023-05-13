"""Test Text entities."""
from __future__ import annotations

from unittest.mock import Mock

from ember_mug import EmberMug
from homeassistant.components.number import NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform


async def test_setup_text_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both text entities."""
    assert len(hass.states.async_all()) == 0
    config = await setup_platform(hass, mock_mug, "number")
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    entity_name = f"number.ember_mug_{config.unique_id}_target_temp"

    name_state = hass.states.get(entity_name)
    assert name_state is not None
    assert name_state.attributes == {
        "friendly_name": "Test Mug Target temperature",
        "device_class": "temperature",
        "max": 100,
        "min": 0,
        "mode": NumberMode.BOX,
        "step": 1,
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
    }
    assert name_state.state == "0.0"

    name_entity = entity_registry.async_get(entity_name)
    assert name_entity.translation_key == "target_temp"
    assert name_entity.original_name == "Target temperature"


async def test_setup_text_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test travel mug also works."""
    mock_mug.is_cup = False
    mock_mug.is_travel_mug = True
    assert len(hass.states.async_all()) == 0
    await setup_platform(hass, mock_mug, "number")
    assert len(hass.states.async_all()) == 1
