"""Ember Mug Custom Integration."""
import logging

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator
from .mug import EmberMug

PLATFORMS = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mug Platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    ble_device = async_ble_device_from_address(hass, entry.data[CONF_ADDRESS].upper())
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Ember Mug with address {entry.data[CONF_ADDRESS]}",
        )
    ember_mug = EmberMug(
        ble_device,
        entry.data[CONF_TEMPERATURE_UNIT] == TEMP_CELSIUS,
        lambda: None,
    )
    mug_coordinator = hass.data[DOMAIN][entry.entry_id] = MugDataUpdateCoordinator(
        hass,
        _LOGGER,
        ble_device,
        ember_mug,
        entry.unique_id,
        entry.data.get(CONF_NAME, entry.title),
    )
    entry.async_on_unload(mug_coordinator.async_start())
    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        mug_coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await mug_coordinator.mug.disconnect()
    return unload_ok
