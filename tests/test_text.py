"""Test Text entities."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ember_mug.consts import MUG_NAME_PATTERN, DeviceModel
from ember_mug.data import ModelInfo
from homeassistant.components.text import TextMode
from homeassistant.components.text.const import DOMAIN as TEXT_DOMAIN
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform

if TYPE_CHECKING:
    from unittest.mock import Mock

    from ember_mug import EmberMug
    from homeassistant.core import HomeAssistant


async def test_setup_text_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both text entities."""
    mock_mug.data.model_info = ModelInfo(DeviceModel.MUG_2_10_OZ)
    assert len(hass.states.async_all()) == 0
    config = await setup_platform(hass, mock_mug, TEXT_DOMAIN)
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    entity_name = f"text.ember_mug_{config.unique_id}_name"

    name_state = hass.states.get(entity_name)
    assert name_state is not None
    assert name_state.attributes == {
        "friendly_name": "Test Mug Name",
        "max": 16,
        "min": 1,
        "mode": TextMode.TEXT,
        "pattern": MUG_NAME_PATTERN,
    }
    assert name_state.state == "EMBER"

    name_entity = entity_registry.async_get(entity_name)
    assert name_entity.translation_key == "name"
    assert name_entity.original_name == "Name"


async def test_setup_text_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test travel mug also works."""
    mock_mug.data.name = "EMBER"
    mock_mug.data.model_info = ModelInfo(DeviceModel.TRAVEL_MUG_12_OZ)
    assert len(hass.states.async_all()) == 0
    await setup_platform(hass, mock_mug, TEXT_DOMAIN)
    assert len(hass.states.async_all()) == 1


async def test_setup_text_cup(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test cup has no sensors as it cannot be named."""
    mock_mug.is_cup = True
    assert len(hass.states.async_all()) == 0
    await setup_platform(hass, mock_mug, TEXT_DOMAIN)
    assert len(hass.states.async_all()) == 0
