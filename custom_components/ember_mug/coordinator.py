"""Coordinator for all the sensors."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any, cast

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import DOMAIN

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice
    from ember_mug import EmberMug


_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage Mug update data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        ble_device: BLEDevice,
        mug: EmberMug,
        entry_id: str,
    ) -> None:
        """Initialize Mug updater coordinator."""
        super().__init__(
            hass,
            logger,
            name=f"ember-mug-{entry_id}",
            update_interval=timedelta(seconds=30),
        )
        self.ble_device = ble_device
        self.mug = mug
        self._entry_id = entry_id
        self.connection = self.mug.connection()
        self.data: dict[str, Any] = {}
        self.available = True
        self._last_refresh_was_full = False

        _LOGGER.info(f"Ember Mug {self.name} Setup")
        # Default Data
        self.data = {
            "mug_id": None,
            "serial_number": None,
            "sw_version": None,
            "mug_name": "Ember Mug",
            "model": "Ember Mug",
            "last_updated": None,
        }

    async def _process_queued(self) -> None:
        """Process queued changes."""
        try:
            await self.connection.ensure_connection()
            changed = await self.connection.update_queued_attributes()
            self.available = True
        except Exception as e:
            _LOGGER.error(e)
            raise UpdateFailed(f"An error occurred updating mug: {e=}")

        if changed:
            _LOGGER.debug(f"Changed: {changed}")
            self.async_update_listeners()

    async def _async_update_data(self) -> dict[str, Any]:
        """Update the data of the coordinator."""
        _LOGGER.debug("Updating")
        try:
            await self.connection.ensure_connection()
            changed = []
            if self._last_refresh_was_full is False:
                # Only fully poll all data every other call to limit time
                _LOGGER.debug("Full Update")
                changed = await self.connection.update_all()
            _LOGGER.debug("Updating queued attributes")
            changed += await self.connection.update_queued_attributes()
            self._last_refresh_was_full = not self._last_refresh_was_full
            self.available = True
        except Exception as e:
            _LOGGER.error(e)
            self.available = False
            raise UpdateFailed(f"An error occurred updating mug: {e=}")
        _LOGGER.debug(f"Changed: {changed}")
        _LOGGER.debug("Update done")
        return {
            "serial_number": getattr(self.mug.meta, "serial_number", ""),
            "hw_version": getattr(self.mug.firmware, "hardware", ""),
            "sw_version": getattr(self.mug.firmware, "version", ""),
            "mug_name": self.mug.name,
            "model": self.mug.model,
            "last_updated": dt_util.utcnow(),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the mug."""
        return DeviceInfo(
            identifiers={(DOMAIN, cast(str, self._entry_id))},
            connections={(CONNECTION_BLUETOOTH, self.ble_device.address)},
            name=self.data["mug_name"],
            model=self.data["model"],
            suggested_area="Kitchen",
            hw_version=str(self.data.get("hw_version")),
            sw_version=str(self.data.get("sw_version")),
            manufacturer="Ember",
        )
