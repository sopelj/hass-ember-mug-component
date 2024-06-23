"""Select Entity for Ember Mug."""

from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING, Literal

from ember_mug.consts import VolumeLevel
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import CONF_PRESETS, CONF_PRESETS_UNIT, DEFAULT_PRESETS
from .entity import BaseMugEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import EmberMugConfigEntry
    from .coordinator import MugDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

TEMPERATURE_UNITS = [t.value for t in (UnitOfTemperature.CELSIUS, UnitOfTemperature.FAHRENHEIT)]
VOLUME_LEVELS = [v.value for v in VolumeLevel]
SELECT_TYPES = {
    "temperature_unit": SelectEntityDescription(
        key="temperature_unit",
        options=TEMPERATURE_UNITS,
        entity_category=EntityCategory.CONFIG,
    ),
    "temperature_preset": SelectEntityDescription(
        key="temperature_preset",
        entity_category=EntityCategory.CONFIG,
    ),
    "volume_level": SelectEntityDescription(
        key="volume_level",
        options=VOLUME_LEVELS,
        entity_category=EntityCategory.CONFIG,
    ),
}


class MugSelectEntity(BaseMugEntity, SelectEntity):
    """Configurable SelectEntity for a mug attribute."""

    _domain = "select"

    def __init__(
        self,
        coordinator: MugDataUpdateCoordinator,
        device_attr: str,
    ) -> None:
        """Initialize the Device select entity."""
        self.entity_description = SELECT_TYPES[device_attr]
        super().__init__(coordinator, device_attr)

    @property
    def current_option(self) -> str | None:
        """Return a mug attribute as the state for the current option."""
        option = self.coordinator.get_device_attr(self._device_attr)
        return option.value if isinstance(option, Enum) else option


class MugTempUnitSelectEntity(MugSelectEntity):
    """Configurable SelectEntity for a mug temp unit."""

    @property
    def icon(self) -> str:
        """Change icon based on current option."""
        if current := self.current_option:
            unit = "fahrenheit" if current == UnitOfTemperature.FAHRENHEIT else "celsius"
            return f"mdi:temperature-{unit}"
        return "mdi:help-rhombus-outline"

    async def async_select_option(
        self,
        option: Literal["°C", "°F"] | UnitOfTemperature,
    ) -> None:
        """Change the selected option."""
        await self.coordinator.mug.set_temperature_unit(option)
        self.coordinator.refresh_from_mug()


class MugVolumeLevelSelectEntity(MugSelectEntity):
    """Configurable SelectEntity for the travel mug volume level."""

    @property
    def icon(self) -> str:
        """Change icon based on current option."""
        if current := self.current_option:
            return f"mdi:volume-{current}"
        return "mdi:volume-off"

    async def async_select_option(
        self,
        option: Literal["high", "medium", "low"] | VolumeLevel,
    ) -> None:
        """Change the selected option."""
        self.coordinator.ensure_writable()
        if isinstance(option, str):
            option = VolumeLevel(option)
        await self.coordinator.mug.set_volume_level(option)
        self.coordinator.refresh_from_mug()


class MugTemperaturePresetSelectEntity(MugSelectEntity):
    """Configurable SelectEntity to set the mug temperature from a list of presets."""

    _attr_icon = "mdi:format-list-bulleted"

    def __init__(
        self,
        presets: dict[str, float],
        presets_unit: UnitOfTemperature,
        coordinator: MugDataUpdateCoordinator,
        device_attr: str,
    ) -> None:
        """Set temperature presets and select options base on configs."""
        super().__init__(coordinator, device_attr)
        if presets_unit != UnitOfTemperature.CELSIUS and coordinator.mug.data.use_metric:
            presets = {
                label: TemperatureConverter.convert(
                    temp,
                    presets_unit,
                    UnitOfTemperature.CELSIUS,
                )
                for label, temp in presets.items()
            }
        self._presets = presets
        self._temp_to_labels: dict[float, str] = {v: k for k, v in presets.items()}
        self._attr_options = list(presets)

    @property
    def current_option(self) -> str | None:
        """Return selected option if found current temp is one of the presets."""
        return self._temp_to_labels.get(self.coordinator.target_temp, None)

    async def async_select_option(self, option: str) -> None:
        """Change the target temp of the mug based on preset."""
        if not (target_temp := self._presets.get(option)):
            raise ValueError("Invalid Option")
        await self.coordinator.mug.set_target_temp(target_temp)
        self.coordinator.refresh_from_mug()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EmberMugConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Select Entities."""
    if entry.entry_id is None:
        raise ValueError("Missing config entry ID")
    coordinator = entry.runtime_data
    preset_unit = entry.options.get(CONF_PRESETS_UNIT, UnitOfTemperature.CELSIUS)
    temp_presets = entry.options.get(CONF_PRESETS, DEFAULT_PRESETS)
    entities = [
        MugTemperaturePresetSelectEntity(temp_presets, preset_unit, coordinator, "temperature_preset"),
        MugTempUnitSelectEntity(coordinator, "temperature_unit"),
    ]
    if coordinator.mug.has_attribute("volume_level"):
        entities.append(
            MugVolumeLevelSelectEntity(coordinator, "volume_level"),
        )
    async_add_entities(entities)
