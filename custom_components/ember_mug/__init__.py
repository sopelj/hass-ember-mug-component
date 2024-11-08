"""Ember Mug Custom Integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ember_mug import EmberMug
from ember_mug.consts import EMBER_BLE_SIG
from ember_mug.utils import get_model_info_from_advertiser_data
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothCallbackMatcher,
    BluetoothScanningMode,
)
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_MAC,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_DEBUG, CONFIG_VERSION, DOMAIN
from .coordinator import MugDataUpdateCoordinator

if TYPE_CHECKING:
    from home_assistant_bluetooth import BluetoothServiceInfoBleak
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, HomeAssistant


type EmberMugConfigEntry = ConfigEntry[MugDataUpdateCoordinator]


PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mug Platform."""
    address: str = entry.data[CONF_ADDRESS].upper()
    service_info = bluetooth.async_last_service_info(hass, address, connectable=True)

    if service_info and not service_info.manufacturer_data:
        _LOGGER.debug("Manufacturer data missing from latest advertisement, looking again.")
        try:
            service_info = await bluetooth.async_process_advertisements(
                hass,
                _process_more_advertisements,
                {"address": address, "connectable": True},
                BluetoothScanningMode.ACTIVE,
                30,
            )
        except TimeoutError as e:
            raise ConfigEntryNotReady(
                f"Could not find device with manufacturer data and address {address}. "
                "If you have issues connecting, try putting the device in pairing mode.",
            ) from e

    if not service_info:
        raise ConfigEntryNotReady(
            f"Could not find Ember device with address {entry.data[CONF_ADDRESS]}",
        )

    _LOGGER.debug(
        "Integration setup. Last service info: Device: %s, Manufacturer Data: %s",
        service_info.device,
        service_info.manufacturer_data,
    )

    ember_mug = EmberMug(
        service_info.device,
        model_info=get_model_info_from_advertiser_data(service_info.advertisement),
        debug=entry.options.get(CONF_DEBUG, False),
    )
    mug_coordinator = MugDataUpdateCoordinator(
        hass,
        _LOGGER,
        ember_mug,
        entry.unique_id,
        entry.data.get(CONF_NAME, entry.title),
    )
    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            mug_coordinator.handle_bluetooth_event,
            BluetoothCallbackMatcher(
                address=address,
                connectable=True,
                manufacturer_id=EMBER_BLE_SIG,
            ),
            BluetoothScanningMode.ACTIVE,
        ),
    )

    await mug_coordinator.async_config_entry_first_refresh()

    entry.async_on_unload(
        bluetooth.async_track_unavailable(
            hass,
            mug_coordinator.handle_unavailable,
            address,
        ),
    )

    entry.runtime_data = mug_coordinator
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_stop(event: Event) -> None:
        """Close the connection."""
        await mug_coordinator.mug.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop),
    )

    return True


def _process_more_advertisements(
    service_info: BluetoothServiceInfoBleak,
) -> bool:
    """Wait for an advertisement with Ember SIG in the manufacturer_data."""
    return EMBER_BLE_SIG in service_info.manufacturer_data


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version >= CONFIG_VERSION:
        # No migrations to run
        return False

    old_data = {**config_entry.data}
    if config_entry.version == 1:
        old_data[CONF_ADDRESS] = old_data[CONF_MAC]

    hass.config_entries.async_update_entry(
        config_entry,
        data={
            CONF_ADDRESS: old_data[CONF_ADDRESS],
            CONF_NAME: old_data[CONF_NAME],
        },
        options={
            CONF_DEBUG: old_data.get(CONF_DEBUG, False),
        },
        version=3,
    )
    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: EmberMugConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        mug_coordinator = entry.runtime_data
        await mug_coordinator.mug.disconnect()
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
