"""Binary Sensor Entity for Ember Mug."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator
from .entity import BaseMugEntity


class EmberMugChargingBinarySensor(BaseMugEntity, BinarySensorEntity):
    """Mug Battery Sensor."""

    _sensor_type = "on charging base"
    _attr_device_class = BinarySensorDeviceClass.PLUG

    @property
    def is_on(self) -> bool:
        """Return "True" if placed on the charging base."""
        return self.coordinator.mug.battery.on_charging_base


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Entities."""
    assert entry.entry_id is not None
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = [
        EmberMugChargingBinarySensor(coordinator),
    ]
    async_add_entities(entities)
