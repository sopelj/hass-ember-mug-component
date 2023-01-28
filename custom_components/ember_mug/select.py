"""Select Entity for Ember Mug."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator
from .entity import BaseMugEntity

_LOGGER = logging.getLogger(__name__)

TEMPERATURE_UNITS = [
    t.value for t in (UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT)
]
SELECT_TYPES = {
    "temperature_unit": SelectEntityDescription(
        key="temperature_unit",
        name="Temperature Unit",
        options=TEMPERATURE_UNITS,
        entity_category=EntityCategory.CONFIG,
    ),
}


class MugSelectEntity(BaseMugEntity, SelectEntity):
    """Configurable SelectEntity for a mug attribute."""

    _domain = "select"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug select."""
        self.entity_description = SELECT_TYPES[mug_attr]
        super().__init__(coordinator, mug_attr)

    @property
    def current_option(self) -> str | None:
        """Return a mug attribute as the state for the current option."""
        return self.coordinator.get_mug_attr(self._mug_attr)


class MugTempUnitSelectEntity(MugSelectEntity):
    """Configurable SelectEntity for a mug temp unit."""

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.connection.set_temperature_unit(option)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Select Entities."""
    assert entry.entry_id is not None
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MugTempUnitSelectEntity(coordinator, "temperature_unit"),
        ],
    )
