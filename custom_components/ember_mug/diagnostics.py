"""Diagnostics support for Mug."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import HassMugData
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    hass_data: HassMugData = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass_data.coordinator
    data: dict[str, Any] = {
        "info": coordinator.data.as_dict(),
        "state": coordinator.data.liquid_state_display,
        "address": coordinator.mug.device.address,
    }
    return data
