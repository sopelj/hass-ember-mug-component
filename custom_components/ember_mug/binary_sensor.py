"""Binary Sensor Entity for Ember Mug."""
from __future__ import annotations

from typing import Any, Mapping

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MugDataUpdateCoordinator
from .const import DOMAIN


class EmberMugBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base Mug Sensor."""

    coordinator: MugDataUpdateCoordinator
    _sensor_type: str | None = None

    def __init__(self, coordinator: MugDataUpdateCoordinator, entry_id: str) -> None:
        """Init set names for attributes."""
        super().__init__(coordinator)
        self._device = coordinator.ble_device
        self._entry_id = entry_id
        self._last_run_success: bool | None = None
        self._address = coordinator.ble_device.address
        self._attr_name = f"Mug {self._sensor_type or ''}".strip()
        self._attr_unique_id = f"ember_mug_{self._sensor_type or ''}_{entry_id}"
        self.data = coordinator.data or {}

    @property
    def device_info(self) -> DeviceInfo:
        """Pass device information."""
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.available

    @property
    def extra_state_attributes(self) -> Mapping[Any, Any]:
        """Return the state attributes."""
        return {"last_run_success": self._last_run_success}

    @callback
    def _handle_coordinator_update(self, *args: Any) -> None:
        """Handle data update."""
        self.data = self.coordinator.data
        self.async_write_ha_state()


class EmberMugChargingBinarySensor(EmberMugBinarySensorBase):
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
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id
    assert entry_id is not None
    entities: list[BinarySensorEntity] = [
        EmberMugChargingBinarySensor(coordinator, entry_id),
    ]
    async_add_entities(entities)
