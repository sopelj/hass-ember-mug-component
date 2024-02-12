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

from .const import CONF_TARGET_TEMP_BACKUP, DOMAIN, MAX_TEMP_CELSIUS, MIN_TEMP_CELSIUS
from .entity import BaseMugValueEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import MugDataUpdateCoordinator
    from .models import HassMugData


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
        native_value = super().native_value
        if (
            native_value == 0
            and self.coordinator.config_entry
            and (stored_temp := self.coordinator.config_entry.data.get(CONF_TARGET_TEMP_BACKUP))
        ):
            return stored_temp
        return native_value

    async def async_set_native_value(self, value: float) -> None:
        """Set the mug target temp."""
        self.coordinator.ensure_writable()
        await self.coordinator.mug.set_target_temp(value)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Number Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    data: HassMugData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MugTargetTempNumberEntity(data.coordinator, "target_temp"),
        ],
    )
