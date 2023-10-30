"""Test Light entities."""
from __future__ import annotations

from unittest.mock import Mock

from ember_mug import EmberMug
from homeassistant.components.light import ColorMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import setup_platform


async def test_setup_light_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test Light entities."""
    assert len(hass.states.async_all()) == 0
    mock_mug.is_travel_mug = False
    config = await setup_platform(hass, mock_mug, "light")
    assert len(hass.states.async_all()) == 1
    entity_registry = er.async_get(hass)

    entity_name = f"light.ember_mug_{config.unique_id}_led"

    led_state = hass.states.get(entity_name)
    assert led_state is not None
    assert led_state.attributes == {
        "friendly_name": "Test Mug LED",
        "color_mode": ColorMode.RGB,
        "supported_color_modes": [ColorMode.RGB],
        "supported_features": 0,
        "brightness": None,
        "hs_color": None,
        "rgb_color": None,
        "xy_color": None,
    }
    assert led_state.state == "on"

    name_entity = entity_registry.async_get(entity_name)
    assert name_entity.translation_key == "led"
    assert name_entity.original_name == "LED"


async def test_setup_light_travel_mug(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Initialize and test both Binary sensors."""
    assert len(hass.states.async_all()) == 0
    mock_mug.is_travel_mug = True
    await setup_platform(hass, mock_mug, "light")
    assert len(hass.states.async_all()) == 0


async def test_setup_light_cup(
    hass: HomeAssistant,
    mock_mug: EmberMug | Mock,
) -> None:
    """Test cup has no sensors as it cannot be named."""
    mock_mug.is_cup = True
    assert len(hass.states.async_all()) == 0
    await setup_platform(hass, mock_mug, "light")
    assert len(hass.states.async_all()) == 1
