"""Expose the Mug's LEDs as a light entity."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ember_mug.data import Colour
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import BaseMugEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .models import HassMugData


_LOGGER = logging.getLogger(__name__)


class MugLightEntity(BaseMugEntity, LightEntity):
    """Light entity for Nug LED."""

    _domain = "light"
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}

    entity_description = LightEntityDescription(
        key="led",
        entity_category=EntityCategory.CONFIG,
    )

    @property
    def is_on(self) -> bool | None:
        """The light is always on if it is available."""
        return self.coordinator.available or None

    @callback
    def _async_update_attrs(self) -> None:
        """Handle updating _attr values."""
        colour = self.coordinator.data.led_colour
        self._attr_brightness = colour.brightness
        self._attr_rgb_color = tuple(colour[:3]) if colour else (255, 255, 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Change the LED colour if defined."""
        _LOGGER.debug(f"Received turn on with {kwargs}")
        rgb, brightness = self.coordinator.mug.data.led_colour[:3], 255
        if (rgb := kwargs.get(ATTR_RGB_COLOR)) or (brightness := kwargs.get(ATTR_BRIGHTNESS)):
            await self.coordinator.mug.set_led_colour(Colour(*rgb, brightness))
            self._attr_rgb_color = tuple(rgb)
            self._attr_brightness = brightness
            self.async_write_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Do nothing, since these lights can't be turned off."""
        _LOGGER.warning(
            "%s LED cannot be turned off; doing nothing.",
            self.coordinator.mug.model_name,
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the mug light."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    data: HassMugData = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if data.mug.is_travel_mug is False:
        entities = [MugLightEntity(data.coordinator, "led_colour")]
    async_add_entities(entities)
