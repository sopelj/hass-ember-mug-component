"""Binary Sensor Entity for Ember Mug."""
from __future__ import annotations

import logging

from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MUG_NAME_REGEX
from .coordinator import MugDataUpdateCoordinator
from .entity import BaseMugEntity

_LOGGER = logging.getLogger(__name__)

TEXT_TYPES = {
    "name": TextEntityDescription(
        key="name",
        name="Name",
        native_min=1,
        native_max=16,
        pattern=MUG_NAME_REGEX,
        entity_category=EntityCategory.CONFIG,
    ),
}


class MugTextEntity(BaseMugEntity, TextEntity):
    """Base Entity for Mug Binary Sensors."""

    _domain = "text"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug sensor."""
        self.entity_description = TEXT_TYPES[mug_attr]
        super().__init__(coordinator, mug_attr)

    def set_value(self, value: str) -> None:
        """Not needed and we use the Async method."""
        pass

    async def async_set_value(self, value: str) -> None:
        """Set the mug name."""
        await self.coordinator.connection.set_name(value)

    @property
    def native_value(self) -> str | None:
        """Return mug attribute as binary state."""
        return self.coordinator.get_mug_attr(self._mug_attr)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Binary Sensor Entities."""
    assert entry.entry_id is not None
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[MugTextEntity] = [
        MugTextEntity(coordinator, "name"),
    ]
    async_add_entities(entities)
