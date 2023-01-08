"""Generic Entity Logic for multiple platforms."""
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MugDataUpdateCoordinator


class BaseMugEntity(CoordinatorEntity):
    """Generic entity encapsulating common features of an Ember Mug."""

    coordinator: MugDataUpdateCoordinator
    _attr_has_entity_name = True

    def __init__(self, coordinator: MugDataUpdateCoordinator, mug_attr: str) -> None:
        """Initialize the entity."""
        self._mug_attr = mug_attr
        base_attr = mug_attr.split(".")[-1]
        self._attr_unique_id = (
            self.entity_id
        ) = f"ember_mug_{coordinator.base_unique_id}_{base_attr}"
        super().__init__(coordinator)
        self.coordinator = coordinator
        # self._attr_unique_id = f"ember_mug_{self._sensor_type or ''}_{entry_id}"
        self._address = coordinator.ble_device.address
        # self._attr_unique_id = coordinator.base_unique_id
        self._attr_device_info = coordinator.device_info

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.available

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "last_updated": self.coordinator.last_updated,
        }

    @callback
    def _async_update_attrs(self) -> None:
        """Update the entity attributes."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        self._async_update_attrs()
        self.async_write_ha_state()
