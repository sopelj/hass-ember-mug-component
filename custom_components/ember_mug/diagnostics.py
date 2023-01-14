"""Diagnostics support for Mug."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: MugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    had_extra = coordinator.data.include_extra
    coordinator.data.include_extra = True
    data: dict[str, Any] = {
        "info": coordinator.data.formatted_data,
        "state": coordinator.data.liquid_state,
        "address": coordinator.data.device.address,
    }
    if not had_extra:
        coordinator.data.include_extra = False
    return data
