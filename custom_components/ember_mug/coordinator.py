"""Coordinator for all the sensors."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from bleak_retry_connector import close_stale_connections
from ember_mug import EmberMug
from ember_mug.data import MugData
from home_assistant_bluetooth import BluetoothServiceInfoBleak
from homeassistant.components.bluetooth import BluetoothChange
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import MANUFACTURER

_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(DataUpdateCoordinator[MugData]):
    """Class to manage fetching Mug data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        mug: EmberMug,
        base_unique_id: str,
        device_name: str,
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
        self.mug = mug
        self.data = self.mug.data
        self.available = False
        self._initial_update = True
        self.last_updated: datetime | None = None
        self._last_refresh_was_full = False
        _LOGGER.info(f"Ember Mug {self.name} Setup")

    async def _async_update_data(self) -> MugData:
        """Poll the device."""
        _LOGGER.debug("Updating")
        full_update = not self._last_refresh_was_full
        try:
            changed = []
            if self._initial_update is True:
                changed = await self.mug.update_initial()
                self._initial_update = False
            if self._last_refresh_was_full is False:
                # Only fully poll all data every other call to limit time
                changed += await self.mug.update_all()
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
    def handle_unavailable(
        self,
        service_info: BluetoothServiceInfoBleak,
    ) -> None:
        """Handle the device going unavailable."""
        _LOGGER.warning("Mug is unavailable")
        self.available = False
        self.async_update_listeners()

    @callback
    def handle_bluetooth_event(
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
        # self.hass.loop.create_task(self.async_request_refresh())
        self.hass.loop.create_task(close_stale_connections(service_info.device))

    @callback
    def _async_handle_callback(self, mug_data: MugData) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug("Callback called in Home Assistant")
        self.async_set_updated_data(mug_data)

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
            connections={(CONNECTION_BLUETOOTH, self.mug.device.address)},
            name=name if (name := self.data.name) != "EMBER" else self.device_name,
            model=self.data.model,
            suggested_area="Kitchen",
            hw_version=str(firmware.hardware) if firmware else None,
            sw_version=str(firmware.version) if firmware else None,
            manufacturer=MANUFACTURER,
        )
