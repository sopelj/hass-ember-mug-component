"""Ember Mug Custom Integration."""
from asyncio import Event
import logging

import async_timeout
from ember_mug import EmberMug
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_TEMPERATURE_UNIT,
    EVENT_HOMEASSISTANT_STOP,
    TEMP_CELSIUS,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mug Platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    ble_device = bluetooth.async_ble_device_from_address(
        hass,
        entry.data[CONF_ADDRESS].upper(),
        True,
    )
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Ember Mug with address {entry.data[CONF_ADDRESS]}",
        )

    ember_mug = EmberMug(
        ble_device,
        entry.data[CONF_TEMPERATURE_UNIT] == TEMP_CELSIUS,
    )
    hass.data[DOMAIN][entry.entry_id] = mug_coordinator = MugDataUpdateCoordinator(
        hass,
        _LOGGER,
        ble_device,
        ember_mug,
        entry.entry_id,
    )

    @callback
    def _async_update_ble(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        """Update from a ble callback."""
        mug_coordinator.connection.set_device(service_info.device)

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_update_ble,
            BluetoothCallbackMatcher({ADDRESS: entry.data[CONF_ADDRESS]}),
            bluetooth.BluetoothScanningMode.ACTIVE,
        ),
    )
    startup_event = Event()
    cancel_first_update = mug_coordinator.connection.register_callback(
        lambda *_: startup_event.set(),
    )

    try:
        await mug_coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        cancel_first_update()
        raise

    try:
        async with async_timeout.timeout(60):
            await startup_event.wait()
    except TimeoutError as ex:
        raise ConfigEntryNotReady(
            "Unable to communicate with the device; "
            f"Try moving the Bluetooth adapter closer to {ember_mug.name}",
        ) from ex
    finally:
        cancel_first_update()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_stop(event: Event) -> None:
        """Close the connection."""
        await mug_coordinator.connection.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop),
    )
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        mug_coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await mug_coordinator.connection.disconnect()
    return unload_ok
