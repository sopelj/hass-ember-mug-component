"""Sensor Entity for Ember Mug."""
from __future__ import annotations

from homeassistant.components.motion_blinds.sensor import ATTR_BATTERY_VOLTAGE
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import voluptuous as vol

from . import MugDataUpdateCoordinator
from .const import (
    DOMAIN,
    MAC_ADDRESS_REGEX,
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

# Schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.matches_regex(MAC_ADDRESS_REGEX),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
    }
)


class EmberMugSensorBase(CoordinatorEntity):
    """Base Mug Sensor."""

    coordinator: MugDataUpdateCoordinator
    _sensor_type: str | None = None

    def __init__(self, coordinator: MugDataUpdateCoordinator, device_id: str) -> None:
        """Init set names for attributes."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_name = f"Mug {self._sensor_type or ''}".strip()
        self._attr_unique_id = f"{self._sensor_type or 'ember_mug'}-{device_id}"

    @property
    def device_info(self):
        """Pass device information."""
        return self.coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and self.coordinator.mug.is_connected
        )


class EmberMugSensor(EmberMugSensorBase, SensorEntity):
    """Base Mug State Sensor."""

    _attr_icon = "mdi:coffee"

    @property
    def native_value(self) -> str:
        """Return information about the contents."""
        return self.coordinator.mug.liquid_state_label

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        mug = self.coordinator.mug
        return {
            "led_colour": mug.colour,
            CONF_TEMPERATURE_UNIT: mug.temperature_unit,
            "latest_push": mug.latest_event_id,
            "on_charging_base": mug.on_charging_base,
            "liquid_level": mug.liquid_level,
            "liquid_state": mug.liquid_state_label,
            "liquid_state_label": mug.liquid_state_label,
            "date_time_zone": mug.date_time_zone,
            "firmware_info": mug.firmware_info,
            "udsk": mug.udsk,
            "dsk": mug.dsk,
            "mug_name": mug.mug_name,
            "mug_id": mug.mug_id,
        }


class EmberMugTemperatureSensor(EmberMugSensorBase, SensorEntity):
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
        super().__init__(coordinator, device_id)
        self._temp_type = temp_type
        self._sensor_type = f"{temp_type} temp"
        self._attr_native_unit_of_measurement = temp_unit

    @property
    def native_value(self):
        """Return sensor state."""
        temp = getattr(self.coordinator.mug, f"{self._temp_type}_temp")
        if temp is not None:
            return round(temp, 2)
        return None

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        return {ATTR_BATTERY_VOLTAGE: self.coordinator.mug.battery_voltage}


class EmberMugBatterySensor(EmberMugSensorBase, SensorEntity):
    """Mug Battery Sensor."""

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
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        return {ATTR_BATTERY_VOLTAGE: self.coordinator.mug.battery_voltage}


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
