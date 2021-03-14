import voluptuous as vol
import logging
import asyncio
from typing import Any, Callable, Dict, Optional

from bleak import BleakClient
from bleak.exc import BleakError

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_TEMPERATURE_UNIT, TEMP_CELSIUS, TEMP_FAHRENHEIT, CONF_ENTITY_ID
from homeassistant.helpers.entity import CoordinatorEntity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
import homeassistant.helpers.config_validation as cv

from const import (
    TARGET_TEMP_UUID, LED_COLOUR_UUID, CURRENT_TEMP_UUID, BATTERY_UUID, ICON_DEFAULT, ICON_UNAVAILABLE
)

# Schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.matches_regex(r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'),
        vol.Required(CONF_TEMPERATURE_UNIT, default=TEMP_CELSIUS): cv.temperature_unit,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_ENTITY_ID): cv.entity_id,
    }
)

logger = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    async_add_entities([EmberMugSensor(config)], update_before_add=True)


class EmberMugSensor(CoordinatorEntity):
    """
    Config for an Ember Mug
    """

    def __init__(self, config: ConfigType):
        super().__init__()
        self.mac_address = config[CONF_MAC]
        self._unique_id = config.get(CONF_ENTITY_ID, f'ember_mug_{self.mac_address.replace(":", "-")}')
        self._name = config.get(CONF_NAME, f'Ember Mug {self.mac_address}')
        self._unit_of_measurement = config[CONF_TEMPERATURE_UNIT]
        
        self.attrs: Dict[str, Any] = {
            'color': None,
            'current_temp': None,
            'target_temp': None,
            'battery': None,
        }
        self._icon = ICON_DEFAULT
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    async def _temp_from_bytes(self, temp_bytes: bytearray) -> float:
        temp_c = float(int.from_bytes(temp_bytes, byteorder='little', signed=False)) * 0.01
        if self._unit_of_measurement == TEMP_FAHRENHEIT:
            # Convert to fahrenheit
            return (temp_c * 9/5) + 32
        return temp_c

    async def update_battery(self) -> None:
        current_battery = await self.client.read_gatt_char(BATTERY_UUID)
        battery_percent = float(current_battery[0])
        logger.debug(f'Battery is at {battery_percent}')
        self.attrs['battery'] = battery_percent

    async def update_led_colour(self) -> None:
        r, g, b, a = await self.client.read_gatt_char(LED_COLOUR_UUID)
        self.colour = [r, g, b, a]
        self.attrs['color'] = f'#{r:02x}{g:02x}{b:02x}'
 
    async def update_target_temp(self) -> None:
        temp_bytes = await self.client.read_gatt_char(TARGET_TEMP_UUID)
        target_temp = await self._temp_from_bytes(temp_bytes)
        logger.debug(f'Target temp {target_temp}')
        self.attrs['target_temp'] = target_temp

    async def update_current_temp(self) -> None:
        temp_bytes = await self.client.read_gatt_char(CURRENT_TEMP_UUID)
        current_temp = await self._temp_from_bytes(temp_bytes)
        logger.debug(f'Current temp {current_temp}')
        self.attrs['current_temp'] = current_temp

    async def async_update(self) -> None:
        try:
            async with BleakClient(self.mac_address) as client:
                self.client = client
                connected_mac = await client.is_connected()
                logger.info(f"Connected: {connected_mac}")

                await self.update_led_colour()
                await self.update_battery()
                await self.update_target_temp()
                await self.update_current_temp()

                self._state = f'{self.attrs["current_temp"]}°{self._unit_of_measurement}'
                self._available = True

        except BleakError as e:
            logger.warning(f'Error connecting to {self.mac_address}: {e}')
            self._available = False
            self._state = None
        except Exception as e:
            logger.error(f'Unexpected Error connecting to {self.mac_address}: {e}')
            self._available = False
            self._state = None
