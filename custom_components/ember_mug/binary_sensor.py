"""Binary Sensor Entity for Ember Mug."""
from __future__ import annotations

import logging

from ember_mug.consts import LiquidState
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
from .models import HassMugData

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "battery.on_charging_base": BinarySensorEntityDescription(
        key="power",
        name="Power",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "battery.percent": BinarySensorEntityDescription(
        key="low_battery",
        name="Low battery",
        device_class=BinarySensorDeviceClass.BATTERY,
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
    def is_on(self) -> bool | None:
        """Return mug attribute as binary state."""
        return self.coordinator.get_mug_attr(self._mug_attr)


class MugLowBatteryBinarySensor(MugBinarySensor):
    """Warn about low battery."""

    @property
    def is_on(self) -> bool | None:
        """Return "on" if battery is low."""
        battery_percent = self.coordinator.get_mug_attr(self._mug_attr)
        if battery_percent is None:
            return None
        if battery_percent > 25:
            # Even if heating, it is not low yet.
            return False
        state = self.coordinator.get_mug_attr("liquid_state")
        # If heating or at target temperature the battery will discharge faster.
        if state in (LiquidState.HEATING, LiquidState.TARGET_TEMPERATURE):
            return True
        return bool(battery_percent < 15)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Binary Sensor Entities."""
    assert entry.entry_id is not None
    data: HassMugData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MugBinarySensor(data.coordinator, "battery.on_charging_base"),
            MugLowBatteryBinarySensor(data.coordinator, "battery.percent"),
        ],
    )
