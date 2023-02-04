"""Generic Entity Logic for multiple platforms."""
from __future__ import annotations

import logging
from typing import Any

from ember_mug.consts import TemperatureUnit
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_conversion import TemperatureConverter, UnitOfTemperature

from .coordinator import MugDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def ensure_celsius(
    value: float | None,
    source_unit: UnitOfTemperature | TemperatureUnit,
) -> float | None:
    """Convert unit back to Celsius for a base and round."""
    if value is None:
        return None
    if source_unit != UnitOfTemperature.CELSIUS:
        value = TemperatureConverter.convert(
            value,
            source_unit,
            UnitOfTemperature.CELSIUS,
        )
    return value


class BaseMugEntity(CoordinatorEntity):
    """Generic entity encapsulating common features of an Ember Mug."""

    coordinator: MugDataUpdateCoordinator

    _domain: str = None  # type: ignore[assignment]
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        mug_attr: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        entity_key = self.entity_description.key
        self._mug_attr = mug_attr
        self._address = coordinator.data.device.address
        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"ember_mug_{coordinator.base_unique_id}_{entity_key}"
        self.entity_id = f"{self._domain}.{self._attr_unique_id}"

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


class BaseMugValueEntity(BaseMugEntity):
    """Base Entity that returns a mug attribute as its `native_value`."""

    @property
    def native_value(self) -> Any:
        """Return a mug attribute as the state for the sensor."""
        return self.coordinator.get_mug_attr(self._mug_attr)
