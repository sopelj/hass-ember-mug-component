"""Binary Sensor Entity for Ember Mug."""
from __future__ import annotations

import logging

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator
from .entity import BaseMugEntity

_LOGGER = logging.getLogger(__name__)

TEXT_TYPES = {
    "target_temp": NumberEntityDescription(
        key="target_temp",
        name="Target Temperature",
        native_max_value=100,
        native_min_value=0,
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
}


class MugNumberEntity(BaseMugEntity, NumberEntity):
    """Base Entity for Mug Binary Sensors."""

    _domain = "number"
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug sensor."""
        self.entity_description = TEXT_TYPES[mug_attr]
        super().__init__(coordinator, mug_attr)

    @property
    def native_value(self) -> float | None:
        """Return mug attribute as temp."""
        temp = self.coordinator.get_mug_attr(self._mug_attr)
        # TODO: convert to Celsius
        if temp:
            return round(temp, 2)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the mug target temp."""
        await self.coordinator.connection.set_target_temp(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Binary Sensor Entities."""
    assert entry.entry_id is not None
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[MugNumberEntity] = [
        MugNumberEntity(coordinator, "target_temp"),
    ]
    async_add_entities(entities)
