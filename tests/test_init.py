"""Test component setup."""
from homeassistant.setup import async_setup_component

from custom_components.ember_mug.const import DOMAIN


async def test_async_setup(hass, enable_custom_integrations):
    """Test the component gets set up."""
    assert await async_setup_component(hass, DOMAIN, {}) is True
