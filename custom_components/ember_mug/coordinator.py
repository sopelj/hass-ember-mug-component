"""Coordinator for all the sensors."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from bleak import BleakError
from bleak_retry_connector import close_stale_connections
from ember_mug.data import Change, MugData
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import MANUFACTURER, SUGGESTED_AREA

if TYPE_CHECKING:
    from ember_mug import EmberMug
    from home_assistant_bluetooth import BluetoothServiceInfoBleak
    from homeassistant.components.bluetooth import BluetoothChange


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
        device_type = mug.data.model_info.device_type.value
        super().__init__(
            hass=hass,
            logger=logger,
            name=f"ember-{device_type.replace('_', '-')}-{base_unique_id}",
            update_interval=timedelta(seconds=15),
        )
        self.device_name = device_name
        self.device_type = device_type
        self.base_unique_id = base_unique_id
        self.mug = mug
        self.data = self.mug.data
        self.available = False
        self._initial_update = True
        self._last_refresh_was_full = False
        self._cancel_callback = self.mug.register_callback(
            self._async_handle_callback,
        )
        _LOGGER.info("%s %s Setup", self.mug.model_name, self.name)

    async def _async_update_data(self) -> MugData:
        """Poll the device."""
        _LOGGER.debug("Updating")
        full_update = not self._last_refresh_was_full
        changed: list[Change] | None = []
        try:
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
        except (asyncio.TimeoutError, BleakError) as e:
            if isinstance(e, BleakError):
                _LOGGER.debug("An error occurred trying to update the mug: %s", e)
            if self.available is True:
                _LOGGER.debug("%s is not available: %s", e)
                self.available = False
            if self._initial_update is True:
                raise UpdateFailed(
                    f"An error occurred updating {self.mug.model_name}: {e=}",
                ) from e
            changed = None
        except Exception as e:
            _LOGGER.error(
                "An unexpected error occurred whilst updating the %s: %s",
                self.mug.model_name,
                e,
            )
            self.available = False
            raise UpdateFailed(
                f"An error occurred updating {self.mug.model_name}: {e=}",
            ) from e

        _LOGGER.debug(
            "[%s Update] Changed: %s",
            "Full" if full_update else "Partial",
            changed,
        )
        return self.mug.data

    def ensure_writable(self) -> None:
        """Writable check for service methods."""
        if self.mug.can_write is False:
            raise ValueError(
                f"Unable to write to {self.mug.data.model_info.device_type.value}",
            )

    @callback
    def handle_unavailable(
        self,
        service_info: BluetoothServiceInfoBleak,
    ) -> None:
        """Handle the device going unavailable."""
        _LOGGER.debug("%s is unavailable", self.mug.model_name)
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
        self.mug.ble_event_callback(service_info.device, service_info.advertisement)
        # Register or update callback
        self._cancel_callback = self.mug.register_callback(
            self._async_handle_callback,
        )
        self.hass.loop.create_task(close_stale_connections(service_info.device))

    @callback
    def _async_handle_callback(self, mug_data: MugData) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug("Callback called in Home Assistant")
        self.async_set_updated_data(mug_data)

    def get_device_attr(self, device_attr: str) -> Any:
        """Get a device attribute by name (recursively) or return None."""
        value = self.data
        for attr in device_attr.split("."):
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
            name=name if (name := self.data.name) and name != "Ember Device" else self.device_name,
            model=self.data.model_info.name,
            serial_number=self.data.meta.serial_number if self.data.meta else None,
            suggested_area=SUGGESTED_AREA,
            hw_version=str(firmware.hardware) if firmware else None,
            sw_version=str(firmware.version) if firmware else None,
            manufacturer=MANUFACTURER,
        )
