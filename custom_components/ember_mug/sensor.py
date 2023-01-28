"""Sensor Entity for Ember Mug."""
from __future__ import annotations

from typing import Any

from ember_mug.consts import LiquidState
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_BATTERY_CHARGING, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MugDataUpdateCoordinator
from .const import (
    ATTR_BATTERY_VOLTAGE,
    DOMAIN,
    ICON_DEFAULT,
    ICON_EMPTY,
    LIQUID_STATE_MAPPING,
    LIQUID_STATE_OPTIONS,
    LIQUID_STATE_TEMP_ICONS,
)
from .entity import BaseMugValueEntity, format_temp

SENSOR_TYPES = {
    "liquid_state": SensorEntityDescription(
        key="state",
        name="State",
        translation_key="liquid_state",
        device_class=SensorDeviceClass.ENUM,
        options=LIQUID_STATE_OPTIONS,
    ),
    "liquid_level": SensorEntityDescription(
        key="liquid_level",
        name="Liquid Level",
        icon="mdi:cup-water",
        native_precision=2,
        native_unit_of_measurement=PERCENTAGE,
    ),
    "current_temp": SensorEntityDescription(
        key="current_temp",
        name="Current Temperature",
        native_precision=2,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "battery.percent": SensorEntityDescription(
        key="battery_percent",
        name="Battery",
        native_precision=2,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}


class EmberMugSensor(BaseMugValueEntity, SensorEntity):
    """Representation of a Mug sensor."""

    _domain = "sensor"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug sensor."""
        self.entity_description = SENSOR_TYPES[mug_attr]
        super().__init__(coordinator, mug_attr)


class EmberMugStateSensor(EmberMugSensor):
    """Base Mug State Sensor."""

    _attr_name = None

    @property
    def icon(self) -> str | None:
        """Change icon based on state."""
        return ICON_EMPTY if self.state == LiquidState.EMPTY else ICON_DEFAULT

    @property
    def native_value(self) -> str | None:
        """Return liquid state key."""
        state = super().native_value
        if state:
            return LIQUID_STATE_MAPPING[state.value].value
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        data = self.coordinator.data
        return {
            "date_time_zone": data.date_time_zone,
            "firmware_info": data.firmware,
            "udsk": data.udsk,
            "dsk": data.dsk,
            "raw_state": data.liquid_state,
            **super().extra_state_attributes,
        }


class EmberMugLiquidLevelSensor(EmberMugSensor):
    """Liquid Level Sensor."""

    @property
    def native_value(self) -> float | int:
        """Return information about the liquid level."""
        liquid_level: float | None = super().native_value
        if liquid_level:
            # 30 -> Full
            # 5, 6 -> Low
            # 0 -> Empty
            return liquid_level / 30 * 100
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        return {
            "raw_liquid_level": self.coordinator.data.liquid_level,
            **super().extra_state_attributes,
        }


class EmberMugTemperatureSensor(EmberMugSensor):
    """Mug Temperature sensor."""

    @property
    def icon(self) -> str | None:
        """Set icon based on temperature."""
        if self._mug_attr != "current_temp":
            return "mdi:thermometer"
        icon = LIQUID_STATE_TEMP_ICONS.get(
            self.coordinator.data.liquid_state,
            "thermometer",
        )
        return f"mdi:{icon}"

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        return format_temp(super().native_value, self.coordinator.data.temperature_unit)


class EmberMugBatterySensor(EmberMugSensor):
    """Mug Battery Sensor."""

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        data = self.coordinator.data
        return {
            ATTR_BATTERY_VOLTAGE: data.battery_voltage,
            ATTR_BATTERY_CHARGING: data.battery.on_charging_base
            if data.battery
            else None,
            **super().extra_state_attributes,
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Entities."""
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entry_id = entry.entry_id
    assert entry_id is not None
    entities: list[EmberMugSensor] = [
        EmberMugStateSensor(coordinator, "liquid_state"),
        EmberMugLiquidLevelSensor(coordinator, "liquid_level"),
        EmberMugTemperatureSensor(coordinator, "current_temp"),
        EmberMugBatterySensor(coordinator, "battery.percent"),
    ]
    async_add_entities(entities)
