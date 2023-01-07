"""Coordinator for all the sensors."""
from __future__ import annotations

import asyncio
import contextlib
from datetime import datetime
import logging
from typing import TYPE_CHECKING

import async_timeout
from ember_mug import EmberMug
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from homeassistant.components.bluetooth import BluetoothChange, BluetoothScanningMode
from homeassistant.components.bluetooth.active_update_coordinator import (
    ActiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import MANUFACTURER

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice


STARTUP_TIMEOUT = 30

_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(ActiveBluetoothDataUpdateCoordinator[EmberMug]):
    """Class to manage fetching Mug data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        ble_device: BLEDevice,
        base_unique_id: str,
        device_name: str,
        mug: EmberMug,
    ) -> None:
        """Initialize global Mug data updater."""
        super().__init__(
            hass=hass,
            logger=logger,
            address=ble_device.address,
            needs_poll_method=self._needs_poll,
            poll_method=self._async_update,
            mode=BluetoothScanningMode.ACTIVE,
        )
        self.ble_device = ble_device
        self.device_name = device_name
        self.base_unique_id = base_unique_id
        self.mug = mug
        self.data = mug
        self.connection = self.mug.connection()
        self._available = False
        self._was_unavailable = True
        self._ready_event = asyncio.Event()
        self.last_updated: datetime | None = None
        self._last_refresh_was_full = False
        _LOGGER.info(f"Ember Mug {self.name} Setup")

    @callback
    def _needs_poll(
        self,
        service_info: BluetoothServiceInfoBleak,
        seconds_since_last_poll: float | None,
    ) -> bool:
        return self._was_unavailable or seconds_since_last_poll >= 30

    async def async_wait_ready(self) -> bool:
        """Wait for the device to be ready."""
        with contextlib.suppress(asyncio.TimeoutError):
            async with async_timeout.timeout(STARTUP_TIMEOUT):
                await self._ready_event.wait()
                return True
        return False

    async def _async_update(self, service_info: BluetoothServiceInfoBleak) -> EmberMug:
        """Poll the device."""
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
            self._available = True
            self.last_updated = datetime.now()
        except Exception as e:
            _LOGGER.error(e)
            self._available = False
            return self.mug
            # raise UpdateFailed(f"An error occurred updating mug: {e=}")
        _LOGGER.debug(f"Changed: {changed}")
        _LOGGER.debug("Update done")
        return self.mug

    async def _process_queued(self) -> None:
        """Process queued changes."""
        try:
            await self.connection.ensure_connection()
            changed = await self.connection.update_queued_attributes()
            self._available = True
        except Exception as e:
            _LOGGER.error(e)
            raise UpdateFailed(f"An error occurred updating mug: {e=}")

        if changed:
            _LOGGER.debug(f"Changed: {changed}")
            self.async_update_listeners()

    @callback
    def _async_handle_unavailable(
        self,
        service_info: BluetoothServiceInfoBleak,
    ) -> None:
        """Handle the device going unavailable."""
        super()._async_handle_unavailable(service_info)
        self._was_unavailable = True

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug(f"Bluetooth event: {service_info} - {change}")
        self._ready_event.set()
        self.ble_device = service_info.device
        self.connection.set_device(self.ble_device)
        super()._async_handle_bluetooth_event(service_info, change)

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the mug."""
        firmware = self.mug.firmware
        return DeviceInfo(
            # identifiers={(DOMAIN, cast(str, self._entry_id))},
            connections={(CONNECTION_BLUETOOTH, self.ble_device.address)},
            name=name if (name := self.data.name) != "EMBER" else self.device_name,
            model=self.data.model,
            suggested_area="Kitchen",
            hw_version=str(firmware.hardware) if firmware else None,
            sw_version=str(firmware.version) if firmware else None,
            manufacturer=MANUFACTURER,
        )
