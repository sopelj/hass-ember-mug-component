from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.bluetooth import BluetoothScanningMode, BluetoothServiceInfoBleak, BluetoothChange
from homeassistant.components.bluetooth.passive_update_coordinator import (
    PassiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant, callback

from .mug import EmberMug

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice


_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(PassiveBluetoothDataUpdateCoordinator):
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
            hass, logger, ble_device.address, BluetoothScanningMode.ACTIVE
        )
        self.ble_device = ble_device
        self.mug = mug
        self.data: dict[str, Any] = {}
        self.device_name = device_name
        self.base_unique_id = base_unique_id

    @callback
    def _async_handle_bluetooth_event(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        """Handle Bluetooth events."""
        super()._async_handle_bluetooth_event(service_info, change)
        _LOGGER.debug(
            "%s: Ember Mug: \n%s\n%s\n%s ", self.ble_device.address, service_info.device, service_info.advertisement, change
        )
        self.async_update_listeners()

