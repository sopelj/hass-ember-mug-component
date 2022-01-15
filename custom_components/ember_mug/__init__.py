"""Ember Mug Custom Integration."""
import asyncio
import logging
from typing import cast

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_MAC,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .mug import EmberMug

PLATFORMS = [Platform.SENSOR]
_LOGGER = logging.getLogger(__name__)


class MugDataUpdateCoordinator(DataUpdateCoordinator):
    """Shared Data Coordinator for polling mug updates."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Init data coordinator and start mug running."""
        super().__init__(
            hass, _LOGGER, name=f"ember-mug-{config.entry_id}", update_interval=None
        )
        self.mac_address = config.data[CONF_MAC]
        self.name = config.data.get(CONF_NAME, f"Ember Mug {self.mac_address}")
        self.unit_of_measurement = config.data.get(CONF_TEMPERATURE_UNIT, TEMP_CELSIUS)

        self.mug = EmberMug(
            self.mac_address, self.unit_of_measurement != TEMP_FAHRENHEIT
        )
        _LOGGER.info(f"Ember Mug {self.name} Setup")
        # Start loop
        _LOGGER.info(f"Start running {self.name}")
        self.hass.async_create_task(self._run())
        # Default Data
        self.data = {
            "serial_number": None,
            "mug_id": None,
            "last_read_time": None,
            "firmware_info": None,
            "model": "Ember Mug",
            "mug_name": self.name,
        }

    async def _run(self):
        """Start the task loop."""
        try:
            self._loop = True
            _LOGGER.info(f"Starting mug loop {self.mac_address}")
            while self._loop:
                await self.mug.ensure_connected()
                await self.mug.update_all()
                self.mug.updates_queued.clear()
                await self.async_refresh()

                # Maintain connection for 5min seconds until next update
                # We will be notified of most changes during this time
                for _ in range(150):
                    await self.mug.ensure_connected()
                    await self.mug.update_queued_attributes()
                    await asyncio.sleep(2)

        except Exception as e:
            _LOGGER.error(f"An unexpected error occurred during loop {e}. Restarting.")
            if self.mug.is_connected:
                await self.mug.disconnect()
            self.hass.async_create_task(self._run())

    async def _async_update_data(self):
        """Update the data of the coordinator."""
        data = {
            "mug_id": self.mug.mug_id,
            "serial_number": self.mug.serial_number,
            "last_read_time": dt_util.utcnow(),
            "firmware_info": self.mug.firmware_info,
            "mug_name": self.name,
            "model": self.mug.model,
        }
        _LOGGER.debug(f"{data}")
        return data

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the mug."""
        unique_id = cast(str, self.config_entry.unique_id)
        return DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=self.data["mug_name"],
            model=self.data["model"],
            sw_version=self.data["firmware_info"],
            manufacturer="Ember",
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mug Platform."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    coordinator = MugDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator}
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Anycubic component."""
    if DOMAIN not in config:
        return True

    for conf in config[DOMAIN]:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
            )
        )
    return True
