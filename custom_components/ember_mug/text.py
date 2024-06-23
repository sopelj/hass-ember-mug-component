"""Text Entity for Ember Mug."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ember_mug.consts import MUG_NAME_PATTERN
from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.helpers.entity import EntityCategory

from .entity import BaseMugValueEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MugDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

TEXT_TYPES = {
    "name": TextEntityDescription(
        key="name",
        native_min=1,
        native_max=16,
        pattern=MUG_NAME_PATTERN,
        entity_category=EntityCategory.CONFIG,
    ),
}


class MugTextEntity(BaseMugValueEntity, TextEntity):
    """Configurable Text Entity for text mug attribute."""

    _domain = "text"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        device_attr: str,
    ) -> None:
        """Initialize the Mug sensor."""
        self.entity_description = TEXT_TYPES[device_attr]
        super().__init__(coordinator, device_attr)

    @property
    def native_value(self) -> str:
        """Return a mug attribute as the state for the sensor."""
        return super().native_value or "EMBER"

    async def async_set_value(self, value: str) -> None:
        """Set the mug name."""
        self.coordinator.ensure_writable()
        await self.coordinator.mug.set_name(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Text Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    coordinator = entry.runtime_data
    entities = []
    if coordinator.mug.has_attribute("name"):
        entities = [MugTextEntity(coordinator, attr) for attr in TEXT_TYPES]
    async_add_entities(entities)
