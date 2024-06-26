"""Binary Sensor Entity for Ember Mug."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

from .const import MAX_TEMP_CELSIUS, MIN_TEMP_CELSIUS
from .entity import BaseMugValueEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import EmberMugConfigEntry
    from .coordinator import MugDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

NUMBER_TYPES = {
    "target_temp": NumberEntityDescription(
        key="target_temp",
        native_min_value=MIN_TEMP_CELSIUS,
        native_max_value=MAX_TEMP_CELSIUS,
        native_step=0.1,
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
        device_attr: str,
    ) -> None:
        """Initialize the Mug Number."""
        self.entity_description = NUMBER_TYPES[device_attr]
        super().__init__(coordinator, device_attr)


class MugTargetTempNumberEntity(MugNumberEntity):
    """Configurable NumerEntity for the Mug's target temp."""

    @property
    def native_value(self) -> float | None:
        """Return a mug attribute as the state for the sensor."""
        return self.coordinator.target_temp

    async def async_set_native_value(self, value: float) -> None:
        """Set the mug target temp."""
        self.coordinator.ensure_writable()
        await self.coordinator.mug.set_target_temp(value)
        self.coordinator.refresh_from_mug()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EmberMugConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Number Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    coordinator = entry.runtime_data
    async_add_entities(
        [
            MugTargetTempNumberEntity(coordinator, "target_temp"),
        ],
    )
