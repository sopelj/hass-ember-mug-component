"""Test Switch entities."""
from __future__ import annotations

from typing import TYPE_CHECKING

from ember_mug.consts import DeviceModel
from ember_mug.data import ModelInfo
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform

if TYPE_CHECKING:
    from unittest.mock import Mock

    from ember_mug import EmberMug
    from homeassistant.core import HomeAssistant


async def test_setup_switch_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test Light entities."""
    assert len(hass.states.async_all()) == 0
    mock_mug.data.target_temp = 65
    mock_mug.data.model_info = ModelInfo(DeviceModel.MUG_2_10_OZ)
    config = await setup_platform(hass, mock_mug, Platform.SWITCH)
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    entity_name = f"switch.ember_mug_{config.unique_id}_temperature_control"

    switch_state = hass.states.get(entity_name)
    assert switch_state is not None
    assert switch_state.attributes == {
        "friendly_name": "Test Mug Temperature Control",
    }
    assert switch_state.state == "on"

    switch_entity = entity_registry.async_get(entity_name)
    assert switch_entity.translation_key == "temperature_control"
    assert switch_entity.original_name == "Temperature Control"
