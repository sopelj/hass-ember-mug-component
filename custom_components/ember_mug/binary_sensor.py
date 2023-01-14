"""Binary Sensor Entity for Ember Mug."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator
from .entity import BaseMugEntity

SENSOR_TYPES = {
    "battery.on_charging_base": BinarySensorEntityDescription(
        key="power",
        name="Power",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}


class MugBinarySensor(BaseMugEntity, BinarySensorEntity):
    """Base Entity for Mug Binary Sensors."""

    _domain = "binary_sensor"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug sensor."""
        self.entity_description = SENSOR_TYPES[mug_attr]
        super().__init__(coordinator, mug_attr)

    @property
    def is_on(self) -> bool:
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
    async_add_entities([MugBinarySensor(coordinator, attr) for attr in SENSOR_TYPES])
