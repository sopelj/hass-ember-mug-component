"""Ember Mug Custom Integration."""
import logging

from ember_mug import EmberMug
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import MugDataUpdateCoordinator

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
    )
    hass.data[DOMAIN][entry.entry_id] = mug_coordinator = MugDataUpdateCoordinator(
        hass,
        _LOGGER,
        ble_device,
        ember_mug,
        entry.entry_id,
    )
    await mug_coordinator.establish_initial_connection()
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
        await mug_coordinator.connection.disconnect()
    return unload_ok
