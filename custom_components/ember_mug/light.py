"""Expose the Mug's LEDs as a light entity."""
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
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import _LOGGER, MugDataUpdateCoordinator
from .entity import BaseMugEntity


class MugLightEntity(BaseMugEntity, LightEntity):
    """Light entity for Nug LED."""

    _domain = "light"
    _attr_brightness = 255
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    entity_description = LightEntityDescription(
        key="led",
        name="LED",
    )

    @callback
    def _async_update_attrs(self) -> None:
        """Handle updating _attr values."""
        self._attr_is_on = self.coordinator.available  # it's always on, if the mug is.
        colour = self.coordinator.data.led_colour
        self._attr_rgb_color = tuple(colour[:3]) if colour else (255, 255, 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Change the LED colour if defined."""
        _LOGGER.debug("Received turn on with kwargs %s", kwargs)
        if ATTR_RGB_COLOR in kwargs:
            rgb = kwargs[ATTR_RGB_COLOR]
            await self.coordinator.connection.ensure_connection()
            await self.coordinator.connection.set_led_colour(Colour(*rgb))
            self._attr_rgb_color = rgb
            self.async_write_ha_state()
        # Nothing else to do, the light is always on.

    def turn_on(self, **kwargs: Any) -> None:
        """Do nothing, since these lights can't be turned on."""
        pass

    def turn_off(self, **kwargs: Any) -> None:
        """Do nothing, since these lights can't be turned off."""
        pass


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the mug light."""
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MugLightEntity(coordinator, "led_colour")])
