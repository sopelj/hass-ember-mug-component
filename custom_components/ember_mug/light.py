"""Expose the Mug's LEDs as a light entity."""
import logging
from typing import Any

from ember_mug.data import Colour
from homeassistant.components.light import (
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator
from .entity import BaseMugEntity

_LOGGER = logging.getLogger(__name__)


class MugLightEntity(BaseMugEntity, LightEntity):
    """Light entity for Nug LED."""

    _domain = "light"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    entity_description = LightEntityDescription(
        key="led",
        name="LED",
        entity_category=EntityCategory.CONFIG,
    )

    @callback
    def _async_update_attrs(self) -> None:
        """Handle updating _attr values."""
        self._attr_is_on = (
            self.coordinator.available
        )  # it's always on, if the mug is there.
        colour = self.coordinator.data.led_colour
        self._attr_brightness = 255
        self._attr_rgb_color = tuple(colour[:3]) if colour else (255, 255, 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Change the LED colour if defined."""
        _LOGGER.debug(f"Received turn on with {kwargs}")
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            await self.coordinator.mug.set_led_colour(Colour(*rgb))
            self._attr_rgb_color = rgb
            self.async_write_ha_state()
        # Nothing else to do, the light is always on.

    def turn_off(self, **kwargs: Any) -> None:
        """Do nothing, since these lights can't be turned off."""
        _LOGGER.warning("Mug LED cannot be turned off; doing nothing.")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the mug light."""
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MugLightEntity(coordinator, "led_colour")])
