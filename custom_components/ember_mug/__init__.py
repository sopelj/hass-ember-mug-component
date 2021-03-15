import logging

from homeassistant import core

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Ember Mug component."""
    # @TODO: Add setup code.
    return True
