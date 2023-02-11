"""Select Entity for Ember Mug."""
from __future__ import annotations

from enum import Enum
import logging
from typing import Literal

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
        option = self.coordinator.get_mug_attr(self._mug_attr)
        return option.value if isinstance(option, Enum) else option


class MugTempUnitSelectEntity(MugSelectEntity):
    """Configurable SelectEntity for a mug temp unit."""

    @property
    def icon(self) -> str:
        """Change icon based on current option."""
        if current := self.current_option:
            unit = (
                "fahrenheit" if current == UnitOfTemperature.FAHRENHEIT else "celsius"
            )
            return f"mdi:temperature-{unit}"
        return "mdi:help-rhombus-outline"

    async def async_select_option(
        self,
        option: Literal["°C", "°F"] | UnitOfTemperature,
    ) -> None:
        """Change the selected option."""
        await self.coordinator.mug.set_temperature_unit(option)


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
