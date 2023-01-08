"""Sensor Entity for Ember Mug."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_CHARGING,
    CONF_NAME,
    CONF_RGB,
    CONF_TEMPERATURE_UNIT,
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MugDataUpdateCoordinator
from .const import (
    ATTR_BATTERY_VOLTAGE,
    DOMAIN,
    ICON_DEFAULT,
    ICON_EMPTY,
    LIQUID_STATE_TEMP_ICONS,
    MUG_DEVICE_CLASS,
    SERVICE_SET_LED_COLOUR,
    SERVICE_SET_MUG_NAME,
    SERVICE_SET_TARGET_TEMP,
)
from .entity import BaseMugEntity
from .services import (
    SET_LED_COLOUR_SCHEMA,
    SET_MUG_NAME_SCHEMA,
    SET_TARGET_TEMP_SCHEMA,
    set_led_colour,
    set_mug_name,
    set_target_temp,
)

SENSOR_TYPES = {
    "liquid_state_display": SensorEntityDescription(
        key="liquid_state_display",
        name="Mug State",
    ),
    "liquid_level": SensorEntityDescription(
        key="liquid_level",
        name="Mug Liquid Level",
        icon="mdi:cup-water",
        native_unit_of_measurement=PERCENTAGE,
    ),
    "battery.percent": SensorEntityDescription(
        key="battery",
        name="Mug Battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "target_temp": SensorEntityDescription(
        key="target_temp",
        name="Mug Target Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "current_temp": SensorEntityDescription(
        key="current_temp",
        name="Mug Current Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
}


class BaseEmberMugSensor(BaseMugEntity, SensorEntity):
    """Representation of a Mug sensor."""

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the Mug sensor."""
        super().__init__(coordinator, mug_attr)
        self.entity_description = SENSOR_TYPES[mug_attr]

    @property
    def native_value(self) -> Any:
        """Return a mug attribute as the state for the sensor."""
        return self.coordinator.get_mug_attr(self._mug_attr)


class EmberMugSensor(BaseEmberMugSensor):
    """Base Mug State Sensor."""

    _attr_device_class = MUG_DEVICE_CLASS

    @property
    def icon(self) -> str | None:
        """Change icon based on state."""
        return ICON_EMPTY if self.state == "Empty" else ICON_DEFAULT

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        mug = self.coordinator.mug
        return {
            CONF_NAME: mug.name,
            CONF_RGB: mug.led_colour_display,
            CONF_TEMPERATURE_UNIT: mug.temperature_unit,
            "date_time_zone": mug.date_time_zone,
            "firmware_info": mug.firmware,
            "udsk": mug.udsk,
            "dsk": mug.dsk,
        }


class EmberMugLiquidLevelSensor(BaseEmberMugSensor):
    """Liquid Level Sensor."""

    @property
    def native_value(self) -> float | int:
        """Return information about the liquid level."""
        liquid_level: float | None = super().native_value
        if liquid_level:
            return round(liquid_level / 30 * 100, 2)
        return 0


class EmberMugTemperatureSensor(BaseEmberMugSensor):
    """Mug Temperature sensor."""

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        sensor_attr: str,
        temp_unit: str,
    ) -> None:
        """Initialize a new temperature sensor."""
        self._attr_native_unit_of_measurement = temp_unit
        super().__init__(coordinator, sensor_attr)

    @property
    def icon(self) -> str | None:
        """Set icon based on temperature."""
        if self._mug_attr != "current_temp":
            return "mdi:thermometer"
        icon = LIQUID_STATE_TEMP_ICONS.get(
            self.coordinator.mug.liquid_state,
            "thermometer",
        )
        return f"mdi:{icon}"

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        temp: float | None = super().native_value
        if temp is not None:
            return round(temp, 2)
        return None


class EmberMugBatterySensor(BaseEmberMugSensor):
    """Mug Battery Sensor."""

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        battery_percent: float | None = super().native_value
        return round(battery_percent, 2) if battery_percent is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        mug = self.coordinator.mug
        return {
            ATTR_BATTERY_VOLTAGE: mug.battery_voltage,
            ATTR_BATTERY_CHARGING: mug.battery.on_charging_base
            if mug.battery
            else None,
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
    temp_unit = (
        UnitOfTemperature.FAHRENHEIT
        if coordinator.mug.use_metric is False
        else UnitOfTemperature.CELSIUS
    )
    entities: list[BaseMugEntity] = [
        EmberMugSensor(coordinator, "liquid_state_display"),
        EmberMugLiquidLevelSensor(coordinator, "liquid_level"),
        EmberMugTemperatureSensor(coordinator, "target_temp", temp_unit),
        EmberMugTemperatureSensor(coordinator, "current_temp", temp_unit),
        EmberMugBatterySensor(coordinator, "battery.percent"),
    ]
    async_add_entities(entities)

    # Setup Services
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_LED_COLOUR,
        SET_LED_COLOUR_SCHEMA,
        set_led_colour,
    )
    platform.async_register_entity_service(
        SERVICE_SET_TARGET_TEMP,
        SET_TARGET_TEMP_SCHEMA,
        set_target_temp,
    )
    platform.async_register_entity_service(
        SERVICE_SET_MUG_NAME,
        SET_MUG_NAME_SCHEMA,
        set_mug_name,
    )
