"""Diagnostics support for Mug."""
from __future__ import annotations

import logging
from typing import Any

from bleak import BleakError
from ember_mug.utils import discover_services
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import HassMugData
from .const import DOMAIN

logger = logging.getLogger(__name__)


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
    if coordinator.mug.debug is True:
        services = None
        try:
            async with coordinator.mug._operation_lock:
                await coordinator.mug._ensure_connection()
                services = await discover_services(coordinator.mug._client)
        except BleakError as e:
            logger.error("Failed to log services, %e", e)

        if services is not None:
            # Ensure bytes are converted into strings for serialization
            for service in services.values():
                for char in service["characteristics"].values():
                    if (value := char["value"]) is not None:
                        char["value"] = str(value)
                    for desc in char["descriptors"]:
                        if (value := desc["value"]) is not None:
                            desc["value"] = str(value)
            data["services"] = services
    return data
