"""Coordinator for all the sensors."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any, cast

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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
            update_interval=timedelta(seconds=60),
        )
        self.ble_device = ble_device
        self.mug = mug
        self.connection = self.mug.connection()
        self.data: dict[str, Any] = {}
        self.available = True

        _LOGGER.info(f"Ember Mug {self.name} Setup")
        # Default Data
        self.data = {
            "mug_id": None,
            "serial_number": None,
            "sw_version": None,
            "mug_name": "Ember Mug",
            "model": "Ember Mug",
        }

    def _notification_callback(self) -> None:
        """Add a sync callback to execute async update in hass."""
        _LOGGER.debug("Notification Callback")
        self.hass.async_create_task(self._process_queued())

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
            changed = await self.connection.update_all()
            self.available = True
        except Exception as e:
            _LOGGER.error(e)
            raise UpdateFailed(f"An error occurred updating mug: {e=}")
        _LOGGER.debug(f"Changed: {changed}")
        _LOGGER.debug("Update done")
        return {
            "serial_number": getattr(self.mug.meta, "serial_number", ""),
            "hw_version": getattr(self.mug.firmware, "hardware", ""),
            "sw_version": getattr(self.mug.firmware, "version", ""),
            "mug_name": self.mug.name,
            "model": self.mug.model,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the mug."""
        unique_id = cast(str, self.config_entry.unique_id)
        return DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=self.data["mug_name"],
            model=self.data["model"],
            suggested_area="Kitchen",
            hw_version=str(self.data.get("hw_version")),
            sw_version=str(self.data.get("sw_version")),
            manufacturer="Ember",
        )
