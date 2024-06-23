"""Diagnostics support for Mug."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from bleak import BleakError

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import EmberMugConfigEntry


logger = logging.getLogger(__name__)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: EmberMugConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    data: dict[str, Any] = {
        "info": coordinator.data,
        "state": coordinator.data.liquid_state_display,
        "address": coordinator.mug.device.address,
    }
    if coordinator.mug.debug is True:
        services: dict[str, Any] | None = None
        try:
            services = await coordinator.mug.discover_services()
        except BleakError as e:
            logger.error("Failed to log services, %s", e)
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
