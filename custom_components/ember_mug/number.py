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
from .entity import BaseMugValueEntity

_LOGGER = logging.getLogger(__name__)

NUMBER_TYPES = {
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


class MugNumberEntity(BaseMugValueEntity, NumberEntity):
    """Configurable NumberEntity for a mug attribute."""

    _domain = "number"
    _attr_mode = NumberMode.BOX

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug Number."""
        self.entity_description = NUMBER_TYPES[mug_attr]
        super().__init__(coordinator, mug_attr)


class MugTargetTempNumberEntity(MugNumberEntity):
    """Configurable NumerEntity for the Mug's target temp."""

    async def async_set_native_value(self, value: float) -> None:
        """Set the mug target temp."""
        await self.coordinator.mug.set_target_temp(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Number Entities."""
    assert entry.entry_id is not None
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MugTargetTempNumberEntity(coordinator, "target_temp"),
        ],
    )
