"""Switch entities."""
from __future__ import annotations

import logging
from functools import cached_property
from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.const import EntityCategory

from . import DOMAIN
from .entity import BaseMugEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import HassMugData
    from .coordinator import MugDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = {
    "target_temp": SwitchEntityDescription(
        key="temperature_control",
        entity_category=EntityCategory.CONFIG,
    ),
}


class MugSwitchEntity(BaseMugEntity, SwitchEntity):
    """Configurable SelectEntity for a mug attribute."""

    _domain = "switch"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        device_attr: str,
    ) -> None:
        """Initialize the Device select entity."""
        self.entity_description = SWITCH_TYPES[device_attr]
        super().__init__(coordinator, device_attr)


class MugTemperatureControlEntity(MugSwitchEntity):
    """Switch entity for controlling temperature control."""

    @property
    def icon(self) -> str:
        """Set icon based on device state."""
        return "mdi:sun-snowflake" if self.is_on else "mdi:sun-snowflake-variant"

    @property
    def is_on(self) -> bool:
        """It is on if the target temp is not zero."""
        return bool(self.coordinator.mug.data.target_temp)

    @cached_property
    def _entry_mug_data(self) -> HassMugData:
        """Shortcut to accessing entry data."""
        return self.hass.data[DOMAIN][self.registry_entry.config_entry_id]

    async def turn_on(self, **kwargs: Any) -> None:
        """Turn heating/cooling on if there is a stored target temp."""
        if not self.coordinator.mug.data.target_temp and self._entry_mug_data.target_temp:
            await self.coordinator.mug.set_target_temp(self._entry_mug_data.target_temp)

    async def turn_off(self, **kwargs: Any) -> None:
        """Turn heating/cooling off if it is not already."""
        if (target_temp := self.coordinator.mug.data.target_temp) not in (0, None):
            self._entry_mug_data.target_temp = target_temp
            await self.coordinator.mug.set_target_temp(0)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Switch Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    data: HassMugData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MugTemperatureControlEntity(data.coordinator, "target_temp")])
