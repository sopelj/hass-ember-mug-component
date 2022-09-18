"""Coordinator for all the sensors."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any, cast

from homeassistant.core import HomeAssistant
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
            update_interval=timedelta(seconds=60),
        )
        self.ble_device = ble_device
        self.mug = mug
        self.connection = self.mug.connection()
        self.data: dict[str, Any] = {}

        _LOGGER.info(f"Ember Mug {self.name} Setup")
        # Default Data
        self.data = {
            "mug_id": None,
            "serial_number": None,
            "last_read_time": None,
            "sw_version": None,
            "mug_name": "Ember Mug",
            "model": "Ember Mug",
        }

    def _sync_callback(self) -> None:
        """Add a sync callback to execute async update in hass."""
        _LOGGER.debug("Sync Callback")
        self.hass.async_create_task(self.async_refresh())

    async def _async_update_data(self) -> dict[str, Any]:
        """Update the data of the coordinator."""
        _LOGGER.debug("Updating")
        try:
            if not self.connection.client or not self.connection.client.is_connected:
                await self.connection.connect()
                await self.connection.subscribe(callback=self._sync_callback)
            await self.connection.update_all()
        except Exception as e:
            _LOGGER.error(e)
            raise UpdateFailed(f"An error occurred updating mug: {e=}")

        _LOGGER.debug("Update done")
        return {
            "serial_number": self.mug.meta.serial_number,
            "last_read_time": dt_util.utcnow(),
            "sw_version": str(self.mug.firmware.version) if self.mug.firmware else None,
            "mug_name": self.mug.name,
            "model": self.mug.model,
        }

    @property
    def is_connected(self) -> bool:
        """Check if mug is connected via Bluetooth."""
        return (
            self.connection.client is not None
            and self.connection.client.is_connected is True
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the mug."""
        unique_id = cast(str, self.config_entry.unique_id)
        return DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=self.data["mug_name"],
            model=self.data["model"],
            sw_version=self.data["sw_version"],
            manufacturer="Ember",
        )
