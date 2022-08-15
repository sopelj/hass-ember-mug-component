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
from .mug import EmberMug

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice


_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage Mug update data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        ble_device: BLEDevice,
        mug: EmberMug,
        base_unique_id: str,
        device_name: str,
    ) -> None:
        """Initialize Mug updater coordinator."""
        super().__init__(
            hass,
            logger,
            name=f"ember-mug-{base_unique_id}",
            update_interval=timedelta(seconds=60),
        )
        self.ble_device = ble_device
        self.mug = mug
        self.mug.update_callback = self._sync_callback
        self.data: dict[str, Any] = {}
        self.device_name = device_name
        self.base_unique_id = base_unique_id

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
            await self.mug.update_all()
        except Exception as e:
            _LOGGER.error(e)
            raise UpdateFailed(f"An error occurred updating mug: {e=}")
        _LOGGER.debug("Update done")
        return {
            "mug_id": self.mug.mug_id,
            "serial_number": self.mug.serial_number,
            "last_read_time": dt_util.utcnow(),
            "sw_version": str(self.mug.firmware_info.get("version", "")),
            "mug_name": self.mug.mug_name,
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
            sw_version=self.data["sw_version"],
            manufacturer="Ember",
        )
