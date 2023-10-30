"""Select Entity for Ember Mug."""
from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Literal

from ember_mug.consts import VolumeLevel
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN
from .entity import BaseMugEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import HassMugData
    from .coordinator import MugDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

TEMPERATURE_UNITS = [t.value for t in (UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT)]
VOLUME_LEVELS = [v.value for v in VolumeLevel]
SELECT_TYPES = {
    "temperature_unit": SelectEntityDescription(
        key="temperature_unit",
        options=TEMPERATURE_UNITS,
        entity_category=EntityCategory.CONFIG,
    ),
    "volume_level": SelectEntityDescription(
        key="volume_level",
        options=VOLUME_LEVELS,
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
            unit = "fahrenheit" if current == UnitOfTemperature.FAHRENHEIT else "celsius"
            return f"mdi:temperature-{unit}"
        return "mdi:help-rhombus-outline"

    async def async_select_option(
        self,
        option: Literal["°C", "°F"] | UnitOfTemperature,
    ) -> None:
        """Change the selected option."""
        await self.coordinator.mug.set_temperature_unit(option)


class MugVolumeLevelSelectEntity(MugSelectEntity):
    """Configurable SelectEntity for the travel mug volume level."""

    @property
    def icon(self) -> str:
        """Change icon based on current option."""
        if current := self.current_option:
            return f"mdi:volume-{current}"
        return "mdi:volume-off"

    async def async_select_option(
        self,
        option: Literal["high", "medium", "low"] | VolumeLevel,
    ) -> None:
        """Change the selected option."""
        if isinstance(option, str):
            option = VolumeLevel(option)
        await self.coordinator.mug.set_volume_level(option)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Select Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    data: HassMugData = hass.data[DOMAIN][entry.entry_id]
    entities = [
        MugTempUnitSelectEntity(data.coordinator, "temperature_unit"),
    ]
    if data.mug.is_travel_mug:
        entities.append(
            MugVolumeLevelSelectEntity(data.coordinator, "volume_level"),
        )
    async_add_entities(entities)
