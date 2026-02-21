"""Coordinator for all the sensors."""

from __future__ import annotations

import logging
import traceback
from datetime import timedelta
from typing import TYPE_CHECKING, Any, TypedDict

from bleak import BleakError
from bleak_retry_connector import close_stale_connections
from ember_mug.data import Change, MugData
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, MANUFACTURER, STORAGE_VERSION, SUGGESTED_AREA

if TYPE_CHECKING:
    from ember_mug import EmberMug
    from home_assistant_bluetooth import BluetoothServiceInfoBleak
    from homeassistant.components.bluetooth import BluetoothChange


_LOGGER = logging.getLogger(__name__)


class PersistentData(TypedDict):
    """Data that should persist on disk."""

    target_temp_bkp: float | None


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
            always_update=False,
        )
        self._store: Store[PersistentData] = Store(hass, STORAGE_VERSION, DOMAIN)
        self.persistent_data: PersistentData = None  # type: ignore[assignment]
        self.device_name = device_name
        self.device_type = device_type
        self.base_unique_id = base_unique_id
        self.mug = mug
        self.data = self.mug.data
        self.available = False
        self._last_refresh_was_full = True
        _LOGGER.info("%s %s Setup", self.mug.model_name, self.name)

    async def _async_setup(self) -> None:
        """Initialize coordinator and fetch initial data."""
        # Setup storage
        self.persistent_data = await self._store.async_load()
        try:
            await self.mug.pair()
            await self.mug.update_initial()
            await self.mug.update_all()
            if not self.persistent_data:
                await self.write_to_storage(self.mug.data.target_temp)
            _LOGGER.debug("[Initial Update] values: %s", self.mug.data)
        except (TimeoutError, BleakError) as e:
            if isinstance(e, BleakError):
                _LOGGER.debug("An error occurred trying to update the %s: %s", self.mug.model_name, e)
            raise UpdateFailed(
                f"An error occurred updating {self.mug.model_name}: {e=}",
            ) from e

        try:
            is_writable = await self.mug.make_writable()
            _LOGGER.debug("Mug writability: %s", is_writable)
        except (TimeoutError, BleakError) as e:
            if isinstance(e, BleakError):
                _LOGGER.debug("An error occurred trying to make the %s writable: %s", self.mug.model_name, e)

        self.mug.register_callback(self._async_handle_callback)
        self.async_update_listeners()

    async def _async_update_data(self) -> MugData:
        """Poll the device."""
        _LOGGER.debug("Updating")
        full_update = not self._last_refresh_was_full
        changed: list[Change] | None = []
        try:
            if not self._last_refresh_was_full:
                # Only fully poll all data every other call to limit time
                changed += await self.mug.update_all()
            else:
                changed += await self.mug.update_queued_attributes()
            self._last_refresh_was_full = not self._last_refresh_was_full
            self.available = True
        except (TimeoutError, BleakError) as e:
            if isinstance(e, BleakError):
                _LOGGER.debug("An error occurred trying to update the %s: %s", self.mug.model_name, e)
            if self.available:
                _LOGGER.debug("%s is not available: %s", self.mug.model_name, e)
                self.available = False
            changed = None
        except Exception as e:
            _LOGGER.error(
                "An unexpected error occurred whilst updating the %s: %s",
                self.mug.model_name,
                e,
            )
            self.available = False
            _LOGGER.debug("Stacktrace: %s", traceback.format_exception(e))
            raise UpdateFailed(f"An error occurred updating {self.mug.model_name}: {e}") from e

        _LOGGER.debug(
            "[%s Update] Changed: %s",
            "Full" if full_update else "Partial",
            changed,
        )
        if changed:
            self.async_update_listeners()
        return self.mug.data

    def ensure_writable(self) -> None:
        """Writable check for service methods."""
        if not self.mug.can_write:
            raise ValueError(
                f"Unable to write to {self.mug.data.model_info.device_type.value}",
            )

    async def write_to_storage(self, target_temp: float | None) -> None:
        """
        Write target temp to file storage.

        This is stored to disk, so it can be restored to the entity even if we restart Home Assistant.
        """
        self.persistent_data: PersistentData = {"target_temp_bkp": target_temp}
        await self._store.async_save(self.persistent_data)

    @property
    def target_temp(self) -> float:
        """Shortcut for getting target temp, but showing stored data if temp control is off."""
        if (
            self.data.target_temp == 0
            and self.persistent_data
            and (bkp_temp := self.persistent_data.get("target_temp_bkp"))
        ):
            return bkp_temp
        return self.data.target_temp

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
        change: BluetoothChange.ADVERTISEMENT,
    ) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug(
            "Bluetooth event. Service Info: %s, change: %s",
            service_info,
            change,
        )
        self.mug.ble_event_callback(service_info.device, service_info.advertisement)
        self.available = True
        self.async_update_listeners()
        self.hass.loop.create_task(close_stale_connections(service_info.device))

    @callback
    def _async_handle_callback(self, mug_data: MugData) -> None:
        """Handle a Bluetooth event."""
        _LOGGER.debug("Callback called in Home Assistant")
        self.async_set_updated_data(mug_data)

    def refresh_from_mug(self) -> None:
        """Update stored data from mug data and trigger entities."""
        self.async_set_updated_data(self.mug.data)

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
            identifiers={(DOMAIN, self.mug.device.address)},
            name=self.device_name,
            model=self.data.model_info.name,
            model_id=self.data.model_info.model.value if self.data.model_info.model else None,
            serial_number=self.data.meta.serial_number if self.data.meta else None,
            suggested_area=SUGGESTED_AREA,
            hw_version=str(firmware.hardware) if firmware else None,
            sw_version=str(firmware.version) if firmware else None,
            manufacturer=MANUFACTURER,
        )
