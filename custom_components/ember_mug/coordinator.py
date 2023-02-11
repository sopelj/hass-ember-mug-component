"""Coordinator for all the sensors."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Any

from ember_mug import EmberMug
from ember_mug.data import MugData
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
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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
        include_extra: bool = False,
    ) -> None:
        """Initialize global Mug data updater."""
        super().__init__(
            hass=hass,
            logger=logger,
            name=f"ember-mug-{base_unique_id}",
            update_interval=timedelta(seconds=15),
        )
        self.device_name = device_name
        self.base_unique_id = base_unique_id
        self.mug = EmberMug(ble_device, include_extra=include_extra)
        self.data = self.mug.data
        self.available = False
        self.last_updated: datetime | None = None
        self._updating = asyncio.Lock()
        self._last_refresh_was_full = False
        self._cancel_track_unavailable: CALLBACK_TYPE | None = None
        self._cancel_bluetooth_advertisements: CALLBACK_TYPE | None = None
        _LOGGER.info(f"Ember Mug {self.name} Setup")

    async def _async_update_data(self) -> MugData:
        """Poll the device."""
        _LOGGER.debug("Updating")
        full_update = not self._last_refresh_was_full
        try:
            changed = []
            if self._last_refresh_was_full is False:
                # Only fully poll all data every other call to limit time
                changed = await self.mug.update_initial()
                changed = await self.mug.update_all()
            else:
                changed += await self.mug.update_queued_attributes()
            self._last_refresh_was_full = not self._last_refresh_was_full
            self.available = True
            self.last_updated = datetime.now()
        except Exception as e:
            _LOGGER.error("An error occurred whilst updating the mug: %s", e)
            self.available = False
            raise UpdateFailed(f"An error occurred updating mug: {e=}")

        # Ensure callbacks are registered
        self._cancel_callback = self.mug.register_callback(
            self._async_handle_callback,
        )

        _LOGGER.debug(
            "[%s Update] Changed: %s",
            "Full" if full_update else "Partial",
            changed,
        )
        return self.mug.data

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
        address = self.mug.device.address
        self._cancel_callback = self.mug.register_callback(
            self._async_handle_callback,
        )
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
        if self._cancel_callback is not None:
            self._cancel_callback()
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
        _LOGGER.warning("Mug is unavailable")
        self.available = False
        self.async_update_listeners()

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug(
            "Bluetooth event. Service Info: %s, change: %s",
            service_info,
            change,
        )
        self.mug.set_device(service_info.device)
        self.hass.loop.create_task(self.async_request_refresh())

    @callback
    def _async_handle_callback(self, mug: EmberMug) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug("Callback called in Home Assistant")
        self.async_set_updated_data(mug)

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
            connections={(CONNECTION_BLUETOOTH, self.data.device.address)},
            name=name if (name := self.data.name) != "EMBER" else self.device_name,
            model=self.data.model,
            suggested_area="Kitchen",
            hw_version=str(firmware.hardware) if firmware else None,
            sw_version=str(firmware.version) if firmware else None,
            manufacturer=MANUFACTURER,
        )
