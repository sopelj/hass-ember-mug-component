"""Sensor Entity for Ember Mug."""
from __future__ import annotations

from typing import Any, Mapping

from homeassistant.components.bluetooth.passive_update_coordinator import (
    PassiveBluetoothCoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_CHARGING,
    ATTR_CONNECTIONS,
    CONF_ID,
    CONF_NAME,
    CONF_RGB,
    CONF_TEMPERATURE_UNIT,
    PERCENTAGE,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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


class EmberMugSensorBase(PassiveBluetoothCoordinatorEntity, SensorEntity):
    """Base Mug Sensor."""

    coordinator: MugDataUpdateCoordinator
    _sensor_type: str | None = None

    def __init__(self, coordinator: MugDataUpdateCoordinator) -> None:
        """Init set names for attributes."""
        super().__init__(coordinator)

        self._device = coordinator.ble_device
        self._last_run_success: bool | None = None
        self._address = coordinator.ble_device.address
        self._attr_unique_id = f"{coordinator.base_unique_id}_{self._sensor_type}"
        self._attr_name = f"Mug {self._sensor_type or ''}".strip()
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_BLUETOOTH, self._address)},
            manufacturer="Ember",
            model="Ember Ceramic Mug",
            name=coordinator.device_name,
        )
        if ":" not in self._address:
            return
        self._attr_device_info[ATTR_CONNECTIONS].add(
            (dr.CONNECTION_NETWORK_MAC, self._address),
        )

    @property
    def data(self) -> dict[str, Any]:
        """Return coordinator data for this entity."""
        return self.coordinator.data

    @property
    def extra_state_attributes(self) -> Mapping[Any, Any]:
        """Return the state attributes."""
        return {"last_run_success": self._last_run_success}


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
            "encoded_dsk": str(mug.dsk),
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
    ) -> None:
        """Initialize a new temperature sensor."""
        self._sensor_type = f"{temp_type} temp"
        self._temp_type = temp_type
        self._attr_native_unit_of_measurement = temp_unit
        super().__init__(coordinator)

    @property
    def icon(self) -> str | None:
        """Set icon based on temperature."""
        if self._sensor_type != "current_temp":
            return "mdi:thermometer"
        icon = LIQUID_STATE_TEMP_ICONS.get(
            self.coordinator.mug.liquid_state,
            "thermometer",
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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Entities."""
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    device_id = entry.unique_id
    assert device_id is not None
    temp_unit = TEMP_FAHRENHEIT if coordinator.mug.use_metric == "F" else TEMP_CELSIUS
    entities: list[SensorEntity] = [
        EmberMugSensor(coordinator),
        EmberMugLiquidLevelSensor(coordinator),
        EmberMugTemperatureSensor(coordinator, "target", temp_unit),
        EmberMugTemperatureSensor(coordinator, "current", temp_unit),
        EmberMugBatterySensor(coordinator),
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
