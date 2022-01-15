"""Sensor Entity for Ember Mug."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_CHARGING,
    CONF_ID,
    CONF_NAME,
    CONF_RGB,
    CONF_TEMPERATURE_UNIT,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import MugDataUpdateCoordinator
from .const import (
    ATTR_BATTERY_VOLTAGE,
    DOMAIN,
    ICON_DEFAULT,
    ICON_EMPTY,
    LIQUID_STATE_TEMP_ICONS,
    SERVICE_SET_LED_COLOUR,
    SERVICE_SET_MUG_NAME,
    SERVICE_SET_TARGET_TEMP,
)
from .services import (
    SET_LED_COLOUR_SCHEMA,
    SET_MUG_NAME_SCHEMA,
    SET_TARGET_TEMP_SCHEMA,
    set_led_colour,
    set_mug_name,
    set_target_temp,
)


class EmberMugSensorBase(CoordinatorEntity, SensorEntity):
    """Base Mug Sensor."""

    coordinator: MugDataUpdateCoordinator
    _sensor_type: str | None = None

    def __init__(self, coordinator: MugDataUpdateCoordinator, device_id: str) -> None:
        """Init set names for attributes."""
        self._device_id = device_id
        self._attr_name = f"Mug {self._sensor_type or ''}".strip()
        self._attr_unique_id = f"{self._sensor_type or 'ember_mug'}-{device_id}"
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Pass device information."""
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and self.coordinator.mug.is_connected
        )


class EmberMugSensor(EmberMugSensorBase):
    """Base Mug State Sensor."""

    @property
    def icon(self) -> str | None:
        """Change icon based on state."""
        return ICON_EMPTY if self.state == "Empty" else ICON_DEFAULT

    @property
    def native_value(self) -> str:
        """Return information about the contents."""
        return self.coordinator.mug.liquid_state_label

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        mug = self.coordinator.mug
        return {
            CONF_NAME: mug.mug_name,
            CONF_ID: mug.mug_id,
            CONF_RGB: mug.colour,
            CONF_TEMPERATURE_UNIT: mug.temperature_unit,
            "date_time_zone": mug.date_time_zone,
            "firmware_info": mug.firmware_info,
            "udsk": mug.udsk,
            "dsk": mug.dsk,
        }


class EmberMugLiquidLevelSensor(EmberMugSensorBase):
    """Liquid Level Sensor."""

    _attr_icon = "mdi:cup-water"
    _sensor_type = "liquid level"
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> float | int:
        """Return information about the liquid level."""
        if liquid_level := self.coordinator.mug.liquid_level:
            return round(liquid_level / 30 * 100, 2)
        return 0


class EmberMugTemperatureSensor(EmberMugSensorBase):
    """Mug Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        temp_type: str,
        temp_unit: str,
        device_id: str,
    ) -> None:
        """Initialize a new temperature sensor."""
        self._sensor_type = f"{temp_type} temp"
        self._temp_type = temp_type
        self._attr_native_unit_of_measurement = temp_unit
        super().__init__(coordinator, device_id)

    @property
    def icon(self) -> str | None:
        """Set icon based on temperature."""
        if self._sensor_type != "current_temp":
            return "mdi:thermometer"
        icon = LIQUID_STATE_TEMP_ICONS.get(
            self.coordinator.mug.liquid_state, "thermometer"
        )
        return f"mdi:{icon}"

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        temp = getattr(self.coordinator.mug, f"{self._temp_type}_temp")
        if temp is not None:
            return round(temp, 2)
        return None


class EmberMugBatterySensor(EmberMugSensorBase):
    """Mug Battery Sensor."""

    _sensor_type = "battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        battery_percentage = self.coordinator.mug.battery
        if battery_percentage is not None:
            return round(battery_percentage, 2)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        return {
            ATTR_BATTERY_VOLTAGE: self.coordinator.mug.battery_voltage,
            ATTR_BATTERY_CHARGING: self.coordinator.mug.on_charging_base,
        }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Entities."""
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        "coordinator"
    ]
    device_id = config_entry.unique_id
    assert device_id is not None
    temp_unit = (
        TEMP_FAHRENHEIT if coordinator.unit_of_measurement == "F" else TEMP_CELSIUS
    )
    entities: list[SensorEntity] = [
        EmberMugSensor(coordinator, device_id),
        EmberMugLiquidLevelSensor(coordinator, device_id),
        EmberMugTemperatureSensor(coordinator, "target", temp_unit, device_id),
        EmberMugTemperatureSensor(coordinator, "current", temp_unit, device_id),
        EmberMugBatterySensor(coordinator, device_id),
    ]
    async_add_entities(entities)

    # Setup Services
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_SET_LED_COLOUR, SET_LED_COLOUR_SCHEMA, set_led_colour
    )
    platform.async_register_entity_service(
        SERVICE_SET_TARGET_TEMP, SET_TARGET_TEMP_SCHEMA, set_target_temp
    )
    platform.async_register_entity_service(
        SERVICE_SET_MUG_NAME, SET_MUG_NAME_SCHEMA, set_mug_name
    )
