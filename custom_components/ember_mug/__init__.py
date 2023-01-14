"""Ember Mug Custom Integration."""
from __future__ import annotations

from asyncio import Event
import logging

import async_timeout
from bleak import BleakError
from ember_mug import EmberMug
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.TEXT,
]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mug Platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    address: str = entry.data[CONF_ADDRESS].upper()
    ble_device = bluetooth.async_ble_device_from_address(hass, address)
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Ember Mug with address {entry.data[CONF_ADDRESS]}",
        )

    ember_mug = EmberMug(ble_device)
    hass.data[DOMAIN][entry.entry_id] = mug_coordinator = MugDataUpdateCoordinator(
        hass,
        _LOGGER,
        ble_device,
        entry.unique_id,
        entry.data.get(CONF_NAME, entry.title),
        ember_mug,
    )

    entry.async_on_unload(mug_coordinator.async_start())
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

    await set_temperature_unit(mug_coordinator, entry.data[CONF_TEMPERATURE_UNIT])
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _async_stop(event: Event) -> None:
        """Close the connection."""
        await mug_coordinator.connection.disconnect()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop),
    )

    return True


async def set_temperature_unit(
    mug_coordinator: MugDataUpdateCoordinator,
    unit: UnitOfTemperature,
) -> None:
    """Try to set Mug Unit if different from current one."""
    if mug_coordinator.mug_temp_unit == unit:
        # No need
        return
    try:
        async with async_timeout.timeout(10):
            target_unit = unit.value.strip("°")
            await mug_coordinator.connection.set_temperature_unit(target_unit)
            mug_coordinator.data.temperature_unit = target_unit
    except (BleakError, TimeoutError, EOFError) as e:
        _LOGGER.warning("Unable to set temperature unit to %s: %s.", unit, e)


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        mug_coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await mug_coordinator.connection.disconnect()

        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
