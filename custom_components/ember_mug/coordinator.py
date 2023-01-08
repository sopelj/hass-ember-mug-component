"""Coordinator for all the sensors."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Any

from ember_mug import EmberMug
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothChange,
    BluetoothScanningMode,
    async_register_callback,
    async_track_unavailable,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import MANUFACTURER

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice


_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(DataUpdateCoordinator[EmberMug]):
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
            name=f"ember-mug-{base_unique_id}",
            update_interval=timedelta(seconds=15),
        )
        self.ble_device = ble_device
        self.device_name = device_name
        self.base_unique_id = base_unique_id
        self.data = mug
        self.connection = self.data.connection()
        self.available = False
        self.last_updated: datetime | None = None
        self._updating = asyncio.Lock()
        self._last_refresh_was_full = False
        self._cancel_track_unavailable: CALLBACK_TYPE | None = None
        self._cancel_bluetooth_advertisements: CALLBACK_TYPE | None = None
        _LOGGER.info(f"Ember Mug {self.name} Setup")

    async def _async_update_data(self) -> EmberMug:
        """Poll the device."""
        _LOGGER.debug("Updating")
        try:
            # async with self._updating.acquire():
            await self.connection.ensure_connection()
            changed = []
            if self._last_refresh_was_full is False:
                # Only fully poll all data every other call to limit time
                _LOGGER.debug("Full Update")
                changed = await self.connection.update_all()
            else:
                _LOGGER.debug("Updating queued attributes")
                changed += await self.connection.update_queued_attributes()
            self._last_refresh_was_full = not self._last_refresh_was_full
            self.available = True
            self.last_updated = datetime.now()
        except Exception as e:
            _LOGGER.error(e)
            self.available = False
            return self.data
            # raise UpdateFailed(f"An error occurred updating mug: {e=}")
        _LOGGER.debug(f"Changed: {changed}")
        _LOGGER.debug("Update done")
        return self.data

    @callback
    def async_start(self) -> CALLBACK_TYPE:
        """Start the data updater."""
        self._async_start()

        @callback
        def _async_cancel() -> None:
            self._async_stop()

        return _async_cancel

    @callback
    def _async_start(self) -> None:
        """Start the Bluetooth callbacks."""
        address = self.connection.mug.device.address
        self._cancel_bluetooth_advertisements = async_register_callback(
            self.hass,
            self._async_handle_bluetooth_event,
            BluetoothCallbackMatcher(address=address),
            BluetoothScanningMode.ACTIVE,
        )
        self._cancel_track_unavailable = async_track_unavailable(
            self.hass,
            self._async_handle_unavailable,
            address,
        )

    @callback
    def _async_stop(self) -> None:
        """Stop the Bluetooth callbacks."""
        if self._cancel_bluetooth_advertisements is not None:
            self._cancel_bluetooth_advertisements()
            self._cancel_bluetooth_advertisements = None
        if self._cancel_track_unavailable is not None:
            self._cancel_track_unavailable()
            self._cancel_track_unavailable = None

    @callback
    def _async_handle_unavailable(
        self,
        service_info: BluetoothServiceInfoBleak,
    ) -> None:
        """Handle the device going unavailable."""
        self.available = False

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug(f"Bluetooth event: {service_info} - {change}")
        self.connection.set_device(self.ble_device)
        self.async_request_refresh()

    def get_mug_attr(self, mug_attr: str) -> Any:
        """Get a mug attribute by name (recursively) or return None."""
        value = self.data
        for attr in mug_attr.split("."):
            try:
                value = getattr(value, attr)
            except AttributeError:
                return None
        return value

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the mug."""
        firmware = self.data.firmware
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
